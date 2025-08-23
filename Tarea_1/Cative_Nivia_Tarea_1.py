# =========================================
# Inteligencia Artificial - Tarea práctica
# Conceptos: Estado, Espacio de Estados, Acciones, Recompensa y Ambiente
# =========================================

# ========================
# 1. VARIABLES DE ESTADO
# ========================
# Se define el estado de un robot: posición (x, y), batería y objetivo alcanzado

estado_robot = {
    "posicion": (0, 0),
    "bateria": 100,
    "objetivo_alcanzado": False
}

print("Estado inicial del robot:", estado_robot)

# ========================
# 2. ESPACIO DE ESTADOS
# ========================
# Se define todas las combinaciones posibles de posición y batería

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
def recompensa(accion, nuevo_estado):
    if accion == "recargar":
        return 5
    elif nuevo_estado["objetivo_alcanzado"]:
        return 10
    elif accion in ["adelante", "atras", "izquierda", "derecha"]:
        return -1  # Costo de moverse
    else:
        return 0

# ========================
# 5. AMBIENTE Y SIMULACIÓN
# ========================
import random

def mover_robot(estado, accion):
    x, y = estado["posicion"]
    if accion == "adelante":
        x = min(x + 1, 2)
    elif accion == "atras":
        x = max(x - 1, 0)
    elif accion == "derecha":
        y = min(y + 1, 2)
    elif accion == "izquierda":
        y = max(y - 1, 0)
    elif accion == "recargar":
        estado["bateria"] = 100

    estado["posicion"] = (x, y)

    # Si llega a (2, 2), objetivo alcanzado
    if estado["posicion"] == (2, 2):
        estado["objetivo_alcanzado"] = True

    return estado

# ========================
# 6. SIMULACIÓN DEL ROBOT
# ========================
estado = {"posicion": (0, 0), "bateria": 50, "objetivo_alcanzado": False}
recompensa_total = 0

for paso in range(10):
    accion = random.choice(acciones)
    estado = mover_robot(estado, accion)
    r = recompensa(accion, estado)
    recompensa_total += r

    print(f"Paso {paso+1}: Acción = {accion}, Estado = {estado}, Recompensa = {r}")

print("\nRecompensa total obtenida:", recompensa_total)