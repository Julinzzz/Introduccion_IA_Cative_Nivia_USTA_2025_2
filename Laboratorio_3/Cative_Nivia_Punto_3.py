# -*- coding: utf-8 -*-
"""
Tercer Punto – Optimización de Horarios con Algoritmo Genético

Requisitos:
    pip install numpy matplotlib

Qué hace:
- Define grupos, materias, franjas horarias, profesores y su disponibilidad.
- Preferencias suaves de materias por franja (bonus si se cumplen).
- Restricciones duras (como penalización grande):
    * Un profesor NO puede estar en dos grupos a la misma hora.
    * Un profesor sólo puede dictar en horarios donde está disponible.
- GA con:
    * Selección por torneo
    * Cruce uniforme por genes
    * Mutación (reasignación aleatoria de profesor y/o materia)
    * Elitismo
- Corre 100 generaciones y muestra la convergencia del fitness.
- Imprime el mejor horario en formato legible.

Ajusta MUTATION_RATES para experimentar con distintas tasas de mutación.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# Datos del problema (puedes ajustar a tu caso)
# ============================================
GROUPS   = ["Grupo1", "Grupo2", "Grupo3"]
SUBJECTS = ["Matematicas", "Ciencias", "Historia", "Arte"]

TIME_SLOTS = [
    "Lun-9:00", "Lun-11:00",
    "Mar-9:00", "Mar-11:00",
    "Mie-9:00", "Mie-11:00",
]

TEACHERS = ["ProfA", "ProfB", "ProfC", "ProfD"]

# Disponibilidades por profesor (franjas en las que PUEDE dictar)
TEACHER_AVAIL: Dict[str, List[str]] = {
    "ProfA": ["Lun-9:00", "Lun-11:00", "Mar-9:00"],
    "ProfB": ["Lun-11:00", "Mar-9:00", "Mar-11:00", "Mie-9:00"],
    "ProfC": ["Lun-9:00", "Mar-11:00", "Mie-9:00", "Mie-11:00"],
    "ProfD": ["Lun-11:00", "Mar-9:00", "Mie-11:00"],
}

# Preferencias suaves (bonus si la materia está en estas franjas)
SUBJECT_PREFS: Dict[str, List[str]] = {
    "Matematicas": ["Lun-9:00", "Mar-9:00"],
    "Ciencias":    ["Mar-11:00", "Mie-9:00"],
    "Historia":    ["Lun-11:00"],
    "Arte":        ["Mie-11:00"],
}

# ============================================
# Representación: cromosoma = lista de genes
# Un gen corresponde a (time_slot, group) -> (teacher, subject)
# Orden de genes: para cada time_slot, para cada group.
# ============================================
Gene = Tuple[str, str]   # (teacher, subject)

def gene_index(ts_idx: int, g_idx: int) -> int:
    return ts_idx * len(GROUPS) + g_idx

def empty_schedule() -> List[Gene]:
    return [(None, None) for _ in range(len(TIME_SLOTS) * len(GROUPS))]

def random_gene(ts: str) -> Gene:
    teacher = random.choice(TEACHERS)
    subject = random.choice(SUBJECTS)
    return (teacher, subject)

def random_schedule() -> List[Gene]:
    sched = []
    for ts in TIME_SLOTS:
        for _ in GROUPS:
            sched.append(random_gene(ts))
    return sched

# ============================================
# Fitness
# ============================================
@dataclass
class Weights:
    # Penalizaciones (negativas) grandes para violaciones
    w_unavailable: float = -10.0     # profe no disponible en esa franja
    w_double_book: float = -12.0     # profe repetido mismo horario (dos grupos a la vez)
    # Recompensas/penalizaciones suaves
    w_subject_pref: float = +1.5     # materia en franja preferida
    w_subject_nonpref: float = -0.5  # materia en franja no preferida (suave)

def evaluate(schedule: List[Gene], w: Weights = Weights()) -> float:
    score = 0.0
    # Revisa cada franja
    for ts_i, ts in enumerate(TIME_SLOTS):
        teachers_in_slot = []
        for g_i, _ in enumerate(GROUPS):
            t, s = schedule[gene_index(ts_i, g_i)]
            if t is None or s is None:
                score += w.w_subject_nonpref   # preferimos tener algo asignado
                continue
            # Disponibilidad del profe
            if ts not in TEACHER_AVAIL.get(t, []):
                score += w.w_unavailable
            teachers_in_slot.append(t)
            # Preferencias de materia
            prefs = SUBJECT_PREFS.get(s, [])
            score += w.w_subject_pref if ts in prefs else w.w_subject_nonpref
        # Chequeo de doble asignación del mismo profe en mismo horario
        if len(teachers_in_slot) != len(set(teachers_in_slot)):
            # hay al menos un profe repetido en este slot
            # (podría haber más de un choque; penalizamos por cada repetición)
            rep = len(teachers_in_slot) - len(set(teachers_in_slot))
            score += rep * w.w_double_book
    return score

# ============================================
# Operadores genéticos
# ============================================
def tournament_selection(pop: List[List[Gene]], fits: np.ndarray, k: int = 3) -> List[Gene]:
    idxs = np.random.choice(len(pop), size=k, replace=False)
    best = max(idxs, key=lambda i: fits[i])  # maximizar fitness
    return pop[best].copy()

def uniform_crossover(p1: List[Gene], p2: List[Gene], px: float = 0.5) -> Tuple[List[Gene], List[Gene]]:
    n = len(p1)
    c1, c2 = p1.copy(), p2.copy()
    for i in range(n):
        if random.random() < px:
            c1[i], c2[i] = c2[i], c1[i]
    return c1, c2

def mutate(schedule: List[Gene], mr: float = 0.15) -> List[Gene]:
    s = schedule.copy()
    for ts_i, ts in enumerate(TIME_SLOTS):
        for g_i, _ in enumerate(GROUPS):
            idx = gene_index(ts_i, g_i)
            if random.random() < mr:
                # Reasignamos profesor y/o materia aleatoriamente
                t, subj = s[idx]
                # 50% cambiar profe, 50% cambiar materia, 25% ambos
                r = random.random()
                if r < 0.25:
                    t = random.choice(TEACHERS)
                    subj = random.choice(SUBJECTS)
                elif r < 0.625:
                    t = random.choice(TEACHERS)
                else:
                    subj = random.choice(SUBJECTS)
                s[idx] = (t, subj)
    return s

# ============================================
# GA principal
# ============================================
@dataclass
class GAConfig:
    pop_size: int = 120
    generations: int = 100
    tournament_k: int = 3
    crossover_rate: float = 0.9
    mutation_rate: float = 0.15
    elitism: int = 2
    seed: int = 7

def run_ga(cfg: GAConfig) -> Tuple[List[Gene], float, List[float]]:
    random.seed(cfg.seed); np.random.seed(cfg.seed)
    pop = [random_schedule() for _ in range(cfg.pop_size)]

    def eval_pop(P):
        return np.array([evaluate(ind) for ind in P], dtype=float)

    fits = eval_pop(pop)
    best_idx = int(np.argmax(fits))
    best, best_fit = pop[best_idx].copy(), float(fits[best_idx])
    history = [best_fit]

    for _ in range(cfg.generations):
        # Elitismo
        elites_idx = np.argsort(fits)[-cfg.elitism:]
        new_pop = [pop[i].copy() for i in elites_idx]

        # Resto por reproducción
        while len(new_pop) < cfg.pop_size:
            p1 = tournament_selection(pop, fits, cfg.tournament_k)
            p2 = tournament_selection(pop, fits, cfg.tournament_k)
            # Crossover
            if random.random() < cfg.crossover_rate:
                c1, c2 = uniform_crossover(p1, p2, px=0.5)
            else:
                c1, c2 = p1.copy(), p2.copy()
            # Mutación
            c1 = mutate(c1, cfg.mutation_rate)
            c2 = mutate(c2, cfg.mutation_rate)
            new_pop.extend([c1, c2])

        pop = new_pop[:cfg.pop_size]
        fits = eval_pop(pop)

        cur_idx = int(np.argmax(fits))
        cur_best = pop[cur_idx].copy()
        cur_fit = float(fits[cur_idx])
        if cur_fit > best_fit:
            best, best_fit = cur_best, cur_fit

        history.append(best_fit)

    return best, best_fit, history

# ============================================
# Utilidades de impresión y visualización
# ============================================
def print_schedule(schedule: List[Gene]) -> None:
    print("\n=== Mejor horario encontrado ===")
    # Cabecera
    header = ["Hora"] + GROUPS
    widths = [max(len(h), 10) for h in header]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*header))
    print("-" * (sum(widths) + 2*(len(widths)-1)))
    # Filas por franja
    for ts_i, ts in enumerate(TIME_SLOTS):
        row = [ts]
        for g_i, g in enumerate(GROUPS):
            t, s = schedule[gene_index(ts_i, g_i)]
            cell = f"{s or '-'} / {t or '-'}"
            row.append(cell)
        print(fmt.format(*row))

def plot_histories(histories: Dict[float, List[float]]) -> None:
    plt.figure(figsize=(7, 4.2))
    for mr, hist in histories.items():
        plt.plot(hist, label=f"mut={mr}")
    plt.xlabel("Generacion")
    plt.ylabel("Mejor fitness")
    plt.title("Convergencia del GA (distintas tasas de mutacion)")
    plt.grid(True); plt.legend()
    plt.tight_layout()
    plt.show()

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    MUTATION_RATES = [0.05, 0.15, 0.30]   # experimenta aquí
    histories = {}
    best_global_sched, best_global_fit = None, -1e9

    for mr in MUTATION_RATES:
        cfg = GAConfig(mutation_rate=mr, generations=100)
        best, best_fit, hist = run_ga(cfg)
        histories[mr] = hist
        if best_fit > best_global_fit:
            best_global_fit = best_fit
            best_global_sched = best

        print(f"\n>>> Resultado con mutacion={mr}: fitness={best_fit:.3f}")

    # Muestra convergencia comparando tasas de mutación (NO guarda archivos)
    plot_histories(histories)

    # Imprime el mejor horario global
    print_schedule(best_global_sched)
