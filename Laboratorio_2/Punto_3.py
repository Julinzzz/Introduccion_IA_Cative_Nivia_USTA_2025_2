"""
03e_apf_bdi_astar_seguro_move.py
APF + BDI + A* con movimiento seguro garantizado (sin atravesar obstáculos).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import heapq

# ---------- Parámetros ----------
K_ATR, K_REP, RADIO_REP = 0.5, 3.5, 3.0
ALPHA_APF = 0.12                 # paso por gradiente APF
BETA_WAYPOINT = 0.55             # empuje directo al (sub)objetivo
WINDOW = 16
UMBRAL_GRAD = 0.05
UMBRAL_MEJORA_DIST = 0.02
UMBRAL_MOV = 0.03
MAX_SIN_MEJORA = 60

WAYPOINT_DIST = 0.7
CLEARANCE = 0.55                 # zona de seguridad alrededor de cada obstáculo
MIN_STEP = 1e-5                  # ahora más pequeño para no “congelarse”
LS_SHRINK = 0.5

GRID_MIN, GRID_MAX = 0, 15
MOVES_8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

# ---------- Utilidades geométricas ----------
def dist_point_segment(q, a, b):
    ab = b - a
    den = np.dot(ab, ab)
    t = 0.0 if den < 1e-12 else np.clip(np.dot(q - a, ab) / den, 0, 1)
    proj = a + t * ab
    return np.linalg.norm(q - proj)

def segmento_seguro(a, b, obstaculos, clearance=CLEARANCE):
    for o in obstaculos:
        if dist_point_segment(o, a, b) < clearance:
            return False
    return True

# ---------- APF ----------
def potencial_total(p, g, obs, eps=0.25):
    U_attr = 0.5 * K_ATR * np.linalg.norm(g - p) ** 2
    U_rep = 0.0
    for o in obs:
        d = np.linalg.norm(p - o)
        if 1 <= d < RADIO_REP:
            U_rep += 0.5 * K_REP * (1/d - 1/RADIO_REP) ** 2
        elif eps < d < 1:
            U_rep += 0.5 * K_REP * (1/d - 1/RADIO_REP)
    return U_attr + U_rep

def gradiente(p, g, obs, h=0.12):
    grad = np.zeros(2)
    for i in range(2):
        dp = np.zeros(2); dp[i] = h
        grad[i] = (potencial_total(p+dp, g, obs) - potencial_total(p-dp, g, obs)) / (2*h)
    return grad

# ---------- A* ----------
def a_star(start_xy, goal_xy, obst_set):
    def h(a, b): return np.hypot(a[0]-b[0], a[1]-b[1])
    start = tuple(map(int, map(round, start_xy)))
    goal  = tuple(map(int, map(round, goal_xy)))
    open_heap = [(h(start, goal), 0.0, start, None)]
    came, g_cost = {}, {start: 0.0}
    while open_heap:
        f, g, u, parent = heapq.heappop(open_heap)
        if u in came: continue
        came[u] = parent
        if u == goal: break
        for dx,dy in MOVES_8:
            v = (u[0]+dx, u[1]+dy)
            if not (GRID_MIN <= v[0] <= GRID_MAX and GRID_MIN <= v[1] <= GRID_MAX):
                continue
            if v in obst_set: continue
            # no cortar esquinas
            if dx != 0 and dy != 0:
                if (u[0]+dx, u[1]) in obst_set or (u[0], u[1]+dy) in obst_set:
                    continue
            ng = g + np.hypot(dx,dy)
            if v not in g_cost or ng < g_cost[v]:
                g_cost[v] = ng
                heapq.heappush(open_heap, (ng + h(v, goal), ng, v, u))
    if goal not in came: return []
    path, cur = [goal], goal
    while came[cur] is not None:
        cur = came[cur]; path.append(cur)
    return list(reversed(path))

def waypoint_seguro(path, p_actual, obst_set):
    if not path: return None
    pa = tuple(map(int, map(round, p_actual)))
    for node in path[3:] + path[-1:]:
        if np.hypot(node[0]-pa[0], node[1]-pa[1]) < 2.0:
            continue
        for dx,dy in MOVES_8:
            if (node[0]+dx, node[1]+dy) in obst_set:
                break
        else:
            return np.array(node, dtype=float)
    k = min(4, len(path)-1)
    return np.array(path[k], dtype=float)

# ---------- BDI ----------
class AgenteBDI:
    def __init__(self, p0, g, obs):
        self.p = p0.astype(float)
        self.G_REAL = g.astype(float)
        self.G_ACTUAL = g.astype(float)
        self.obs = obs.astype(float)
        self.obs_set = {tuple(map(int, o)) for o in obs}
        self.histU, self.histDist, self.histPos = [], deque(maxlen=WINDOW), deque(maxlen=WINDOW)
        self.intencion = "seguir_gradiente"
        self.waypoint, self.path = None, []
        self.sin_mejora = 0
        self.first_tick = True

    def actualizar_creencias(self):
        U = potencial_total(self.p, self.G_ACTUAL, self.obs)
        self.histU.append(U)
        self.histPos.append(self.p.copy())
        self.dist_obj = np.linalg.norm(self.G_REAL - self.p)
        self.histDist.append(self.dist_obj)
        self.grad = gradiente(self.p, self.G_ACTUAL, self.obs)

    def estancado(self):
        if len(self.histDist) < WINDOW: 
            return False
        cond_grad = np.linalg.norm(self.grad) < UMBRAL_GRAD
        mejoras = np.diff(np.array(self.histDist))
        mejora_media = -np.mean(np.clip(mejoras, -np.inf, 0))
        movs = [np.linalg.norm(self.histPos[i]-self.histPos[i-1]) for i in range(1,len(self.histPos))]
        mov_media = np.mean(movs) if movs else 1.0
        return cond_grad or (mejora_media < UMBRAL_MEJORA_DIST) or (mov_media < UMBRAL_MOV)

    def plan_escape(self):
        self.path = a_star(self.p, self.G_REAL, self.obs_set)
        if not self.path:
            fallback = (int(GRID_MAX-1), int(GRID_MAX-1))
            self.path = a_star(self.p, fallback, self.obs_set)
        wp = waypoint_seguro(self.path, self.p, self.obs_set)
        if wp is not None:
            self.waypoint = wp
            self.G_ACTUAL = self.waypoint
            self.intencion = "escapar_minimo"

    def revisar_cambio_objetivo(self):
        if self.intencion == "escapar_minimo" and np.linalg.norm(self.p - self.G_ACTUAL) < WAYPOINT_DIST:
            self.waypoint = None
            self.G_ACTUAL = self.G_REAL
            self.intencion = "seguir_gradiente"

    def paso_seguro(self, delta):
        lam = 1.0
        a = self.p
        while lam > MIN_STEP:
            b = self.p + lam * delta
            if segmento_seguro(a, b, self.obs, CLEARANCE):
                return lam * delta
            lam *= LS_SHRINK
        return None

    def follow_path_step(self):
        """Paso corto hacia el siguiente nodo de A* (con seguridad)."""
        if not self.path:
            return False
        # elige el nodo más adelantado aún “razonablemente cerca”
        idx = 1
        if len(self.path) >= 3: idx = 2
        target = np.array(self.path[idx], dtype=float)
        d = target - self.p
        n = np.linalg.norm(d)
        if n < 1e-9: 
            return True
        step = 0.28 * d / n
        safe = self.paso_seguro(step)
        if safe is None:
            # intenta aún más pequeño
            step *= 0.5
            safe = self.paso_seguro(step)
            if safe is None:
                return False
        self.p += safe
        # si nos acercamos bastante, acorta la ruta
        if np.linalg.norm(target - self.p) < 0.6 and len(self.path) > 1:
            self.path = self.path[idx:]
        return True

    def actuar(self):
        dir_goal = self.G_ACTUAL - self.p
        n = np.linalg.norm(dir_goal)
        if n > 1e-9: dir_goal /= n
        delta = -ALPHA_APF * self.grad + BETA_WAYPOINT * dir_goal
        safe_delta = self.paso_seguro(delta)
        if safe_delta is not None:
            self.p += safe_delta
            return
        # si el delta compuesto no es seguro, usa la ruta de A*
        if self.intencion == "escapar_minimo":
            if not self.follow_path_step():
                # última carta: replanificar
                self.plan_escape()
        else:
            # pequeño paso hacia el objetivo real
            tiny = 0.08 * dir_goal
            safe_tiny = self.paso_seguro(tiny)
            if safe_tiny is not None:
                self.p += safe_tiny

    def tick(self):
        if self.first_tick:
            # fuerza plan de escape desde el inicio si hay herradura
            self.plan_escape()
            self.first_tick = False

        prev = getattr(self, "dist_obj", np.inf)
        self.actualizar_creencias()
        self.sin_mejora = 0 if (prev - self.dist_obj) > 0.05 else (self.sin_mejora + 1)

        if (self.estancado() or self.sin_mejora > MAX_SIN_MEJORA) and self.intencion != "escapar_minimo":
            self.plan_escape()

        self.revisar_cambio_objetivo()
        self.actuar()

# ---------- Escenario ----------
P0 = np.array([1.0, 1.0])
G = np.array([12.0, 12.0])
OBS = np.array([
    [2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],
    [3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],
    [4,9],[5,9],[6,9],[7,9],[8,9],
    [9,2],[9,3],[9,4],[9,5],[9,6],[9,7],[9,8],[9,9],
    [10,2],[10,3],[10,4],[10,5],[10,6],[10,7],[10,8],[10,9],[10,10]
])

agent = AgenteBDI(P0, G, OBS)

# ---------- Visual ----------
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12,5))
def update(_):
    agent.tick()
    ax.clear()
    for o in OBS:
        ax.scatter(o[0], o[1], c='black', marker='x', s=80)
    ax.scatter(agent.p[0], agent.p[1], c='red', s=200, label="Agente")
    ax.scatter(agent.G_REAL[0], agent.G_REAL[1], c='green', marker='x', s=120, label="Objetivo real")
    if agent.waypoint is not None:
        ax.scatter(agent.waypoint[0], agent.waypoint[1], c='orange', marker='*', s=160, label="Waypoint A*")
        if agent.path:
            xs, ys = zip(*agent.path)
            ax.plot(xs, ys, linestyle='--', linewidth=1, color='tab:blue', alpha=0.6)
    ax.set_xlim(0, 15); ax.set_ylim(0, 15)
    ax.set_title(f"APF + BDI + A* (modo: {agent.intencion})")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")

    ax2.clear()
    ax2.plot(agent.histU, label="Energía Potencial")
    ax2.set_title("Evolución de la Energía Potencial")
    ax2.set_xlabel("Iteración"); ax2.set_ylabel("Energía Potencial")
    ax2.legend()

ani = FuncAnimation(fig, update, frames=320, interval=120)
plt.tight_layout()
if __name__ == "__main__":
    plt.show()
