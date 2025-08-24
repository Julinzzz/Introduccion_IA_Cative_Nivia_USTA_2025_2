# Segundo_punto.py — Commit 2 (paso a paso + BFS corto)
# -----------------------------------------------------------------------------
# Mejoras:
# - Impresión "paso a paso" más clara para lámpara y mascota.
# - En el tesoro cambiamos la política simple por un BFS cortico que encuentra
#   un camino MÁS CORTO (óptimo en número de pasos) en la cuadrícula 3x3.
#   BFS es fácil: cola (queue), visitados y padres para reconstruir el camino.
# -----------------------------------------------------------------------------

from collections import deque

# ===================== 1) LÁMPARA =====================
def acciones_lampara(_estado):
    return ["PRENDER", "APAGAR"]

def transicion_lampara(estado, accion):
    if accion == "PRENDER":
        return "ENCENDIDA"
    elif accion == "APAGAR":
        return "APAGADA"
    return estado

def ejemplo_lampara():
    print("=== LÁMPARA (paso a paso) ===")
    estado = "APAGADA"
    meta    = "ENCENDIDA"
    print(f"Estado inicial: {estado}")
    print("Acciones disponibles:", acciones_lampara(estado))
    estado = transicion_lampara(estado, "PRENDER")
    print(f"Después de PRENDER → {estado}")
    if estado == meta:
        print("¡Meta alcanzada!\n")

# ===================== 2) MASCOTA =====================
def acciones_mascota(_estado):
    return ["DAR_COMIDA", "QUITAR_COMIDA"]

def transicion_mascota(estado, accion):
    if accion == "DAR_COMIDA":
        return "CONTENTA"
    elif accion == "QUITAR_COMIDA":
        return "TRISTE"
    return estado

def ejemplo_mascota():
    print("=== MASCOTA (paso a paso) ===")
    estado = "TRISTE"
    meta    = "CONTENTA"
    print(f"Estado inicial: {estado}")
    print("Acciones disponibles:", acciones_mascota(estado))
    estado = transicion_mascota(estado, "DAR_COMIDA")
    print(f"Después de DAR_COMIDA → {estado}")
    if estado == meta:
        print("¡Meta alcanzada!\n")

# ===================== 3) TESORO (BFS corto) =====================
N = 3
MOVES = [(-1,0,"↑"), (0,1,"→"), (1,0,"↓"), (0,-1,"←")]

def dentro(x, y):
    return 0 <= x < N and 0 <= y < N

def bfs_camino(inicio, meta):
    """
    BFS en cuadrícula sin obstáculos.
    Retorna (camino, acciones) si existe, sino (None, None).
    """
    q = deque([inicio])
    parents = {inicio: (None, None)}  # celda -> (padre, acción)
    visit = {inicio}

    while q:
        x, y = q.popleft()
        if (x, y) == meta:
            # reconstruir
            path, acts = [], []
            cur = meta
            while cur is not None:
                p, a = parents[cur]
                path.append(cur)
                acts.append(a)
                cur = p
            path.reverse()
            acts = [a for a in reversed(acts)][1:]  # quitar None inicial
            return path, acts

        for dx, dy, nombre in MOVES:
            nx, ny = x + dx, y + dy
            if dentro(nx, ny) and (nx, ny) not in visit:
                visit.add((nx, ny))
                parents[(nx, ny)] = ((x, y), nombre)
                q.append((nx, ny))
    return None, None

def ejemplo_tesoro():
    print("=== TESORO (BFS) ===")
    inicio = (0, 0)
    meta   = (2, 2)
    camino, acciones = bfs_camino(inicio, meta)
    if camino is None:
        print("No hay camino.")
    else:
        print("Acciones:", " ".join(acciones))
        print("Camino:", " -> ".join(map(str, camino)))
        print("¡Tesoro encontrado!\n")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    ejemplo_lampara()
    ejemplo_mascota()
    ejemplo_tesoro()
