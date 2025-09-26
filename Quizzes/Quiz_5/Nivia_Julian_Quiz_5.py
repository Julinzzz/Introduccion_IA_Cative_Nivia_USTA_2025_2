# pso_drones_busqueda.py
# --------------------------------------------------------------
# Introducción a IA: Coordinación de drones con PSO para búsqueda
# Autor: (tu nombre)
# --------------------------------------------------------------
# Supuestos (razonables para un contexto introductorio):
# - Área cuadrada 5 km x 5 km -> coordenadas [0, 5000] m.
# - 10 drones, todos parten desde (0,0) al mismo tiempo.
# - Velocidad constante por dron: 12 m/s.
# - Tiempo máximo de misión: 120 minutos -> 7200 s
# - Presupuesto de recorrido por dron = speed * time = 86.4 km (muy amplio para 5x5 km),
#   pero igualmente se respeta y se penaliza si se excede.
# - Cada dron visita W waypoints; el sensor "cubre" un disco de 200 m alrededor
#   de cada waypoint (buena aproximación si se vuela patrón de búsqueda local).
# - El mapa de probabilidad se genera como mezcla de varias "zonas calientes"
#   (gaussianas) + ruido suave (puedes reemplazarlo por un mapa real si lo tienes).
#
# Objetivo de optimización:
# - Maximizar la probabilidad total cubierta (unión de celdas cubiertas por cualquier dron),
#   penalizando:
#     1) Recorridos por dron que excedan el presupuesto de distancia.
#     2) Soluciones con mucha superposición entre drones (para fomentar cobertura diversa).
#
# Salidas:
# - Mejor conjunto de waypoints por dron.
# - Métricas de cobertura y penalizaciones.
# - Gráficos: mapa de probabilidad y trayectorias óptimas.
# --------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# Parámetros del problema
# ---------------------------
SEED = 42
rng = np.random.default_rng(SEED)

AREA = 5000.0           # metros, lado del cuadrado
N_DRONES = 10
SENSOR_R = 200.0        # metros
SPEED = 12.0            # m/s
T_MAX_MIN = 120
T_MAX = T_MAX_MIN * 60  # s
BUDGET_PER_DRONE = SPEED * T_MAX  # metros

# Waypoints por dron (mantener moderado para que el PSO sea rápido)
W = 4                   # 4 puntos por dron -> 8 variables por dron (x,y)
DIM = N_DRONES * W * 2  # dimensión del vector de decisión

# Discretización del mapa (ocupancy/prob map) para integrar cobertura
GRID = 100              # 100 x 100 celdas (cada celda ~50 m)
cell = AREA / GRID
xs = np.linspace(0, AREA, GRID)
ys = np.linspace(0, AREA, GRID)
XX, YY = np.meshgrid(xs, ys)

# ---------------------------
# Crear mapa de probabilidades (toy)
# Mezcla de gausianas + ruido suave
# ---------------------------
def gaussian_2d(x, y, mux, muy, sx, sy):
    return np.exp(-(((x-mux)**2)/(2*sx**2) + ((y-muy)**2)/(2*sy**2)))

def build_probability_map():
    hotspots = []
    K = 5  # número de zonas calientes
    for _ in range(K):
        mux = rng.uniform(0.15*AREA, 0.85*AREA)
        muy = rng.uniform(0.15*AREA, 0.85*AREA)
        sx  = rng.uniform(0.10*AREA, 0.25*AREA)
        sy  = rng.uniform(0.10*AREA, 0.25*AREA)
        amp = rng.uniform(0.7, 1.2)
        hotspots.append(amp * gaussian_2d(XX, YY, mux, muy, sx, sy))

    base = sum(hotspots)
    base += 0.1 * rng.random(size=base.shape)  # ruido suave
    base = np.maximum(base, 0)
    # normalizar a [0,1] para que "suma de probas" tenga escala interpretable
    base = (base - base.min()) / (base.max() - base.min() + 1e-9)
    return base

PROB = build_probability_map()

