# Segundo_punto.py — Commit 3 (versión final)
# -----------------------------------------------------------------------------
# Contenido:
# 1) LÁMPARA: estados y acciones, transición, simulación y verificación de meta.
# 2) MASCOTA: igual que lámpara pero con otra semántica; añadimos "recompensa" simple.
# 3) TESORO: BFS en cuadrícula 3x3 con reconstrucción de ruta, métricas y comentarios.
# Objetivo docente: visualizar "espacio de estados", "espacio de acciones" y "estado meta".
# -----------------------------------------------------------------------------

from collections import deque

# ===================== 1) LÁMPARA =====================
def acciones_lampara(_estado):
    """Acciones siempre disponibles en este ejemplo."""
    return ["PRENDER", "APAGAR"]

def transicion_lampara(estado, accion):
    """Función de transición f(estado, acción) -> nuevo_estado."""
    if accion == "PRENDER":
        return "ENCENDIDA"
    if accion == "APAGAR":
        return "APAGADA"
    return estado  # acción inválida → sin cambio

def ejemplo_lampara():
    estados = ["ENCENDIDA", "APAGADA"]
    estado_inicial = "APAGADA"
    estado_meta    = "ENCENDIDA"

    print("=== LÁMPARA (espacio de estados y acciones) ===")
    print(f"Estados: {estados}")
    print(f"Inicial: {estado_inicial} | Meta: {estado_meta}")
    print("Acciones disponibles:", acciones_lampara(estado_inicial))

    accion = "PRENDER"
    estado = transicion_lampara(estado_inicial, accion)
    print(f"Aplicar {accion} → {estado}")
    print("¡Meta alcanzada!\n" if estado == estado_meta else "No se alcanzó la meta.\n")

# ===================== 2) MASCOTA =====================
def acciones_mascota(_estado):
    return ["DAR_COMIDA", "QUITAR_COMIDA"]

def transicion_mascota(estado, accion):
    if accion == "DAR_COMIDA":
        return "CONTENTA"
    if accion == "QUITAR_COMIDA":
        return "TRISTE"
    return estado

def recompensa_mascota(estado, accion, nuevo_estado):
    """
    Recompensa muy simple:
      +1 si pasamos a CONTENTA,
       0 en otro caso. (Solo ilustrativo; no hay aprendizaje aquí)
    """
    return 1 if nuevo_estado == "CONTENTA" else 0

def ejemplo_mascota():
    estados = ["CONTENTA", "TRISTE"]
    estado_inicial = "TRISTE"
    estado_meta    = "CONTENTA"

    print("=== MASCOTA (recompensa & ambiente) ===")
    print(f"Estados: {estados}")
    print(f"Inicial: {estado_inicial} | Meta: {estado_meta}")

    accion = "DAR_COMIDA"
    nuevo_estado = transicion_mascota(estado_inicial, accion)
    r = recompensa_mascota(estado_inicial, accion, nuevo_estado)

    print(f"Acción: {accion} → Estado: {nuevo_estado} | Recompensa: {r}")
    print("¡Meta alcanzada!\n" if nuevo_estado == estado_meta else "No se alcanzó la meta.\n")

# ===================== 3) TESORO (BFS con métricas) =====================
N = 3
MOVES = [(-1,0,"↑"), (0,1,"→"), (1,0,"↓"), (0,-1,"←")]

def dentro(x, y):
    return 0 <= x < N and 0 <= y < N

def bfs_camino(inicio, meta):
    """
    BFS en cuadrícula sin obstáculos.
    Retorna (camino, acciones, estadisticas).
    'estadisticas' incluye: nodos_expandidos y longitud_de_camino.
    """
    q = deque([inicio])
    parents = {inicio: (None, None)}  # (padre, acción)
    visit = {inicio}
    expandidos = 0

    while q:
        x, y = q.popleft()
        expandidos += 1

        if (x, y) == meta:
            # reconstrucción
            path, acts = [], []
            cur = meta
            while cur is not None:
                p, a = parents[cur]
                path.append(cur)
                acts.append(a)
                cur = p
            path.reverse()
            acts = [a for a in reversed(acts)][1:]
            stats = {"nodos_expandidos": expandidos, "longitud_de_camino": len(acts)}
            return path, acts, stats

        for dx, dy, nombre in MOVES:
            nx, ny = x + dx, y + dy
            if dentro(nx, ny) and (nx, ny) not in visit:
                visit.add((nx, ny))
                parents[(nx, ny)] = ((x, y), nombre)
                q.append((nx, ny))

    return None, None, {"nodos_expandidos": expandidos, "longitud_de_camino": None}

def ejemplo_tesoro():
    inicio = (0, 0)
    meta   = (2, 2)
    print("=== TESORO (BFS con métricas) ===")
    print(f"Inicio: {inicio}  |  Meta: {meta}")

    camino, acciones, stats = bfs_camino(inicio, meta)
    if camino is None:
        print("No hay camino.")
        return

    print("Acciones:", " ".join(acciones))
    print("Camino:", " -> ".join(map(str, camino)))
    print(f"Métricas: {stats['nodos_expandidos']} nodos expandidos | "
          f"longitud de camino = {stats['longitud_de_camino']}\n")
    print("¡Tesoro encontrado!\n")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    ejemplo_lampara()
    ejemplo_mascota()
    ejemplo_tesoro()