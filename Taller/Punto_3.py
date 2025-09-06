
# punto3_circuito_solver_v3.py
# ---------------------------------------------------------------
# Solver robusto para el circuito (A* + movimiento seguro)
# - Reintenta automáticamente si no hay camino (baja CLEARANCE y permite/evita cortar esquinas)
# - Valida conectividad con BFS (sin clearance) para diagnosticar mapas cerrados
# - Mapa ASCII con S abajo-izq y G arriba-der, estilo figura y con paso garantizado
# ---------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import heapq
from collections import deque

# ===============================================================
# Utilidades de mapa
# ===============================================================
def grid_from_ascii(lines):
    H = len(lines)
    W = len(lines[0])
    obst, start, goal = set(), None, None
    # invertimos filas: última línea -> y=0
    for r, row in enumerate(lines[::-1]):
        y = r
        for x, ch in enumerate(row):
            c = ch.upper()
            if c == 'X': obst.add((x,y))
            elif c == 'S': start = (x,y)
            elif c == 'G': goal  = (x,y)
    return obst, start, goal, W, H

def dilate_obstacles(obst, W, H, radius=0.0):
    if radius <= 1e-9: return obst
    r = int(np.ceil(radius))
    K = [(dx,dy) for dx in range(-r,r+1) for dy in range(-r,r+1)
         if np.hypot(dx,dy) <= radius + 1e-9]
    out = set(obst)
    for ox,oy in obst:
        for dx,dy in K:
            nx,ny = ox+dx, oy+dy
            if 0<=nx<W and 0<=ny<H:
                out.add((nx,ny))
    return out

def bfs_connectivity(start, goal, occ, W, H, allow_diag=True):
    """Conectividad sin clearance (para diagnóstico)."""
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    if allow_diag:
        moves += [(1,1),(1,-1),(-1,1),(-1,-1)]
    q = deque([start]); seen = {start}
    while q:
        u = q.popleft()
        if u == goal: return True
        ux,uy = u
        for dx,dy in moves:
            vx,vy = ux+dx, uy+dy
            if not (0<=vx<W and 0<=vy<H): continue
            if (vx,vy) in occ or (vx,vy) in seen: continue
            # opcional: no cortar esquinas
            if dx!=0 and dy!=0:
                if (ux+dx,uy) in occ or (ux,uy+dy) in occ:
                    continue
            seen.add((vx,vy)); q.append((vx,vy))
    return False

# ===============================================================
# A* + ayuda
# ===============================================================
def a_star(start, goal, occ, W, H, allow_cut_corners=False):
    moves = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    def h(a,b): return np.hypot(a[0]-b[0], a[1]-b[1])
    pq = [(h(start,goal), 0.0, start, None)]
    came, g = {}, {start:0.0}
    while pq:
        f, gc, u, p = heapq.heappop(pq)
        if u in came: continue
        came[u] = p
        if u == goal: break
        ux,uy = u
        for dx,dy in moves:
            vx,vy = ux+dx, uy+dy
            if not (0<=vx<W and 0<=vy<H): continue
            if (vx,vy) in occ: continue
            if not allow_cut_corners and dx!=0 and dy!=0:
                if (ux+dx,uy) in occ or (ux,uy+dy) in occ:
                    continue
            ng = gc + np.hypot(dx,dy)
            if (vx,vy) not in g or ng < g[(vx,vy)]:
                g[(vx,vy)] = ng
                heapq.heappush(pq, (ng + h((vx,vy), goal), ng, (vx,vy), u))
    if goal not in came:
        return []
    path = [goal]; c = goal
    while came[c] is not None:
        c = came[c]; path.append(c)
    return list(reversed(path))

def line_of_sight(a, b, occ, _clearance_ignored=None):
    # Raycast: basta con NO pisar celdas ocupadas del 'occ' (ya dilatado)
    ax, ay = a; bx, by = b
    n = max(2, int(np.hypot(bx-ax, by-ay) * 12))  # muestreo un poco más denso
    for i in range(n + 1):
        t = i / n
        x = ax + t * (bx - ax)
        y = ay + t * (by - ay)
        ix, iy = int(round(x)), int(round(y))
        if (ix, iy) in occ:
            return False
    return True


def smooth_path(path, occ, clearance):
    if not path: return path
    out = [path[0]]; i = 0
    while i < len(path)-1:
        j = len(path)-1
        while j>i+1 and not line_of_sight(out[-1], path[j], occ, clearance):
            j -= 1
        out.append(path[j]); i = j
    return out

