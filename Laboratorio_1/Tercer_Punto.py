# Tercer_punto.py — Commit 3 (versión final 3x3)
# -----------------------------------------------------------------------------
# Consejos aplicados del enunciado:
# - Definir estados posibles (grid 3x3).
# - Listar acciones y crear tabla de transición (si A y acción X -> entonces B).
# - Usar diccionarios para recompensas (por ejemplo, -1 por paso y +10 al llegar).
# - Probar con valores fijos antes de hacerlo dinámico.
# Incluye:
#   * Obstáculos configurables.
#   * BFS para encontrar camino mínimo.
#   * Métricas: nodos expandidos y longitud de camino.
# -----------------------------------------------------------------------------

from collections import deque

# ---------- Configuración del mundo ----------
W, H = 3, 3                          # mundo 3x3
ACCIONES = {                         # desplazamientos
    "↑": (-1, 0),
    "→": (0, +1),
    "↓": (+1, 0),
    "←": (0, -1),
}
OBSTACULOS = {(1, 1)}                # ejemplo: bloqueamos el centro
INICIO = (0, 0)
META   = (2, 2)

# ---------- Utilidades ----------
def dentro(x, y): return 0 <= x < W and 0 <= y < H

def construir_transiciones(obstaculos):
    """
    Tabla de transición T[(x,y)][accion] = (nx, ny) o None si no es posible.
    (Sirve para "ver" el espacio de estados y acciones de forma explícita.)
    """
    T = {}
    for x in range(W):
        for y in range(H):
            s = (x, y)
            T[s] = {}
            if s in obstaculos:      # celdas bloqueadas no tienen sucesores
                continue
            for a, (dx, dy) in ACCIONES.items():
                nx, ny = x + dx, y + dy
                T[s][a] = (nx, ny) if dentro(nx, ny) and (nx, ny) not in obstaculos else None
    return T

def recompensas(meta):
    """
    Recompensa simple: -1 por paso y +10 al llegar a la meta.
    (Mapa: (estado, accion, nuevo_estado) -> recompensa)
    """
    R = {}
    for x in range(W):
        for y in range(H):
            s = (x, y)
            for a, (dx, dy) in ACCIONES.items():
                nx, ny = x + dx, y + dy
                if not dentro(nx, ny) or (nx, ny) in OBSTACULOS:
                    continue
                ns = (nx, ny)
                R[(s, a, ns)] = 10 if ns == meta else -1
    return R

# ---------- Búsqueda ----------
def vecinos(s, T):
    """Genera (nuevo_estado, acción) usando la tabla de transición T."""
    if s not in T: return
    for a, ns in T[s].items():
        if ns is not None:
            yield ns, a

def bfs(inicio, meta, T):
    """BFS con reconstrucción y métricas."""
    q = deque([inicio])
    padres = {inicio: (None, None)}
    visit  = {inicio}
    expandidos = 0

    while q:
        u = q.popleft()
        expandidos += 1
        if u == meta:
            # reconstrucción
            path, acts = [], []
            cur = u
            while cur is not None:
                p, a = padres[cur]
                path.append(cur); acts.append(a)
                cur = p
            path.reverse()
            acts = [a for a in reversed(acts)][1:]
            return path, acts, {"expandidos": expandidos, "long_camino": len(acts)}

        for v, a in vecinos(u, T):
            if v not in visit:
                visit.add(v)
                padres[v] = (u, a)
                q.append(v)

    return None, None, {"expandidos": expandidos, "long_camino": None}

# ---------- Demo ----------
def demo():
    print("=== LABERINTO 3x3 — versión final ===")
    print(f"Tamaño: {W}x{H} | Inicio: {INICIO} | Meta: {META} | Obstáculos: {OBSTACULOS}")

    T = construir_transiciones(OBSTACULOS)
    R = recompensas(META)  # no usamos R en BFS, solo lo mostramos como ejemplo

    path, acts, stats = bfs(INICIO, META, T)
    if path is None:
        print("No hay camino (obstáculos bloquean la meta o el inicio).")
        return

    print("Acciones:", " ".join(acts))
    print("Camino :", " -> ".join(map(str, path)))
    print(f"Métricas: {stats['expandidos']} nodos expandidos | longitud camino = {stats['long_camino']}")
    print(f"Ejemplo de recompensas (primeros 5): {list(R.items())[:5]}")

if __name__ == "__main__":
    demo()