# Máscaras de cobertura: para acelerar evaluaciones,
# precomputamos el centro de cada celda y su índice lineal.
cells_xy = np.stack([XX.ravel(), YY.ravel()], axis=1)

def coverage_mask_from_points(points_xy, radius=SENSOR_R):
    """
    points_xy: array shape (K,2) con waypoints
    return: boolean mask (GRID*GRID,) True si la celda está cubierta por al menos un punto
    """
    if points_xy.size == 0:
        return np.zeros(GRID*GRID, dtype=bool)
    # Distancia mínima desde cada celda a los waypoints
    # Para eficiencia: calcula d^2 celda-punto por bloques si te preocupa la RAM.
    d2 = ((cells_xy[:, None, :] - points_xy[None, :, :])**2).sum(axis=2)
    min_d2 = d2.min(axis=1)
    return min_d2 <= radius**2

def route_length(points_xy, start=(0.0, 0.0)):
    """
    Longitud total (m) del recorrido: arranca en 'start' y visita los waypoints en el orden dado.
    """
    if len(points_xy) == 0:
        return 0.0
    length = 0.0
    prev = np.array(start, dtype=float)
    for p in points_xy:
        length += np.linalg.norm(p - prev)
        prev = p
    return length

# ---------------------------
# Función objetivo para PSO
# ---------------------------
P_MAP = PROB.ravel()
TOTAL_PROB_MASS = P_MAP.sum()  # útil para interpretar cobertura

def decode_position(x):
    """
    x: vector 1D de tamaño DIM en [0, AREA].
    Return: lista de arrays por dron: [ (W,2), (W,2), ..., ]
    """
    pts_per_drone = []
    for d in range(N_DRONES):
        start = d * W * 2
        chunk = x[start:start + W*2]
        pts = chunk.reshape(W, 2)
        pts_per_drone.append(pts)
    return pts_per_drone

def objective(x):
    """
    Devuelve un costo NEGATIVO de utilidad (porque el PSO lo minimiza).
    Queremos MAXIMIZAR la probabilidad cubierta, por lo que usamos -score.
    Penalizaciones:
      - Exceso de recorrido por dron (sobre BUDGET_PER_DRONE)
      - Superposición fuerte entre drones (para fomentar diversidad)
    """
    pts_list = decode_position(x)

    # Cobertura total (unión) y superposición
    union_mask = np.zeros(GRID*GRID, dtype=bool)
    overlap_count = np.zeros(GRID*GRID, dtype=np.int16)

    penalty_route = 0.0
    for pts in pts_list:
        # Longitud de ruta
        L = route_length(pts)
        if L > BUDGET_PER_DRONE:
            penalty_route += (L - BUDGET_PER_DRONE) / 1000.0  # km excedidos

        # cobertura por dron
        mask_d = coverage_mask_from_points(pts)
        union_mask |= mask_d
        overlap_count += mask_d.astype(np.int16)

    # Puntuación base: masa de prob cubierta (suma de probabilidades de celdas cubiertas)
    base_score = P_MAP[union_mask].sum()

    # Penalizar solapamiento (celdas cubiertas por >=2 drones)
    # (No queremos castigar levemente el solapamiento inevitable; solo castigos suaves)
    overlap_cells = np.clip(overlap_count - 1, 0, None)
    overlap_pen = 0.10 * P_MAP[(overlap_cells > 0)].sum()

    # Costo final (negativo para minimizar)
    score = base_score - overlap_pen - 1e4 * penalty_route
    return -float(score)

