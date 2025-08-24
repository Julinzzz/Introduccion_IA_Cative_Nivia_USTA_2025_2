# Segundo_punto.py — Commit 1 (versión base)
# -----------------------------------------------------------------------------
# Tres mini‑ejemplos de "espacio de estados y acciones":
# 1) Lámpara (dos estados): ENCENDIDA/APAGADA
# 2) Mascota virtual (dos estados): CONTENTA/TRISTE
# 3) Búsqueda de tesoro en una islita (coordenadas 3x3):
#    política simple: avanzar a la derecha y luego hacia abajo hasta (2,2)
# -----------------------------------------------------------------------------

# ===================== 1) LÁMPARA =====================
def acciones_lampara(_estado):
    # En este ejemplo las dos acciones siempre están disponibles
    return ["PRENDER", "APAGAR"]

def transicion_lampara(estado, accion):
    # Función de transición: devuelve el nuevo estado
    if accion == "PRENDER":
        return "ENCENDIDA"
    elif accion == "APAGAR":
        return "APAGADA"
    return estado  # acción no reconocida → sin cambio

def ejemplo_lampara():
    estados = ["ENCENDIDA", "APAGADA"]
    estado_inicial = "APAGADA"
    estado_meta    = "ENCENDIDA"

    print("=== LÁMPARA ===")
    print(f"Estados posibles: {estados}")
    print(f"Estado inicial: {estado_inicial}  | Meta: {estado_meta}")

    # Elegimos la acción "correcta" para llegar en 1 paso
    accion = "PRENDER"
    estado_nuevo = transicion_lampara(estado_inicial, accion)
    print(f"Acción: {accion} -> Estado: {estado_nuevo}")

    if estado_nuevo == estado_meta:
        print("¡Meta alcanzada!\n")
    else:
        print("No se alcanzó la meta.\n")

# ===================== 2) MASCOTA =====================
def acciones_mascota(_estado):
    # Dos acciones disponibles para el ejemplo
    return ["DAR_COMIDA", "QUITAR_COMIDA"]

def transicion_mascota(estado, accion):
    # Si damos comida → CONTENTA, si quitamos → TRISTE
    if accion == "DAR_COMIDA":
        return "CONTENTA"
    elif accion == "QUITAR_COMIDA":
        return "TRISTE"
    return estado

def ejemplo_mascota():
    estados = ["CONTENTA", "TRISTE"]
    estado_inicial = "TRISTE"
    estado_meta    = "CONTENTA"

    print("=== MASCOTA VIRTUAL ===")
    print(f"Estados posibles: {estados}")
    print(f"Estado inicial: {estado_inicial}  | Meta: {estado_meta}")

    accion = "DAR_COMIDA"
    estado_nuevo = transicion_mascota(estado_inicial, accion)
    print(f"Acción: {accion} -> Estado: {estado_nuevo}")

    if estado_nuevo == estado_meta:
        print("¡Meta alcanzada!\n")
    else:
        print("No se alcanzó la meta.\n")

# ===================== 3) TESORO (3x3) =====================
# Isla con coordenadas de 0 a 2 en ambos ejes. Inicio (0,0), tesoro en (2,2).
N = 3
MOVES = [(0,1,"→"), (1,0,"↓")]  # política simplificada: primero derecha, luego abajo

def dentro_tablero(x, y):
    return 0 <= x < N and 0 <= y < N

def ejemplo_tesoro():
    inicio = (0, 0)
    meta   = (2, 2)

    print("=== BUSCANDO EL TESORO (política simple) ===")
    print(f"Inicio: {inicio} | Meta: {meta}")

    x, y = inicio
    camino = [inicio]
    acciones = []

    # Política muy simple: intenta avanzar en orden (→, luego ↓) hasta la meta
    while (x, y) != meta:
        moved = False
        for dx, dy, nombre in MOVES:
            nx, ny = x + dx, y + dy
            if dentro_tablero(nx, ny) and (nx <= 2 and ny <= 2):
                x, y = nx, ny
                camino.append((x, y))
                acciones.append(nombre)
                moved = True
                break
        if not moved:
            print("No se pudo avanzar (política simple falló).")
            return

    print("Acciones:", " ".join(acciones))
    print("Camino:", " -> ".join(map(str, camino)))
    print("¡Tesoro encontrado!\n")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    ejemplo_lampara()
    ejemplo_mascota()
    ejemplo_tesoro()
