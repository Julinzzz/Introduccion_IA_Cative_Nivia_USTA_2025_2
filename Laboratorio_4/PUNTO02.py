import numpy as np
import matplotlib.pyplot as plt
import random

# ------------------------------
# Configuración
# ------------------------------
GRID_SIZE = 20
N_DRONES = 20
N_ITER = 100
N_SURVIVORS = 8
OBSTACLE_PROB = 0.15

# Parámetros ACO
ALPHA = 1.0
BETA = 2.0
RHO = 0.2
Q = 200

# ------------------------------
# Crear terreno
# ------------------------------
grid = np.zeros((GRID_SIZE, GRID_SIZE))
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if random.random() < OBSTACLE_PROB:
            grid[i, j] = 1

base = (0, 0)
grid[base] = 0

survivors = []
while len(survivors) < N_SURVIVORS:
    x, y = np.random.randint(0, GRID_SIZE, 2)
    if grid[x, y] == 0 and (x, y) != base:
        survivors.append((x, y))

# ------------------------------
# Inicializar feromonas
# ------------------------------
pheromone = np.ones((GRID_SIZE, GRID_SIZE)) * 0.1

# ------------------------------
# Funciones auxiliares
# ------------------------------
def get_neighbors(pos):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if grid[nx, ny] == 0:
                neighbors.append((nx, ny))
    return neighbors

def move_ant(pos, visited):
    neighbors = get_neighbors(pos)
    if not neighbors:
        return pos

    probs = []
    for n in neighbors:
        tau = pheromone[n] ** ALPHA
        eta = (1.0 / (1 + np.linalg.norm(np.array(n) - np.array(pos)))) ** BETA
        if n in visited:
            probs.append((n, 0.1 * tau * eta))  # penalización
        else:
            probs.append((n, tau * eta))

    total = sum(p for _, p in probs)
    if total == 0:
        return random.choice(neighbors)
    probs = [(n, p/total) for n, p in probs]

    r = random.random()
    cum = 0
    for n, p in probs:
        cum += p
        if r <= cum:
            return n
    return probs[-1][0]

def update_pheromones(paths, survivors_found):
    global pheromone
    pheromone *= (1 - RHO)
    for path in paths:
        L = len(path)
        for pos in path:
            pheromone[pos] += Q / (L+1e-6)
            if pos in survivors_found:
                pheromone[pos] += Q * 5

# ------------------------------
# Simulación principal
# ------------------------------
def run_simulation():
    coverage = np.zeros_like(grid)
    energy_consumed = 0
    survivors_found = set()

    for it in range(N_ITER):
        paths = []
        for d in range(N_DRONES):
            pos = base
            path = [pos]
            visited = set([pos])

            for _ in range(GRID_SIZE*3):
                new_pos = move_ant(pos, visited)
                path.append(new_pos)
                visited.add(new_pos)
                coverage[new_pos] = 1
                energy_consumed += 1

                if new_pos in survivors:
                    survivors_found.add(new_pos)

                pos = new_pos

            paths.append(path)

        update_pheromones(paths, survivors_found)

        if it == N_ITER//2:
            ox, oy = np.random.randint(0, GRID_SIZE, 2)
            grid[ox, oy] = 1
            print(f"⚠️ Nuevo obstáculo introducido en {ox, oy}")

    total_area = GRID_SIZE * GRID_SIZE - np.sum(grid==1)
    covered_area = np.sum(coverage==1)
    coverage_percent = (covered_area / total_area) * 100

    return coverage, survivors_found, coverage_percent, energy_consumed

# ------------------------------
# Ejecutar
# ------------------------------
coverage, survivors_found, coverage_percent, energy_consumed = run_simulation()

# ------------------------------
# Visualización con métricas
# ------------------------------
plt.figure(figsize=(8,8))
plt.imshow(grid, cmap="gray_r", origin="lower")

# Supervivientes encontrados (verde) y no encontrados (rojo)
for (x,y) in survivors:
    if (x,y) in survivors_found:
        plt.scatter(y, x, c="green", marker="o", s=100)  # sin label para evitar duplicados
    else:
        plt.scatter(y, x, c="red", marker="o", s=100)

# Base
plt.scatter(base[1], base[0], c="blue", marker="s", s=100)

# Cobertura
covered_x, covered_y = np.where(coverage==1)
plt.scatter(covered_y, covered_x, c="yellow", marker=".", alpha=0.3)

# Feromonas
plt.imshow(pheromone, cmap="Reds", alpha=0.4, origin="lower")

# Título y métricas en figura
plt.title("Simulación ACO - Drones en rescate")
metrics_text = (
    f"Supervivientes encontrados: {len(survivors_found)} / {len(survivors)}\n"
    f"Cobertura: {coverage_percent:.1f}%\n"
    f"Energía consumida: {energy_consumed}"
)
plt.gcf().text(0.02, 0.02, metrics_text, fontsize=10, va="bottom", ha="left",
               bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

# 🔹 Leyenda limpia con solo 4 indicadores
handles = [
    plt.Line2D([0],[0], marker="o", color="w", label="Superviviente encontrado", markerfacecolor="green", markersize=10),
    plt.Line2D([0],[0], marker="o", color="w", label="Superviviente no encontrado", markerfacecolor="red", markersize=10),
    plt.Line2D([0],[0], marker="s", color="w", label="Base", markerfacecolor="blue", markersize=10),
    plt.Line2D([0],[0], marker=".", color="yellow", label="Cobertura", markersize=10)
]
plt.legend(handles=handles, loc="upper right", fontsize=8)

plt.show()