# ---------------------------
# PSO (sencillo, desde cero)
# ---------------------------
class PSO:
    def __init__(self, dim, n_particles=80, iters=150,
                 bounds=(0.0, AREA), w=0.72, c1=1.49, c2=1.49):
        self.dim = dim
        self.n = n_particles
        self.iters = iters
        self.lo, self.hi = bounds
        self.w, self.c1, self.c2 = w, c1, c2

        self.X = rng.uniform(self.lo, self.hi, size=(self.n, self.dim))
        self.V = rng.normal(0, (self.hi-self.lo)*0.05, size=(self.n, self.dim))
        self.pbest_X = self.X.copy()
        self.pbest_f = np.array([objective(x) for x in self.X])
        g_idx = np.argmin(self.pbest_f)
        self.gbest_X = self.pbest_X[g_idx].copy()
        self.gbest_f = self.pbest_f[g_idx]

    def step(self, t):
        r1 = rng.random(size=(self.n, self.dim))
        r2 = rng.random(size=(self.n, self.dim))

        cognitive = self.c1 * r1 * (self.pbest_X - self.X)
        social    = self.c2 * r2 * (self.gbest_X - self.X)
        self.V = self.w * self.V + cognitive + social

        # Avance y restricción a los límites
        self.X = self.X + self.V
        self.X = np.clip(self.X, self.lo, self.hi)

        # Evaluación
        fvals = np.array([objective(x) for x in self.X])

        # Actualiza mejores personales
        better = fvals < self.pbest_f
        self.pbest_X[better] = self.X[better]
        self.pbest_f[better] = fvals[better]

        # Actualiza mejor global
        g_idx = np.argmin(self.pbest_f)
        if self.pbest_f[g_idx] < self.gbest_f:
            self.gbest_f = self.pbest_f[g_idx]
            self.gbest_X = self.pbest_X[g_idx].copy()

    def run(self, verbose=True):
        for t in range(self.iters):
            self.step(t)
            if verbose and (t % 10 == 0 or t == self.iters-1):
                print(f"[Iter {t+1:3d}/{self.iters}] mejor costo = {self.gbest_f:.3f}")
        return self.gbest_X, self.gbest_f

# ---------------------------
# Ejecutar la optimización
# ---------------------------
if __name__ == "__main__":
    pso = PSO(DIM, n_particles=80, iters=150)
    best_x, best_cost = pso.run(verbose=True)

    # Decodificar solución y métricas
    best_pts = decode_position(best_x)

    # Cobertura final y métricas explicativas
    union_mask = np.zeros(GRID*GRID, dtype=bool)
    overlap_count = np.zeros(GRID*GRID, dtype=np.int16)
    lengths = []
    for pts in best_pts:
        lengths.append(route_length(pts))
        mask_d = coverage_mask_from_points(pts)
        union_mask |= mask_d
        overlap_count += mask_d.astype(np.int16)

    covered_mass = P_MAP[union_mask].sum()
    covered_pct  = 100.0 * covered_mass / (TOTAL_PROB_MASS + 1e-9)
    overlap_cells = np.clip(overlap_count - 1, 0, None)
    overlap_mass = P_MAP[(overlap_cells > 0)].sum()

    print("\n===== RESULTADOS =====")
    for i, L in enumerate(lengths, 1):
        print(f"Dron {i:02d}: recorrido = {L/1000:.2f} km (presupuesto {BUDGET_PER_DRONE/1000:.1f} km)")
    print(f"Cobertura de probabilidad (masa relativa): {covered_pct:.2f}%")
    print(f"Masa en celdas solapadas (castigada): {overlap_mass:.3f}")
    print(f"Función objetivo (negativa, porque minimizamos): {best_cost:.3f}")

    # ---------------------------
    # Gráficos
    # ---------------------------
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(PROB, origin='lower', extent=[0, AREA, 0, AREA])
    cb = plt.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("Probabilidad (mapa)")

    # Dibuja trayectorias y discos de cobertura en cada waypoint
    for d, pts in enumerate(best_pts, 1):
        pts = np.array(pts)
        ax.plot([0, *pts[:,0]], [0, *pts[:,1]], marker='o', linewidth=1.5, label=f"Dron {d}")
        # círculos de cobertura
        for (x, y) in pts:
            circ = plt.Circle((x, y), SENSOR_R, fill=False, alpha=0.4)
            ax.add_patch(circ)

    ax.set_title("Búsqueda con PSO: trayectorias y cobertura (radio sensor = 200 m)")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.legend(ncol=2, fontsize=8, loc="upper right")
    plt.tight_layout()
    plt.show()
