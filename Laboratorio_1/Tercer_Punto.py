# Tercer_punto.py — Commit 1 (versión base 2x2)
# -----------------------------------------------------------------------------
# Objetivo: laberinto mínimo en un mundo 2x2.
# Estados: celdas (x,y) con x,y in {0,1}. Inicio = (0,0), Meta = (0,1)
# Acciones permitidas: -> (derecha) y ↓ (abajo)
# Esta versión:
#   1) Define estados, acciones y una función de movimiento determinista.
#   2) Simula el camino de (0,0) a (0,1) aplicando 'derecha'.
# -----------------------------------------------------------------------------

# Tamaño del mundo (2x2)
W, H = 2, 2

# Acciones: desplazamiento (dx, dy) y nombre
ACTIONS = {
    "derecha": (0, +1),  # (x,y) -> (x, y+1)
    "abajo":   (+1, 0),  # (x,y) -> (x+1, y)
}

def dentro_mapa(x, y):
    """Chequea que (x,y) caiga dentro del mundo 2x2."""
    return 0 <= x < W and 0 <= y < H

def mover(estado, accion):
    """
    Función de transición f(estado, acción) -> nuevo_estado.
    - No hay obstáculos en esta versión.
    - Si la acción saca del mapa, se queda en el mismo estado.
    """
    dx, dy = ACTIONS[accion]
    nx, ny = estado[0] + dx, estado[1] + dy
    return (nx, ny) if dentro_mapa(nx, ny) else estado

def simular_basico():
    inicio = (0, 0)
    meta   = (0, 1)

    print("=== LABERINTO 2x2 — versión base ===")
    print(f"Inicio: {inicio} | Meta: {meta}")
    print("Acciones disponibles:", list(ACTIONS.keys()))

    # Camino obvio: una vez a la derecha
    estado = inicio
    print(f"Estado actual: {estado}")
    estado = mover(estado, "derecha")
    print(f"Aplicar 'derecha' -> {estado}")

    print("¡Meta alcanzada!\n" if estado == meta else "No se alcanzó la meta.\n")

if __name__ == "__main__":
    simular_basico()
