# Tercer_punto.py — Commit 2 (2x2 con obstáculos + BFS)
# -----------------------------------------------------------------------------
# Mejoras:
# 1) Agregamos obstáculo(s) como conjunto de celdas bloqueadas.
# 2) Implementamos BFS para hallar la ruta más corta (si existe).
# 3) Probamos el caso con obstáculo en (0,1) (la meta original) y
#    mostramos que el problema queda bloqueado; luego probamos otra meta.
# -----------------------------------------------------------------------------

from collections import deque

W, H = 2, 2
ACTIONS = {"derecha": (0, +1), "abajo": (+1, 0)}

def dentro_mapa(x, y): return 0 <= x < W and 0 <= y < H

def vecinos(celda, obstaculos):
    """Genera vecinos válidos (aplicando acciones y filtrando obstáculos)."""
    x, y = celda
    for nombre, (dx, dy) in ACTIONS.items():
        nx, ny = x + dx, y + dy
        if dentro_mapa(nx, ny) and (nx, ny) not in obstaculos:
            yield (nx, ny), nombre

def bfs_camino(inicio, meta, obstaculos):
    """
    BFS en el grafo implícito del grid 2x2.
    Retorna (camino, acciones) o (None, None) si no hay ruta.
    """
    q = deque([inicio])
    padres = {inicio: (None, None)}  # hijo -> (padre, acción)
    visit  = {inicio}

    while q:
        u = q.popleft()
        if u == meta:
            # reconstruir
            path, acts = [], []
            cur = u
            while cur is not None:
                p, a = padres[cur]
                path.append(cur); acts.append(a)
                cur = p
            path.reverse()
            acts = [a for a in reversed(acts)][1:]  # quita None
            return path, acts

        for v, a in vecinos(u, obstaculos):
            if v not in visit:
                visit.add(v)
                padres[v] = (u, a)
                q.append(v)

    return None, None

def probar():
    inicio = (0, 0)

    print("=== LABERINTO 2x2 — obstáculos + BFS ===")
    print("Acciones: derecha, abajo")

    # Caso A: meta (0,1) y obstáculo en (0,1) → no hay ruta
    meta = (0, 1)
    obst = {(0, 1)}  # bloqueamos precisamente la meta
    print(f"\nCaso A: inicio={inicio}, meta={meta}, obstaculos={obst}")
    camino, acciones = bfs_camino(inicio, meta, obst)
    if camino is None:
        print("Resultado: NO hay camino (la meta está bloqueada).")

    # Caso B: probamos otra meta alcanzable (1,1) con el mismo obstáculo
    meta_b = (1, 1)
    print(f"\nCaso B: inicio={inicio}, meta={meta_b}, obstaculos={obst}")
    camino, acciones = bfs_camino(inicio, meta_b, obst)
    if camino is None:
        print("Resultado: NO hay camino.")
    else:
        print("Acciones:", " -> ".join(acciones))
        print("Camino:", " -> ".join(map(str, camino)))
        print("¡Meta alcanzada!")

if __name__ == "__main__":
    probar()
