import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# ============================
# Definición de ciudades
# ============================
ciudades = {
    'A': (0, 0),
    'B': (1, 5),
    'C': (2, 3),
    'D': (5, 2),
    'E': (6, 6),
    'F': (7, 1),
    'G': (8, 4),
    'H': (9, 9)
}

nombres = list(ciudades.keys())
coords = list(ciudades.values())

# ============================
# Funciones auxiliares
# ============================
def distancia(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])

def distancia_total(ruta):
    dist = 0.0
    for i in range(len(ruta) - 1):
        dist += distancia(ciudades[ruta[i]], ciudades[ruta[i + 1]])
    dist += distancia(ciudades[ruta[-1]], ciudades[ruta[0]])  # regreso al inicio
    return dist

def fitness(ruta):
    return 1 / (distancia_total(ruta) + 1e-9)

# ============================
# Operadores genéticos
# ============================
def seleccion(poblacion, distancias):
    torneo = random.sample(list(zip(poblacion, distancias)), 3)
    torneo.sort(key=lambda x: x[1])  # menor distancia
    return torneo[0][0]

def cruce_ordenado(padre1, padre2):
    n = len(padre1)
    a, b = sorted(random.sample(range(n), 2))
    hijo = [None] * n
    hijo[a:b] = padre1[a:b]

    pos = b
    for ciudad in padre2:
        if ciudad not in hijo:
            if pos >= n:
                pos = 0
            hijo[pos] = ciudad
            pos += 1
    return hijo

def mutacion(ruta, tasa=0.2):
    if random.random() < tasa:
        i, j = random.sample(range(len(ruta)), 2)
        ruta[i], ruta[j] = ruta[j], ruta[i]
    return ruta

# ============================
# Algoritmo Genético
# ============================
def algoritmo_genetico(generaciones=200, poblacion_size=50, tasa_mutacion=0.2):
    poblacion = [random.sample(nombres, len(nombres)) for _ in range(poblacion_size)]
    mejor_ruta = None
    mejor_distancia = float("inf")
    historial = []

    for _ in range(generaciones):
        distancias = [distancia_total(r) for r in poblacion]
        gen_mejor = min(distancias)
        if gen_mejor < mejor_distancia:
            mejor_distancia = gen_mejor
            mejor_ruta = poblacion[np.argmin(distancias)].copy()
        historial.append(mejor_distancia)

        nueva_poblacion = []
        for _ in range(poblacion_size):
            padre1 = seleccion(poblacion, distancias)
            padre2 = seleccion(poblacion, distancias)
            hijo = cruce_ordenado(padre1, padre2)
            hijo = mutacion(hijo, tasa_mutacion)
            nueva_poblacion.append(hijo)
        poblacion = nueva_poblacion

    return mejor_ruta, mejor_distancia, historial

# ============================
# Visualización
# ============================
def graficar_ruta(ruta, dist):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.axis("equal")
    ax.axis("off")

    for i in range(len(ruta)):
        a = ciudades[ruta[i]]
        b = ciudades[ruta[(i + 1) % len(ruta)]]
        arrow = FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=12,
                                lw=2, color="red", shrinkA=5, shrinkB=5)
        ax.add_patch(arrow)

    for nombre, (x, y) in ciudades.items():
        ax.scatter(x, y, s=200, facecolors="white", edgecolors="black", linewidths=1.5)
        ax.text(x, y, nombre, fontsize=12, ha="center", va="center", weight="bold")

    ax.text(0.05, 0.95, f"Mejor ruta: {ruta}\nDistancia: {dist:.2f}",
            transform=ax.transAxes, fontsize=10,
            verticalalignment="top", bbox=dict(facecolor="white", alpha=0.8))
    plt.title("Problema del Agente Viajero - Mejor Ruta")
    plt.show()

def graficar_convergencia(historial):
    plt.plot(historial, lw=2)
    plt.xlabel("Generaciones")
    plt.ylabel("Mejor distancia encontrada")
    plt.title("Convergencia del Algoritmo Genético")
    plt.grid(True)
    plt.show()

# ============================
# Main
# ============================
if __name__ == "__main__":
    mejor_ruta, mejor_distancia, historial = algoritmo_genetico()
    print("Mejor ruta encontrada:", mejor_ruta)
    print("Distancia total:", mejor_distancia)

    graficar_ruta(mejor_ruta, mejor_distancia)
    graficar_convergencia(historial)
