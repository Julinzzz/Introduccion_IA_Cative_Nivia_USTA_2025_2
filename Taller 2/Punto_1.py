"""
Primer Punto - Evolución Pokemon

Este script implementa un algoritmo genético (GA) que evoluciona "Pokémon"
(representados por 5 genes: ataque, defensa, velocidad, vida, tipo) para
maximizar una función de fitness. El código es didáctico, autocontenido y
reproducible.

"""
from __future__ import annotations
import json, csv, random, math, statistics, os
from dataclasses import dataclass, asdict
from typing import List, Tuple
import matplotlib.pyplot as plt  # Se permite matplotlib (no seaborn)

# ------------------ Configuración (puedes editar) ------------------
SEED = 42                 # Semilla para reproducibilidad
POBLACION = 80            # Tamaño de población
GENERACIONES = 60         # Número de generaciones
ELITISMO = 4              # Nº de mejores individuos que pasan directamente
TAM_TORNEO = 3            # Selección por torneo
PROB_MUTACION = 0.20      # Probabilidad de mutar cada gen continuo
SIGMA_MUT = 0.10          # Desviación estándar de la mutación gaussiana
PROB_MUT_TIPO = 0.10      # Probabilidad de mutar el tipo (gen categórico)

# Pesos de la función de fitness (suman 1.0 idealmente)
W_ATAQUE   = 0.30
W_DEFENSA  = 0.20
W_VELOCIDAD= 0.25
W_VIDA     = 0.25

TIPOS = ["fuego", "agua", "planta", "electrico", "roca", "hielo", "lucha", "fantasma"]

# Multiplicador por tipo (puedes ajustar para "metagame" distinto)
BONO_TIPO = {
    "fuego": 1.10,
    "agua": 1.05,
    "planta": 1.03,
    "electrico": 1.07,
    "roca": 1.02,
    "hielo": 1.03,
    "lucha": 1.04,
    "fantasma": 1.01,
}

random.seed(SEED)

# ------------------ Representación ------------------
@dataclass
class Pokemon:
    ataque: float     # [0,1]
    defensa: float    # [0,1]
    velocidad: float  # [0,1]
    vida: float       # [0,1]
    tipo: str         # categórico

    def clip(self) -> "Pokemon":
        """Satura genes continuos al rango [0,1]."""
        self.ataque   = max(0.0, min(1.0, self.ataque))
        self.defensa  = max(0.0, min(1.0, self.defensa))
        self.velocidad= max(0.0, min(1.0, self.velocidad))
        self.vida     = max(0.0, min(1.0, self.vida))
        return self

# ------------------ Fitness ------------------
def evaluar(p: Pokemon) -> float:
    """
    Fitness: combinación ponderada + bono por tipo + sinergias suaves.
    Mayor es mejor.
    """
    base = (p.ataque * W_ATAQUE +
            p.defensa * W_DEFENSA +
            p.velocidad * W_VELOCIDAD +
            p.vida * W_VIDA)

    # Bono por tipo
    mult = BONO_TIPO.get(p.tipo, 1.0)

    # Pequeñas sinergias/penalizaciones para hacerlo más interesante
    if p.ataque > 0.7 and p.velocidad > 0.7:
        mult *= 1.03  # atacante rápido
    if p.defensa > 0.7 and p.vida > 0.7:
        mult *= 1.02  # tanque resiliente
    if p.vida < 0.25:
        mult *= 0.97  # frágil

    return base * mult

# ------------------ Operadores GA ------------------
def inicializar(n: int) -> List[Pokemon]:
    poblacion = []
    for _ in range(n):
        p = Pokemon(
            ataque=random.random(),
            defensa=random.random(),
            velocidad=random.random(),
            vida=random.random(),
            tipo=random.choice(TIPOS),
        )
        poblacion.append(p)
    return poblacion

def torneo(pop: List[Pokemon], k: int) -> Pokemon:
    candidatos = random.sample(pop, k)
    return max(candidatos, key=evaluar)

def crossover(a: Pokemon, b: Pokemon) -> Pokemon:
    """
    Cruce blend: mezcla aleatoria de los genes continuos; tipo tomado de un padre.
    """
    beta = random.random()
    hijo = Pokemon(
        ataque   = a.ataque   * beta + b.ataque   * (1 - beta),
        defensa  = a.defensa  * beta + b.defensa  * (1 - beta),
        velocidad= a.velocidad* beta + b.velocidad* (1 - beta),
        vida     = a.vida     * beta + b.vida     * (1 - beta),
        tipo     = random.choice([a.tipo, b.tipo])
    )
    return hijo.clip()

def mutar(p: Pokemon) -> Pokemon:
    """
    Mutación gaussiana independiente en cada gen continuo con probabilidad PROB_MUTACION.
    Posible cambio de tipo con PROB_MUT_TIPO.
    """
    if random.random() < PROB_MUTACION:
        p.ataque += random.gauss(0, SIGMA_MUT)
    if random.random() < PROB_MUTACION:
        p.defensa += random.gauss(0, SIGMA_MUT)
    if random.random() < PROB_MUTACION:
        p.velocidad += random.gauss(0, SIGMA_MUT)
    if random.random() < PROB_MUTACION:
        p.vida += random.gauss(0, SIGMA_MUT)

    if random.random() < PROB_MUT_TIPO:
        p.tipo = random.choice(TIPOS)

    return p.clip()

# ------------------ Bucle principal ------------------
def evolucionar():
    pop = inicializar(POBLACION)
    historial_mejor, historial_prom = [], []

    for gen in range(GENERACIONES):
        # Métricas actuales
        fits = [evaluar(x) for x in pop]
        mejor = pop[fits.index(max(fits))]
        prom = statistics.mean(fits)
        historial_mejor.append(max(fits))
        historial_prom.append(prom)

        # Impresión de progreso cada 5 generaciones
        if gen % 5 == 0 or gen == GENERACIONES-1:
            print(f"Gen {gen:3d} | mejor={max(fits):.4f} | promedio={prom:.4f} | tipo={mejor.tipo}")

        # Elitismo
        elite = sorted(pop, key=evaluar, reverse=True)[:ELITISMO]

        # Nueva población
        nueva = elite.copy()
        while len(nueva) < POBLACION:
            p1 = torneo(pop, TAM_TORNEO)
            p2 = torneo(pop, TAM_TORNEO)
            hijo = crossover(p1, p2)
            hijo = mutar(hijo)
            nueva.append(hijo)

        pop = nueva

    # Cierre: escoger mejor final
    fits = [evaluar(x) for x in pop]
    mejor = pop[fits.index(max(fits))]
    return mejor, historial_mejor, historial_prom

def Grafica_fitness(mejor: Pokemon, hist_mejor: List[float], hist_prom: List[float]):

    # Curva de aprendizaje
    plt.figure()
    plt.plot(hist_mejor, label="Mejor por generación")
    plt.plot(hist_prom, label="Promedio por generación")
    plt.xlabel("Generación")
    plt.ylabel("Fitness")
    plt.title("Evolución del fitness (GA Pokémon)")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

def main():
    mejor, h_mejor, h_prom = evolucionar()
    Grafica_fitness(mejor, h_mejor, h_prom)
    print("\nMejor Pokémon encontrado:")
    print(json.dumps({**asdict(mejor), "fitness": evaluar(mejor)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
