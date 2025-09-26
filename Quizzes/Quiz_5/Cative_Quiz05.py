"""
pso_drones_optimizado.py

PSO mejorado para coordinar 10 drones en un área de 5x5 km y maximizar
la cobertura (área) y la probabilidad simultáneamente.

"""

import numpy as np
import matplotlib.pyplot as plt
import time

# ------------------ Parámetros del problema ------------------
AREA_SIZE = 5000.0       # metros (5 km)
GRID_RES = 120           # resolución del grid (GRID_RES x GRID_RES). Aumentar para más precisión.
N_DRONES = 10
DETECTION_RADIUS = 200.0  # metros

# ------------------ Parámetros PSO (ajustables) ------------------
N_PARTICLES = 60
N_ITER = 250
W = 0.7       # inertia
C1 = 1.5      # cognitive
C2 = 1.5      # social
VEL_CLAMP = 500.0

# ------------------ Pesos de la función objetivo (ajustables) ------------------
# score = w_prob * (probabilidad cubierta normalizada)
#       + w_area * (fracción de área cubierta)
#       + w_spread * (separación normalizada entre drones)
w_prob = 0.20
w_area = 0.75
w_spread = 0.05

np.random.seed(42)

# ------------------ Generar mapa de probabilidades (simulado) ------------------
grid_x = np.linspace(0, AREA_SIZE, GRID_RES)
grid_y = np.linspace(0, AREA_SIZE, GRID_RES)
xx, yy = np.meshgrid(grid_x, grid_y)
prob_map = np.zeros_like(xx)

# Hotspots (gaussianas) representando zonas con mayor probabilidad de sobrevivientes
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
TOTAL_PROB_SUM = float(cell_probs.sum())
N_CELLS = cell_probs.size
MAX_PAIRWISE_SUM = (np.sqrt(2) * AREA_SIZE) * (N_DRONES * (N_DRONES - 1) / 2)

def objective_score(positions_flat):
    """
    Retorna (score_scalar, covered_prob, coverage_frac, spread_norm)
    - score_scalar: valor objetivo para PSO (mayor es mejor)
    - covered_prob: suma de probabilidades cubiertas (no normalizada)
    - coverage_frac: fracción de celdas cubiertas
    - spread_norm: suma de distancias pares normalizada
    """
    positions = positions_flat.reshape(-1, 2)  # (N_DRONES, 2)

    # Distancias celdas <-> drones (vectorizado)
    diffs = cell_coords[:, None, :] - positions[None, :, :]                # (n_cells, n_drones, 2)
    dists = np.linalg.norm(diffs, axis=2)                                # (n_cells, n_drones)
    covered_mask = np.any(dists <= DETECTION_RADIUS, axis=1)             # (n_cells,)
    covered_prob = float(np.sum(cell_probs[covered_mask]))               # probabilidad cubierta
    coverage_frac = float(np.sum(covered_mask)) / float(N_CELLS)         # fracción de celdas cubiertas

    # Spread (separación entre drones): sum de distancias únicas
    pdists = np.linalg.norm(positions[:, None, :] - positions[None, :, :], axis=2)
    iu = np.triu_indices(N_DRONES, k=1)
    sum_pairwise = float(pdists[iu].sum())
    spread_norm = sum_pairwise / MAX_PAIRWISE_SUM if MAX_PAIRWISE_SUM > 0 else 0.0

    # Normalizar covered_prob a [0,1] para combinar
    covered_prob_norm = covered_prob / TOTAL_PROB_SUM if TOTAL_PROB_SUM > 0 else 0.0

    # Score combinado (ajustar pesos arriba)
    score = w_prob * covered_prob_norm + w_area * coverage_frac + w_spread * spread_norm

    return score, covered_prob, coverage_frac, spread_norm

# ------------------ PSO Implementation ------------------
dim = 2 * N_DRONES
pos_min = np.zeros(dim)
pos_max = np.ones(dim) * AREA_SIZE

# Inicializar partículas
particles_pos = np.random.uniform(low=0.0, high=AREA_SIZE, size=(N_PARTICLES, dim))
particles_vel = np.random.uniform(low=-VEL_CLAMP, high=VEL_CLAMP, size=(N_PARTICLES, dim)) * 0.05

# Heurística: algunas partículas iniciales con drones en una retícula (mejora cobertura inicial)
def grid_initial_positions():
    # distribuir N_DRONES en una retícula lo más cuadrada posible
    n_cols = int(np.ceil(np.sqrt(N_DRONES)))
    n_rows = int(np.ceil(N_DRONES / n_cols))
    xs = np.linspace(AREA_SIZE*0.1, AREA_SIZE*0.9, n_cols)
    ys = np.linspace(AREA_SIZE*0.1, AREA_SIZE*0.9, n_rows)
    pts = []
    for yi in ys:
        for xi in xs:
            pts.append((xi, yi))
            if len(pts) >= N_DRONES:
                break
        if len(pts) >= N_DRONES:
            break
    arr = np.array(pts)[:N_DRONES].reshape(-1)
    return arr

