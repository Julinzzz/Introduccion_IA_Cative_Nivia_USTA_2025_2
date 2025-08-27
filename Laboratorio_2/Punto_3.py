"""
02_apf_bdi_astar_simple_mitad.py
----------------------------------
Versión INTERMEDIA (commit 2)
- Integra BDI + A* para crear un waypoint de escape.
- Movimiento: APF + empuje directo al (sub)objetivo.
- Sin control de clearance/colisión (puede cortar esquinas).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import heapq

# --- Parámetros ---
K_ATR, K_REP, RADIO_REP = 0.5, 3.5, 3.0
ALPHA_APF = 0.12
BETA_WAYPOINT = 0.45
WINDOW = 14
UMBRAL_GRAD = 0.05
UMBRAL_MEJORA_DIST = 0.02
UMBRAL_MOV = 0.03

GRID_MIN, GRID_MAX = 0, 15
MOVES_8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
WAYPOINT_DIST = 0.7

def potencial_total(p, g, obs, eps=0.25):
    U_attr = 0.5 * K_ATR * np.linalg.norm(g - p)**2
    U_rep = 0.0
    for o in obs:
        d = np.linalg.norm(p - o)
        if 1 <= d < RADIO_REP:
            U_rep += 0.5 * K_REP * (1/d - 1/RADIO_REP)**2
        elif eps < d < 1:
            U_rep += 0.5 * K_REP * (1/d - 1/RADIO_REP)
    return U_attr + U_rep

def gradiente(p, g, obs, h=0.12):
    grad = np.zeros(2)
    for i in range(2):
        dp = np.zeros(2); dp[i] = h
        grad[i] = (potencial_total(p+dp, g, obs) - potencial_total(p-dp, g, obs)) / (2*h)
    return grad

# --- A* simple (sin clearance) ---
def a_star(start_xy, goal_xy, obst_set):
    def h(a,b): return np.hypot(a[0]-b[0], a[1]-b[1])
    start = tuple(map(int, map(round, start_xy)))
    goal  = tuple(map(int, map(round, goal_xy)))
    openh = [(h(start,goal), 0.0, start, None)]
    came, gcost = {}, {start: 0.0}
    while openh:
        f,g,u,parent = heapq.heappop(openh)
        if u in came: continue
        came[u] = parent
        if u == goal: break
        for dx,dy in MOVES_8:
            v = (u[0]+dx, u[1]+dy)
            if not (GRID_MIN <= v[0] <= GRID_MAX and GRID_MIN <= v[1] <= GRID_MAX): continue
            if v in obst_set: continue
            # evitar cortar esquinas diagonales por celdas bloqueadas inmediatas
            if dx!=0 and dy!=0:
                if (u[0]+dx, u[1]) in obst_set or (u[0], u[1]+dy) in obst_set: continue
            ng = g + np.hypot(dx,dy)
            if v not in gcost or ng < gcost[v]:
                gcost[v] = ng
                heapq.heappush(openh, (ng + h(v,goal), ng, v, u))
    if goal not in came: return []
    path, cur = [goal], goal
    while came[cur] is not None:
        cur = came[cur]; path.append(cur)
    return list(reversed(path))

def waypoint_seguro(path, p_actual):
    if not path: return None
    pa = tuple(map(int, map(round, p_actual)))
    for node in path[3:] + path[-1:]:
        if np.hypot(node[0]-pa[0], node[1]-pa[1]) >= 2.0:
            return np.array(node, dtype=float)
    k = min(3, len(path)-1)
    return np.array(path[k], dtype=float)

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
        self.first_tick = True

    def actualizar_creencias(self):
        U = potencial_total(self.p, self.G_ACTUAL, self.obs)
        self.histU.append(U)
        self.histPos.append(self.p.copy())
        self.dist_obj = np.linalg.norm(self.G_REAL - self.p)
        self.histDist.append(self.dist_obj)
        self.grad = gradiente(self.p, self.G_ACTUAL, self.obs)

    def estancado(self):
        if len(self.histDist) < WINDOW: return False
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
        wp = waypoint_seguro(self.path, self.p)
        if wp is not None:
            self.waypoint = wp
            self.G_ACTUAL = self.waypoint
            self.intencion = "escapar_minimo"

    def revisar_cambio_objetivo(self):
        if self.intencion == "escapar_minimo" and np.linalg.norm(self.p - self.G_ACTUAL) < WAYPOINT_DIST:
            self.waypoint = None
            self.G_ACTUAL = self.G_REAL
            self.intencion = "seguir_gradiente"

    def actuar(self):
        # Movimiento sin chequeo de colisiones (se corrige en la versión final)
        dir_goal = self.G_ACTUAL - self.p
        n = np.linalg.norm(dir_goal)
        if n > 1e-9: dir_goal /= n
        delta = -ALPHA_APF * self.grad + BETA_WAYPOINT * dir_goal
        self.p += delta

    def tick(self):
        if self.first_tick:
            self.plan_escape()           # fuerza un plan de escape inicial (más estable)
            self.first_tick = False

        self.actualizar_creencias()
        if self.estancado() and self.intencion != "escapar_minimo":
            self.plan_escape()
        self.revisar_cambio_objetivo()
        self.actuar()

# --- Escenario (herradura) ---
P0 = np.array([1.0, 1.0])
G  = np.array([12.0, 12.0])
OBS = np.array([
    [2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],
    [3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],
    [4,9],[5,9],[6,9],[7,9],[8,9],
    [9,2],[9,3],[9,4],[9,5],[9,6],[9,7],[9,8],[9,9],
    [10,2],[10,3],[10,4],[10,5],[10,6],[10,7],[10,8],[10,9],[10,10]
])

agent = AgenteBDI(P0, G, OBS)

# --- Visualización ---
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12,5))
def update(_):
    agent.tick()
    ax.clear()
    for o in OBS: ax.scatter(o[0], o[1], c='black', marker='x', s=80)
    ax.scatter(agent.p[0], agent.p[1], c='red', s=200, label="Agente")
    ax.scatter(agent.G_REAL[0], agent.G_REAL[1], c='green', marker='x', s=120, label="Objetivo real")
    if agent.waypoint is not None:
        ax.scatter(agent.waypoint[0], agent.waypoint[1], c='orange', marker='*', s=160, label="Waypoint A*")
        if agent.path:
            xs, ys = zip(*agent.path)
            ax.plot(xs, ys, linestyle='--', linewidth=1, alpha=0.6)
    ax.set_xlim(0,15); ax.set_ylim(0,15); ax.legend(loc="upper left", fontsize=8)
    ax.set_title(f"APF + BDI + A* (modo: {agent.intencion})"); ax.set_xlabel("x"); ax.set_ylabel("y")

    ax2.clear(); ax2.plot(agent.histU, label="Energía Potencial")
    ax2.set_title("Evolución de la Energía Potencial"); ax2.legend()

ani = FuncAnimation(fig, update, frames=320, interval=120)
plt.tight_layout()
if __name__ == "__main__":
    plt.show()