# ===============================================================
# Movimiento seguro
# ===============================================================
def safe_step(p, target, occ, step_size, clearance, ls_shrink=0.5, min_step=1e-4):
    d = target - p; n = np.linalg.norm(d)
    if n < 1e-9:
        return None
    v = (step_size / n) * d
    lam = 1.0
    while lam > min_step:
        cand = p + lam * v
        if line_of_sight(tuple(p), tuple(cand), occ, clearance):
            return lam * v
        lam *= ls_shrink

    # --- Fallback: probar 8 micro-pasos que acerquen al waypoint ---
    best = None; best_dist = float("inf")
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
        cand = p + 0.6 * step_size * np.array([dx, dy], float)
        if line_of_sight(tuple(p), tuple(cand), occ, clearance):
            d2 = np.linalg.norm(target - cand)
            if d2 < best_dist:
                best_dist = d2; best = cand
    if best is not None:
        return best - p
    return None


# ===============================================================
# Plan con reintentos
# ===============================================================
def plan_with_retries(S, G, obst, W, H):
    # Intentos: (clearance, allow_cut_corners)
    trials = [
        (0.45, False),
        (0.35, False),
        (0.25, False),
        (0.20, False),
        (0.20, True),
        (0.15, True),
        (0.10, True),
    ]
    for clearance, cut in trials:
        occ = dilate_obstacles(obst, W, H, radius=max(0, clearance-0.01))
        path = a_star(S, G, occ, W, H, allow_cut_corners=cut)
        if path:
            sm = smooth_path(path, occ, clearance)
            return sm, occ, clearance, cut
    return [], obst, None, None

# ===============================================================
# Mapa ASCII (garantiza paso, estilo enunciado) — 37x16
# ===============================================================
CIRCUITO_27x14_TOP_DOWN = [
    "........XXXXXXXXXX........G",  # fila 14 (arriba)
    "........XXXXXXXXXX..XXX....",
    ".XXXXX..........XX..XXX....",
    ".XXXXX.XX.......XX..XXX....",
    "....XX.XXXX..XXXXX.....XX..",
    "....XX...XX..XXXXX.....XX..",
    "....XX...........X...XX....",
    ".XXXXXXXXXX......X...XX....",
    ".XXXXXXXXXX..XXXXX...XXXXXX",
    "....XX...XX..XXXXX...XXXXXX",
    "....XX...XX..........X.....",
    "....XX...XX.........XX.....",
    "....XX...XX..XX.....XX.....",
    "S........XX..XX............",  # fila 1 (abajo)
]
# Parámetros de animación
STEP_SIZE = 0.35

def main():
    obst, S, G, W, H = grid_from_ascii(CIRCUITO_27x14_TOP_DOWN)
    if S is None or G is None:
        raise RuntimeError("El mapa debe tener 'S' y 'G'.")

    # Diagnóstico rápido (sin clearance). Si no hay conectividad, el mapa está cerrado.
    if not bfs_connectivity(S, G, obst, W, H, allow_diag=True):
        print("[ADVERTENCIA] El mapa base no conecta S con G (sin clearance). Ajusta el ASCII.")

    path, occ, used_clearance, cut = plan_with_retries(S, G, obst, W, H)
    if not path:
        raise RuntimeError("No hay camino con A*. Prueba abrir un poco el circuito o reduce más CLEARANCE.")

    print(f"[OK] Camino encontrado. CLEARANCE={used_clearance:.2f} | cut_corners={cut} | waypoints={len(path)}")

    p = np.array(S, float)
    k = 1

    fig, ax = plt.subplots(figsize=(13,5))
    ax.set_aspect('equal')

    def draw():
        ax.clear()
        ax.plot([0,W,W,0,0],[0,0,H,H,0], 'k', lw=2)
        if obst:
            ox,oy = zip(*obst)
            ax.scatter(np.array(ox)+0.5, np.array(oy)+0.5, c='k', marker='x', s=55, label='Obstáculo')
        px,py = zip(*path)
        ax.plot(np.array(px)+0.5, np.array(py)+0.5, '--', c='tab:blue', lw=1.8, label='Ruta (suavizada)')
        ax.scatter(S[0]+0.5, S[1]+0.5, c='red', s=120, edgecolors='k', zorder=5, label='S')
        ax.scatter(G[0]+0.5, G[1]+0.5, c='lime', marker='X', s=160, edgecolors='k', zorder=5, label='G')
        ax.scatter(p[0]+0.5, p[1]+0.5, c='dodgerblue', s=130, edgecolors='k', zorder=6, label='Agente')
        ax.set_xlim(-0.2, W+0.2); ax.set_ylim(-0.2, H+0.2)
        ax.set_xticks(range(W)); ax.set_yticks(range(H))
        ax.grid(True, alpha=0.20)
        ax.legend(loc='upper right', fontsize=8)
        ax.set_title("A* + movimiento seguro — reintentos automáticos")

    def step(_):
        nonlocal p, k
        draw()
        if k >= len(path): return
        target = np.array(path[k], float)
        v = safe_step(p, target, occ, step_size=STEP_SIZE, clearance=used_clearance)
        if v is None:
            k = min(k+1, len(path)-1)
            return
        p += v
        if np.linalg.norm(p - target) < 0.40:
            k += 1

    anim = FuncAnimation(fig, step, frames=1000, interval=60)
    plt.tight_layout(); plt.show()

if __name__ == "__main__":
    main()
