"""
pso_drones.py

PSO para coordinar 10 drones en un área de 5x5 km y maximizar la probabilidad
de encontrar sobrevivientes. El objetivo es ubicar un punto por dron (x,y)
de modo que la suma de probabilidades de las celdas cubiertas por al menos
un dron sea máxima.

Ejecución:
    python pso_drones.py

Requisitos:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import time

# ------------------ Parámetros del problema ------------------
AREA_SIZE = 5000.0       # metros (5 km)
GRID_RES = 100           # resolución del grid (GRID_RES x GRID_RES)
N_DRONES = 10
DETECTION_RADIUS = 200.0  # metros

# PSO parameters
N_PARTICLES = 60
N_ITER = 200
W = 0.7     # inertia weight
C1 = 1.5    # cognitive coefficient
C2 = 1.5    # social coefficient
VEL_CLAMP = 500.0  # max velocity per dimension

np.random.seed(42)

# ------------------ Generar mapa de probabilidades (simulado) ------------------
grid_x = np.linspace(0, AREA_SIZE, GRID_RES)
grid_y = np.linspace(0, AREA_SIZE, GRID_RES)
xx, yy = np.meshgrid(grid_x, grid_y)
prob_map = np.zeros_like(xx)

# Definimos "hotspots" (islas de probabilidad) como gaussianas
hotspots = [
    (1200, 4000, 0.8, 700),
    (3800, 4200, 0.6, 600),
    (2500, 2500, 0.9, 500),
    (800, 1200, 0.4, 400),
    (4200, 800, 0.5, 650),
]
for cx, cy, amp, sigma in hotspots:
    prob_map += amp * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))

# Normalizar mapa a [0,1]
prob_map = prob_map / prob_map.max()

# ------------------ Preparar datos para evaluación ------------------
cell_coords = np.stack([xx.ravel(), yy.ravel()], axis=1)  # (n_cells, 2)
cell_probs = prob_map.ravel()  # (n_cells,)

def coverage_score(positions_flat):
    """
    positions_flat: vector de tamaño 2*N_DRONES -> [x1,y1,x2,y2,...]
    Retorna la suma de probabilidades de celdas cubiertas por >=1 dron.
    """
    positions = positions_flat.reshape(-1, 2)  # (N_DRONES, 2)
    diffs = cell_coords[:, None, :] - positions[None, :, :]
    dists = np.linalg.norm(diffs, axis=2)  # (n_cells, n_drones)
    covered = np.any(dists <= DETECTION_RADIUS, axis=1)
    score = float(np.sum(cell_probs[covered]))
    return score

# ------------------ PSO Implementation ------------------
dim = 2 * N_DRONES
pos_min = np.zeros(dim)
pos_max = np.ones(dim) * AREA_SIZE

# Inicializar partículas (posiciones y velocidades)
particles_pos = np.random.uniform(low=0.0, high=AREA_SIZE, size=(N_PARTICLES, dim))
particles_vel = np.random.uniform(low=-VEL_CLAMP, high=VEL_CLAMP, size=(N_PARTICLES, dim)) * 0.1
particles_best_pos = particles_pos.copy()
particles_best_score = np.array([coverage_score(p) for p in particles_pos])

global_best_idx = np.argmax(particles_best_score)
global_best_pos = particles_best_pos[global_best_idx].copy()
global_best_score = particles_best_score[global_best_idx]

history = []
start_time = time.time()

for it in range(N_ITER):
    r1 = np.random.rand(N_PARTICLES, dim)
    r2 = np.random.rand(N_PARTICLES, dim)
    cognitive = C1 * r1 * (particles_best_pos - particles_pos)
    social = C2 * r2 * (global_best_pos[None, :] - particles_pos)
    particles_vel = W * particles_vel + cognitive + social
    particles_vel = np.clip(particles_vel, -VEL_CLAMP, VEL_CLAMP)
    particles_pos = particles_pos + particles_vel
    particles_pos = np.clip(particles_pos, pos_min, pos_max)

    # evaluar partículas y actualizar mejores
    for i in range(N_PARTICLES):
        score = coverage_score(particles_pos[i])
        if score > particles_best_score[i]:
            particles_best_score[i] = score
            particles_best_pos[i] = particles_pos[i].copy()
        if score > global_best_score:
            global_best_score = score
            global_best_pos = particles_pos[i].copy()

    history.append(global_best_score)
    if (it+1) % 20 == 0 or it == 0:
        elapsed = time.time() - start_time
        print(f"Iter {it+1:3d}/{N_ITER}  Mejor score = {global_best_score:.4f}  Tiempo {elapsed:.1f}s")

print("\nOptimización completada.")
print(f"Mejor score final (probabilidad cubierta total): {global_best_score:.4f}")

best_positions = global_best_pos.reshape(-1, 2)

# ------------------ Visualizaciones ------------------
fig = plt.figure(figsize=(12,5))

# Mapa de probabilidad + posiciones de drones
ax1 = fig.add_subplot(1,2,1)
im = ax1.imshow(prob_map, origin='lower', extent=[0, AREA_SIZE, 0, AREA_SIZE])
ax1.set_title("Mapa de probabilidad y posiciones finales de drones")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("y (m)")
ax1.scatter(best_positions[:,0], best_positions[:,1], marker='o', s=30)
for (x,y) in best_positions:
    circle = plt.Circle((x,y), DETECTION_RADIUS, fill=False, linewidth=0.8)
    ax1.add_patch(circle)
plt.colorbar(im, ax=ax1, label='Probabilidad (normalizada)')

# Evolución del mejor fitness
ax2 = fig.add_subplot(1,2,2)
ax2.plot(history)
ax2.set_title("Evolución del mejor score durante iteraciones")
ax2.set_xlabel("Iteración")
ax2.set_ylabel("Mejor score (suma de probabilidades)")

plt.tight_layout()
plt.show()

# Mapa de cobertura resultante (máscara)
covered_mask = np.zeros(cell_probs.shape, dtype=bool)
for (x,y) in best_positions:
    dists = np.linalg.norm(cell_coords - np.array([x,y])[None,:], axis=1)
    covered_mask |= (dists <= DETECTION_RADIUS)

covered_map = covered_mask.reshape((GRID_RES, GRID_RES))

plt.figure(figsize=(6,6))
plt.title("Mapa de cobertura resultante (1 = cubierto por al menos un dron)")
plt.imshow(covered_map, origin='lower', extent=[0, AREA_SIZE, 0, AREA_SIZE])
plt.xlabel("x (m)"); plt.ylabel("y (m)")
plt.show()

# ------------------ Resultados numéricos ------------------
print("\nPosiciones finales de los drones (metros):")
for i, (x,y) in enumerate(best_positions, start=1):
    print(f" Dron {i:2d}: x={x:8.1f} m, y={y:8.1f} m")

print(f"\nPorcentaje de área en la cuadrícula cubierta: {100.0 * covered_mask.sum() / covered_mask.size:.2f}%")