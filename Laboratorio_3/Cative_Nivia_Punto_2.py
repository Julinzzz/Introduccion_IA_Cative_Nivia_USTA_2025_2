# tsp_ga.py
import numpy as np
import random
import matplotlib.pyplot as plt

# ==========================
# Utilidades
# ==========================
def euclidean(a, b):
    return np.hypot(a[0]-b[0], a[1]-b[1])

def route_length(route, cities):
    return sum(euclidean(cities[route[i]], cities[route[(i+1) % len(route)]])
               for i in range(len(route)))

# ==========================
# Operadores Genéticos
# ==========================
def tournament_selection(pop, fitness, k=3):
    """Selecciona el mejor de k individuos al azar (minimiza distancia)."""
    idxs = np.random.choice(len(pop), size=k, replace=False)
    best = min(idxs, key=lambda i: fitness[i])
    return pop[best].copy()

def ordered_crossover_OX(parent1, parent2):
    """OX: mantiene segmento de p1 y completa en orden relativo de p2."""
    n = len(parent1)
    a, b = sorted(random.sample(range(n), 2))
    child = [-1]*n
    # Copia segmento de p1
    child[a:b+1] = parent1[a:b+1]
    # Rellena con el orden de p2
    p2_idx = 0
    for i in range(n):
        if child[i] == -1:
            while parent2[p2_idx] in child:
                p2_idx += 1
            child[i] = parent2[p2_idx]
    return child

def swap_mutation(route, p=0.2):
    """Con probabilidad p, intercambia dos posiciones."""
    r = route.copy()
    if random.random() < p:
        i, j = random.sample(range(len(r)), 2)
        r[i], r[j] = r[j], r[i]
    return r

# ==========================
# Algoritmo Genético TSP
# ==========================
def genetic_tsp(cities, pop_size=120, generations=600,
                tournament_k=3, crossover_rate=0.95, mutation_rate=0.25,
                elitism=2, seed=42):
    random.seed(seed); np.random.seed(seed)

    n = len(cities)
    # Población inicial: permutaciones aleatorias
    pop = [random.sample(range(n), n) for _ in range(pop_size)]

    def eval_pop(pop):
        fit = np.array([route_length(ind, cities) for ind in pop])
        return fit

    fitness = eval_pop(pop)
    best_idx = np.argmin(fitness)
    best = pop[best_idx].copy()
    best_fit = fitness[best_idx]

    history = [best_fit]

    for gen in range(generations):
        # Elitismo
        elites_idx = np.argsort(fitness)[:elitism]
        new_pop = [pop[i].copy() for i in elites_idx]

        # Resto por reproducción
        while len(new_pop) < pop_size:
            p1 = tournament_selection(pop, fitness, k=tournament_k)
            p2 = tournament_selection(pop, fitness, k=tournament_k)

            if random.random() < crossover_rate:
                c1 = ordered_crossover_OX(p1, p2)
                c2 = ordered_crossover_OX(p2, p1)
            else:
                c1, c2 = p1.copy(), p2.copy()

            c1 = swap_mutation(c1, mutation_rate)
            c2 = swap_mutation(c2, mutation_rate)

            new_pop.extend([c1, c2])

        pop = new_pop[:pop_size]
        fitness = eval_pop(pop)

        # Actualiza mejor
        cur_idx = np.argmin(fitness)
        cur_best = pop[cur_idx].copy()
        cur_fit = fitness[cur_idx]
        if cur_fit < best_fit:
            best_fit = cur_fit
            best = cur_best.copy()

        history.append(best_fit)

    return best, best_fit, history

# ==========================
# Ejecución y visualización
# ==========================
if __name__ == "__main__":
    # Genera 10 ciudades en [0,1]x[0,1]
    np.random.seed(1)
    cities = np.random.rand(10, 2)

    best_route, best_len, history = genetic_tsp(
        cities,
        pop_size=150,
        generations=800,
        tournament_k=4,
        crossover_rate=0.95,
        mutation_rate=0.25,
        elitism=2,
        seed=7
    )

    print("Mejor longitud encontrada:", round(best_len, 4))
    print("Ruta (orden de visita, 0-index):", best_route)

    # Plot ruta
    route_xy = cities[best_route]
    route_xy = np.vstack([route_xy, route_xy[0]])  # cerrar ciclo

    plt.figure(figsize=(6,6))
    plt.plot(route_xy[:,0], route_xy[:,1], '-o')
    for i,(x,y) in enumerate(cities):
        plt.text(x+0.01, y+0.01, str(i))
    plt.title(f"Mejor ruta GA (dist = {best_len:.3f})")
    plt.axis('equal'); plt.grid(True)
    plt.show()

    # Plot convergencia
    plt.figure()
    plt.plot(history)
    plt.xlabel("Generación")
    plt.ylabel("Mejor distancia")
    plt.title("Convergencia del GA")
    plt.grid(True)
    plt.show()