base_grid = grid_initial_positions()
# setear las primeras ~10 partículas con variaciones de la retícula
k = min(10, N_PARTICLES)
for i in range(k):
    jitter = np.random.normal(scale=AREA_SIZE*0.02, size=dim)  # pequeña variación aleatoria
    particles_pos[i] = np.clip(base_grid + jitter, pos_min, pos_max)

# evaluar partículas
particles_best_pos = particles_pos.copy()
particles_best_score = np.empty(N_PARTICLES)
for i in range(N_PARTICLES):
    s, _, _, _ = objective_score(particles_pos[i])
    particles_best_score[i] = s

global_best_idx = np.argmax(particles_best_score)
global_best_pos = particles_best_pos[global_best_idx].copy()
global_best_score = particles_best_score[global_best_idx]

history = []
start_time = time.time()

# PSO loop
for it in range(N_ITER):
    r1 = np.random.rand(N_PARTICLES, dim)
    r2 = np.random.rand(N_PARTICLES, dim)
    cognitive = C1 * r1 * (particles_best_pos - particles_pos)
    social = C2 * r2 * (global_best_pos[None, :] - particles_pos)
    particles_vel = W * particles_vel + cognitive + social
    particles_vel = np.clip(particles_vel, -VEL_CLAMP, VEL_CLAMP)
    particles_pos = particles_pos + particles_vel
    particles_pos = np.clip(particles_pos, pos_min, pos_max)

    for i in range(N_PARTICLES):
        s, _, _, _ = objective_score(particles_pos[i])
        if s > particles_best_score[i]:
            particles_best_score[i] = s
            particles_best_pos[i] = particles_pos[i].copy()
        if s > global_best_score:
            global_best_score = s
            global_best_pos = particles_pos[i].copy()

    history.append(global_best_score)
    if (it + 1) % 10 == 0 or it == 0:
        elapsed = time.time() - start_time
        # calcular métricas de la solución global actual para mostrar progreso
        _, g_covprob, g_covfrac, g_spread = objective_score(global_best_pos)
        print(f"Iter {it+1:4d}/{N_ITER}  Score={global_best_score:.5f}  "
              f"prob_cubierta={g_covprob:.3f}  area_pct={100*g_covfrac:.2f}%  spread={g_spread:.4f}  tiempo={elapsed:.1f}s")

print("\nOptimización completada.")
# métricas finales
final_score, final_covprob, final_covfrac, final_spread = objective_score(global_best_pos)
print(f"Mejor score final: {final_score:.5f}")
print(f"Prob. cubierta (suma): {final_covprob:.3f} / {TOTAL_PROB_SUM:.3f}")
print(f"Fracción de área cubierta: {final_covfrac:.4f} ({100*final_covfrac:.2f}%)")
print(f"Spread normalizado: {final_spread:.4f}")

best_positions = global_best_pos.reshape(-1, 2)

# ------------------ Visualizaciones ------------------
fig = plt.figure(figsize=(12,5))
ax1 = fig.add_subplot(1,2,1)
im = ax1.imshow(prob_map, origin='lower', extent=[0, AREA_SIZE, 0, AREA_SIZE])
ax1.set_title("Mapa de probabilidad y posiciones finales de drones (optimizado)")
ax1.set_xlabel("x (m)"); ax1.set_ylabel("y (m)")
ax1.scatter(best_positions[:,0], best_positions[:,1], marker='o', s=40, zorder=5)
for (x,y) in best_positions:
    circle = plt.Circle((x,y), DETECTION_RADIUS, fill=False, linewidth=0.8, zorder=4)
    ax1.add_patch(circle)
plt.colorbar(im, ax=ax1, label='Probabilidad (normalizada)')

ax2 = fig.add_subplot(1,2,2)
ax2.plot(history)
ax2.set_title("Evolución del score (PSO)")
ax2.set_xlabel("Iteración"); ax2.set_ylabel("Score combinado")
plt.tight_layout()
plt.show()

# Mapa de cobertura resultante (máscara)
covered_mask = np.zeros(cell_probs.shape, dtype=bool)
for (x,y) in best_positions:
    dists = np.linalg.norm(cell_coords - np.array([x,y])[None,:], axis=1)
    covered_mask |= (dists <= DETECTION_RADIUS)

covered_map = covered_mask.reshape((GRID_RES, GRID_RES))
plt.figure(figsize=(6,6))
plt.title("Mapa de cobertura (1 = cubierto por >=1 dron)")
plt.imshow(covered_map, origin='lower', extent=[0, AREA_SIZE, 0, AREA_SIZE])
plt.xlabel("x (m)"); plt.ylabel("y (m)")
plt.show()

print("\nPosiciones finales de los drones (metros):")
for i, (x,y) in enumerate(best_positions, start=1):
    print(f" Dron {i:2d}: x={x:8.1f} m, y={y:8.1f} m")

print(f"\nPorcentaje de área en la cuadrícula cubierta: {100.0 * covered_mask.sum() / covered_mask.size:.2f}%")
