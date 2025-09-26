import math
import random
from typing import Dict, List, Tuple

# ================== Datos del problema ==================
ciudades: Dict[str, Tuple[int, int]] = {
    'A': (0, 0),
    'B': (1, 5),
    'C': (2, 3),
    'D': (5, 2),
    'E': (6, 6),
    'F': (7, 1),
    'G': (8, 4),
    'H': (9, 9),
}

# ------------------ Utilidades ------------------
def distancia_euclidiana(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# ================== Funciones pedidas ==================
def distancia_ruta(ruta: List[str]) -> float:
    """
    Calcula la distancia total de una ruta cerrada: ciudad_0 -> ... -> ciudad_n-1 -> ciudad_0.
    """
    total = 0.0
    n = len(ruta)
    for i in range(n):
        c1 = ruta[i]
        c2 = ruta[(i + 1) % n]  # regresa al inicio al final
        total += distancia_euclidiana(ciudades[c1], ciudades[c2])
    return total


def crear_poblacion_inicial(tam_poblacion: int) -> List[List[str]]:
    """
    Crea población inicial con permutaciones aleatorias de las ciudades.
    """
    base = list(ciudades.keys())
    poblacion = []
    for _ in range(tam_poblacion):
        individuo = base[:]
        random.shuffle(individuo)
        poblacion.append(individuo)
    return poblacion


def seleccion(poblacion: List[List[str]], k_torneo: int = 3) -> List[str]:
    """
    Selección por torneo: toma k individuos al azar y devuelve el mejor (menor distancia).
    """
    candidatos = random.sample(poblacion, k_torneo)
    ganador = min(candidatos, key=distancia_ruta)
    return ganador[:]


def cruce(padre1: List[str], padre2: List[str]) -> Tuple[List[str], List[str]]:
    """
    Cruce OX (Ordered Crossover).
    Devuelve dos hijos respetando el orden relativo.
    """
    n = len(padre1)
    a, b = sorted(random.sample(range(n), 2))
    # Segmentos heredados del primer padre
    hijo1 = [None] * n
    hijo1[a:b+1] = padre1[a:b+1]

    # Completar con el orden del segundo padre
    pos = (b + 1) % n
    for ciudad in padre2:
        if ciudad not in hijo1:
            hijo1[pos] = ciudad
            pos = (pos + 1) % n

    # Hijo 2 (simétrico)
    hijo2 = [None] * n
    hijo2[a:b+1] = padre2[a:b+1]
    pos = (b + 1) % n
    for ciudad in padre1:
        if ciudad not in hijo2:
            hijo2[pos] = ciudad
            pos = (pos + 1) % n

    return hijo1, hijo2


def mutacion(ruta: List[str], tasa_mutacion: float) -> None:
    """
    Mutación por intercambio (swap) con probabilidad 'tasa_mutacion' por individuo.
    Aplica como máximo un intercambio por llamada (suficiente en GA clásico).
    """
    if random.random() < tasa_mutacion:
        i, j = random.sample(range(len(ruta)), 2)
        ruta[i], ruta[j] = ruta[j], ruta[i]


# ================== GA principal ==================
def ga_tsp(
    tam_poblacion: int = 100,
    generaciones: int = 400,
    tasa_mutacion: float = 0.15,
    prob_cruce: float = 0.9,
    k_torneo: int = 3,
    elitismo: int = 2,
    semilla: int = 42,
) -> Tuple[List[str], float]:
    """
    Ejecuta el algoritmo genético y retorna (mejor_ruta, distancia).
    """
    random.seed(semilla)

    poblacion = crear_poblacion_inicial(tam_poblacion)
    mejor = min(poblacion, key=distancia_ruta)
    mejor_dist = distancia_ruta(mejor)

    for gen in range(1, generaciones + 1):
        # Elitismo: conservar los mejores 'elitismo' individuos
        poblacion_ordenada = sorted(poblacion, key=distancia_ruta)
        nueva_poblacion = [ind[:] for ind in poblacion_ordenada[:elitismo]]

        # Reproducción
        while len(nueva_poblacion) < tam_poblacion:
            p1 = seleccion(poblacion, k_torneo)
            p2 = seleccion(poblacion, k_torneo)

            if random.random() < prob_cruce:
                h1, h2 = cruce(p1, p2)
            else:
                h1, h2 = p1[:], p2[:]

            mutacion(h1, tasa_mutacion)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(h1)

            if len(nueva_poblacion) < tam_poblacion:
                mutacion(h2, tasa_mutacion)
                nueva_poblacion.append(h2)

        poblacion = nueva_poblacion

        # Actualizar mejor global
        candidato = min(poblacion, key=distancia_ruta)
        cand_dist = distancia_ruta(candidato)
        if cand_dist < mejor_dist:
            mejor, mejor_dist = candidato[:], cand_dist

        # (Opcional) mostrar progreso cada cierto número de generaciones
        if gen % max(1, generaciones // 10) == 0:
            print(f"Gen {gen:4d} | mejor distancia: {mejor_dist:.4f} | ruta: {'-'.join(mejor)}")

    return mejor, mejor_dist


# ================== Ejecución directa ==================
if __name__ == "__main__":
    ruta, dist = ga_tsp(
        tam_poblacion=120,
        generaciones=500,
        tasa_mutacion=0.12,
        prob_cruce=0.95,
        k_torneo=3,
        elitismo=2,
        semilla=7,
    )
    print("\n== Resultado final ==")
    print("Mejor ruta encontrada:", " -> ".join(ruta), "->", ruta[0])
    print(f"Distancia total: {dist:.4f}")
