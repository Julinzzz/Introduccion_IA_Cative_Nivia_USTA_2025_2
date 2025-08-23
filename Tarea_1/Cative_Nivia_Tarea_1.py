# =========================================
# Inteligencia Artificial - Tarea práctica
# Conceptos: Estado, Espacio de Estados, Acciones, Recompensa y Ambiente
# =========================================

# ========================
# 1. VARIABLES DE ESTADO
# ========================
estado_robot = {
    "posicion": (0, 0),
    "bateria": 100,
    "objetivo_alcanzado": False
}

print("Estado inicial del robot:", estado_robot)

# ========================
# 2. ESPACIO DE ESTADOS
# ========================
posiciones = [(x, y) for x in range(3) for y in range(3)]
baterias = ["alta", "baja"]

espacio_estados = [(p, b) for p in posiciones for b in baterias]
print("\nTotal de estados posibles:", len(espacio_estados))
print("Ejemplos de estados:", espacio_estados[:5])

# ========================
# 3. ESPACIO DE ACCIONES
# ========================
acciones = ["adelante", "atras", "izquierda", "derecha", "recargar"]
print("\nAcciones posibles:", acciones)

# ========================
# 4. FUNCIÓN DE RECOMPENSA
# ========================
def recompensa(accion, nuevo_estado, paso_actual, total_pasos):
    # 1. Recargar da recompensa pequeña
    if accion == "recargar":
        return 5

    # 2. Objetivo alcanzado
    if nuevo_estado["objetivo_alcanzado"]:
        return 10

    # 3. Castigo por moverse sin batería
    if accion in ["adelante", "atras", "izquierda", "derecha"] and nuevo_estado["bateria"] <= 0:
        return -5

    # 4. Bonus por llegar rápido al objetivo (menos de 5 pasos)
    if nuevo_estado["objetivo_alcanzado"] and paso_actual < 5:
        return 20

    # 5. Castigo por demasiados movimientos sin llegar al objetivo (ejemplo: más de la mitad de los pasos)
    if paso_actual > total_pasos // 2 and not nuevo_estado["objetivo_alcanzado"]:
        return -2

    # 6. Costo normal de moverse
    if accion in ["adelante", "atras", "izquierda", "derecha"]:
        return -1

    return 0

# ========================
# 5. AMBIENTE Y SIMULACIÓN
# ========================
import random

# >>> Paso 1 (ya hecho): costo por movimiento
COSTO_MOVIMIENTO = 10

def mover_robot(estado, accion):
    x, y = estado["posicion"]

    movimientos = ["adelante", "atras", "izquierda", "derecha"]

    # >>> Paso 2: si no hay batería, bloquear movimientos
    if accion in movimientos and estado["bateria"] <= 0:
        # no cambia la posición; se avisa
        print("Intento de moverse sin batería: acción ignorada")
        return estado

    # --- movimientos permitidos ---
    if accion == "adelante":
        x = min(x + 1, 2)
    elif accion == "atras":
        x = max(x - 1, 0)
    elif accion == "derecha":
        y = min(y + 1, 2)
    elif accion == "izquierda":
        y = max(y - 1, 0)
    elif accion == "recargar":
        estado["bateria"] = 100  # recarga completa

    # costo de batería solo al moverse
    if accion in movimientos:
        estado["bateria"] = max(0, estado["bateria"] - COSTO_MOVIMIENTO)

    estado["posicion"] = (x, y)

    if estado["posicion"] == (2, 2):
        estado["objetivo_alcanzado"] = True

    return estado

# ========================
# 6. SIMULACIÓN DEL ROBOT
# ========================
estado = {"posicion": (0, 0), "bateria": 50, "objetivo_alcanzado": False}
recompensa_total = 0
total_pasos = 10

for paso in range(total_pasos):
    accion = random.choice(acciones)
    estado = mover_robot(estado, accion)
    r = recompensa(accion, estado, paso + 1, total_pasos)
    recompensa_total += r
    print(f"Paso {paso+1}: Acción = {accion}, Estado = {estado}, Recompensa = {r}")

print("\nRecompensa total obtenida:", recompensa_total)
