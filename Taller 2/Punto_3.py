"""
Punto 3 — Controlador de robot de carreras con IA híbrida
(Genético + ACO + PSO)

• GA: evoluciona los 3 parámetros del controlador:
    - agresividad   (a ∈ [0,1])
    - conservador   (c ∈ [0,1])
    - adelantamiento(o ∈ [0,1])

• ACO: aprende la mejor línea de carrera (elegir entre 3 líneas
  discretas por tramo: interior / ideal / exterior).

• PSO: decide localmente cómo ejecutar un sobrepaso cuando aparece
  un oponente (cuándo/qué tan fuerte cambiar de carril y acelerar).

El simulador es ligero y determinista (seed fija), pensado para uso docente
en Introducción a la IA.
"""

from __future__ import annotations
import random, math, json, csv, os
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

# ============================================================
# 0) Parámetros globales del experimento
# ============================================================
SEED = 123
random.seed(SEED)

N_SEG      = 5            # tramos de pista
LANES      = 3             # 0=interior, 1=ideal, 2=exterior
V_MAX_BASE = 69.0          # m/s tope teórico (≈187 km/h) en recta plana
DT_OPP     = 0.15          # densidad de oponentes (prob de bloque por tramo)
N_OPP_SAMPLES = 2          # muestras de oponentes por evaluación

# ============================================================
# 1) Modelado de pista y controlador
# ============================================================
@dataclass
class Segmento:
    curva: float   # [0,1] 0 recta, 1 curva cerrada
    largo: float   # metros

@dataclass
class Track:
    segmentos: List[Segmento]
    width: float = 10.0  # m

def generar_pista(n=N_SEG, seed=SEED) -> Track:
    rng = random.Random(seed)
    segs = []
    for i in range(n):
        # bloques "tipo": recta → curva leve → curva media → recta...
        base = 0.15 + 0.35*math.sin(2*math.pi*(i/n)*rng.uniform(0.9,1.2))
        curva = max(0.0, min(1.0, base + rng.uniform(-0.08, 0.08)))
        largo = rng.uniform(60.0, 140.0) if curva < 0.25 else rng.uniform(40.0, 90.0)
        segs.append(Segmento(curva=curva, largo=largo))
    return Track(segs)

@dataclass
class Controller:
    agresividad: float   # ↑ velocidad, ↑ riesgo
    conservador: float   # ↑ seguridad, ↓ velocidad
    adelantamiento: float# propensión a intentar overtake

    def clip(self):
        self.agresividad   = max(0, min(1, self.agresividad))
        self.conservador   = max(0, min(1, self.conservador))
        self.adelantamiento= max(0, min(1, self.adelantamiento))
        return self

# ============================================================
# 2) Utilidades físicas/evaluación base
# ============================================================
def lane_factor(lane: int) -> float:
    """
    Factor de línea sobre el límite de velocidad por curvatura.
    interior(0) reduce distancia pero castiga más en curva cerrada;
    ideal(1) balance; exterior(2) permite mayor radio.
    """
    if lane == 0:   # interior
        return -0.05
    if lane == 1:   # ideal
        return 0.00
    return +0.05    # exterior

def vmax_segmento(seg: Segmento, lane: int, ctrl: Controller) -> float:
    """
    Límite de velocidad para el tramo según curvatura, línea y estilo del conductor.
    """
    # penalización por curvatura (≈ 1 - k*curva)
    curv_penalty = 1.0 - 0.72*seg.curva
    # ajuste por línea (exterior +, interior -)
    line_adj = 1.0 + lane_factor(lane)
    # estilo del controlador
    style = 1.0 + 0.35*ctrl.agresividad - 0.30*ctrl.conservador
    vmax = V_MAX_BASE * curv_penalty * line_adj * style
    return max(8.0, vmax)  # mínimo físico

# ============================================================
# 3) Oponentes (bloqueos) y PSO para sobrepaso
# ============================================================
def muestrea_oponentes(track: Track, seed: int) -> Dict[int, Dict]:
    """Genera un diccionario {i: {'speed_factor':..}} con bloqueos en algunos tramos."""
    rng = random.Random(seed)
    opp = {}
    for i, seg in enumerate(track.segmentos):
        if rng.random() < DT_OPP:  # aparece un bloqueo
            # el oponente va un poco más lento (factor 0.8-0.95)
            opp[i] = {"speed_factor": rng.uniform(0.80, 0.95)}
    return opp

@dataclass
class PSOConfig:
    particles: int = 18
    iters: int = 22
    w: float = 0.55
    c1: float = 1.6
    c2: float = 1.6

class PSOPlanner:
    """
    Optimiza una micro-estrategia de sobrepaso en un tramo:
    x = [shift, pace] en [0,1]^2
      - shift: cuánto moverse hacia exterior (0 sin cambio, 1 = carril más externo)
      - pace : empuje adicional (0 nada, 1 empuje máximo permitido)
    Se minimiza el tiempo esperado del tramo + penalizaciones por riesgo.
    """
    def __init__(self, cfg: PSOConfig = PSOConfig(), seed: int = SEED):
        self.cfg = cfg
        self.rng = random.Random(seed)

    def _eval(self, x: Tuple[float,float], seg: Segmento, lane: int,
              ctrl: Controller, opp_speed_factor: float) -> float:
        shift, pace = x
        # Lane efectivo tras el desplazamiento
        eff_lane = min(LANES-1, lane + (1 if shift > 0.5 else 0))
        # Velocidad base sin overtake
        v_nom = vmax_segmento(seg, lane, ctrl)
        v_eff = vmax_segmento(seg, eff_lane, ctrl)

        # impulso por "pace" (limitado por estilo y curvatura)
        pace_gain = (0.08 + 0.22*ctrl.adelantamiento) * pace * (1.0 - 0.5*seg.curva)
        v_eff *= (1.0 + pace_gain)

        # si hay oponente, impone un tope; el cambio de carril + pace ayuda a superarlo
        overtake_bonus = 0.20*shift + 0.35*pace
        opp_limit = v_nom * opp_speed_factor * (1.0 + 0.60*overtake_bonus)
        v_eff = min(v_eff, max(v_nom, opp_limit))

        # riesgo por agresividad + cambio de carril en curva
        risk = (0.20 + 0.80*ctrl.agresividad) * seg.curva * (0.4 + 0.8*shift) * (0.6 + 0.7*pace)
        risk *= (1.0 - 0.7*ctrl.conservador)  # conservador reduce riesgo

        # tiempo y penalización (tiempo equivalente por riesgo)
        t = seg.largo / max(1e-6, v_eff)
        penalty = 0.35 * risk  # en segundos equivalentes aprox
        return t + penalty

    def optimize(self, seg: Segmento, lane: int, ctrl: Controller, opp_speed_factor: float) -> Tuple[float, Tuple[float,float]]:
        rng = self.rng
        # Inicialización
        X = [(rng.random(), rng.random()) for _ in range(self.cfg.particles)]
        V = [(rng.uniform(-0.2,0.2), rng.uniform(-0.2,0.2)) for _ in range(self.cfg.particles)]

        pbest = X[:]
        pbest_val = [self._eval(x, seg, lane, ctrl, opp_speed_factor) for x in X]
        gbest_idx = min(range(self.cfg.particles), key=lambda i: pbest_val[i])
        gbest = pbest[gbest_idx]

        for _ in range(self.cfg.iters):
            for i in range(self.cfg.particles):
                r1, r2 = rng.random(), rng.random()
                vx = (self.cfg.w*V[i][0] +
                      self.cfg.c1*r1*(pbest[i][0]-X[i][0]) +
                      self.cfg.c2*r2*(gbest[0]-X[i][0]))
                vy = (self.cfg.w*V[i][1] +
                      self.cfg.c1*r1*(pbest[i][1]-X[i][1]) +
                      self.cfg.c2*r2*(gbest[1]-X[i][1]))
                V[i] = (vx, vy)
                X[i] = (max(0.0, min(1.0, X[i][0]+vx)),
                        max(0.0, min(1.0, X[i][1]+vy)))

                val = self._eval(X[i], seg, lane, ctrl, opp_speed_factor)
                if val < pbest_val[i]:
                    pbest[i], pbest_val[i] = X[i], val
                    if val < pbest_val[gbest_idx]:
                        gbest_idx, gbest = i, X[i]

        best_val = self._eval(gbest, seg, lane, ctrl, opp_speed_factor)
        return best_val, gbest  # (tiempo esperado del tramo, decisión)

# ============================================================
# 4) ACO — línea de carrera
# ============================================================
@dataclass
class ACOConfig:
    ants: int = 18
    iters: int = 18
    alpha: float = 1.0  # feromona
    beta: float = 2.0   # heurística
    evap: float = 0.25
    Q: float = 150.0

class RacingACO:
    """
    Cada hormiga elige una línea (lane 0/1/2) por tramo según:
        prob ∝ (tau^alpha) * (eta^beta)
    donde la heurística eta favorece líneas con menor tiempo estimado
    (sin oponentes) usando el controlador dado.
    """
    def __init__(self, track: Track, ctrl: Controller, pso: PSOPlanner, cfg: ACOConfig = ACOConfig(), seed: int = SEED):
        self.track, self.ctrl, self.cfg = track, ctrl, cfg
        self.pso = pso
        self.rng = random.Random(seed)
        # feromonas por (seg, lane)
        self.tau = [[0.5 for _ in range(LANES)] for _ in range(len(track.segmentos))]

    def _heuristic(self, seg: Segmento, lane: int) -> float:
        v = vmax_segmento(seg, lane, self.ctrl)
        t = seg.largo / v
        # menor tiempo => mayor heurística
        return 1.0 / max(1e-6, t)

    def _build_line(self) -> List[int]:
        line = []
        for i, seg in enumerate(self.track.segmentos):
            etas = [self._heuristic(seg, l) for l in range(LANES)]
            probs = []
            for l in range(LANES):
                probs.append( (self.tau[i][l] ** self.cfg.alpha) * (etas[l] ** self.cfg.beta) )
            s = sum(probs)
            if s == 0:  # fallback
                line.append(1)
            else:
                r = self.rng.random() * s
                acc = 0.0
                opt = 0
                for l, p in enumerate(probs):
                    acc += p
                    if acc >= r:
                        opt = l; break
                line.append(opt)
        return line

    def _eval_line(self, line: List[int], seed_opp: int) -> float:
        """Tiempo total con PSO ante oponentes muestreados (semilla fija)."""
        opp = muestrea_oponentes(self.track, seed_opp)
        total = 0.0
        for i, seg in enumerate(self.track.segmentos):
            lane = line[i]
            if i in opp:
                t_l, _ = self.pso.optimize(seg, lane, self.ctrl, opp[i]["speed_factor"])
            else:
                v = vmax_segmento(seg, lane, self.ctrl)
                t_l = seg.largo / v
            total += t_l
        return total

    def train(self) -> List[int]:
        best_line, best_time = None, float("inf")
        for it in range(self.cfg.iters):
            ants_lines = []
            ants_times = []
            # construir y evaluar
            for _ in range(self.cfg.ants):
                line = self._build_line()
                # usar varias muestras de oponentes para robustez
                times = [self._eval_line(line, seed_opp=SEED + it*31 + k*97) for k in range(2)]
                t = sum(times)/len(times)
                ants_lines.append(line)
                ants_times.append(t)
                if t < best_time:
                    best_time, best_line = t, line[:]

            # evaporación
            for i in range(len(self.tau)):
                for l in range(LANES):
                    self.tau[i][l] *= (1.0 - self.cfg.evap)

            # refuerzo proporcional a 1/tiempo
            for line, t in zip(ants_lines, ants_times):
                deposit = self.cfg.Q / max(1e-6, t)
                for i, l in enumerate(line):
                    self.tau[i][l] += deposit

        return best_line

# ============================================================
# 5) GA — evolución de parámetros del controlador
# ============================================================
@dataclass
class GAConfig:
    pop: int = 28
    gens: int = 18
    elite: int = 2
    p_mut: float = 0.25
    sigma: float = 0.18
    torneo: int = 3

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))

def crossover(a: Controller, b: Controller, rng: random.Random) -> Controller:
    beta = rng.random()
    h = Controller(
        agresividad    = clip01(a.agresividad*beta + b.agresividad*(1-beta)),
        conservador    = clip01(a.conservador*beta + b.conservador*(1-beta)),
        adelantamiento = clip01(a.adelantamiento*beta + b.adelantamiento*(1-beta)),
    )
    return h

def mutar(c: Controller, cfg: GAConfig, rng: random.Random) -> Controller:
    if rng.random() < cfg.p_mut:
        c.agresividad    = clip01(c.agresividad + rng.gauss(0, cfg.sigma))
    if rng.random() < cfg.p_mut:
        c.conservador    = clip01(c.conservador + rng.gauss(0, cfg.sigma))
    if rng.random() < cfg.p_mut:
        c.adelantamiento = clip01(c.adelantamiento + rng.gauss(0, cfg.sigma))
    return c

def torneo_sel(pobl: List[Controller], fits: List[float], k: int, rng: random.Random) -> Controller:
    idxs = rng.sample(range(len(pobl)), k)
    # fitness mayor es mejor (usaremos -tiempo), escoger el mayor
    best = max(idxs, key=lambda i: fits[i])
    return pobl[best]

def eval_controller(ctrl: Controller, track: Track, rng: random.Random) -> Tuple[float, List[int]]:
    """
    Evalúa un controlador:
      - Aprende línea con ACO (rápido)
      - Promedia tiempo con varias muestras de oponentes
    Retorna (fitness, best_line)
    fitness = -tiempo (para maximizar)
    """
    pso = PSOPlanner(seed=rng.randrange(1_000_000))
    aco = RacingACO(track, ctrl, pso, seed=rng.randrange(1_000_000))
    line = aco.train()

    # tiempo promedio sobre distintas muestras
    total = 0.0
    for k in range(N_OPP_SAMPLES):
        opp = muestrea_oponentes(track, seed=rng.randrange(1_000_000))
        t = 0.0
        for i, seg in enumerate(track.segmentos):
            lane = line[i]
            if i in opp:
                t_i, _ = pso.optimize(seg, lane, ctrl, opp[i]["speed_factor"])
            else:
                v = vmax_segmento(seg, lane, ctrl)
                t_i = seg.largo / v
            t += t_i
        total += t
    lap_time = total / N_OPP_SAMPLES
    fitness = -lap_time
    return fitness, line

def run_ga(track: Track, cfg: GAConfig = GAConfig(), seed: int = SEED):
    rng = random.Random(seed)
    # población inicial
    pobl = [Controller(rng.random(), rng.random(), rng.random()).clip() for _ in range(cfg.pop)]
    best = None
    hist = []

    for g in range(cfg.gens):
        fits = []
        lines = []
        for c in pobl:
            f, l = eval_controller(c, track, rng)
            fits.append(f)
            lines.append(l)
        # log
        best_idx = max(range(cfg.pop), key=lambda i: fits[i])
        best = (pobl[best_idx], -fits[best_idx], lines[best_idx])  # (ctrl, lap_time, line)
        hist.append((g, -sum(fits)/len(fits), -max(fits)))

        print(f"Gen {g:02d} | mejor_tiempo={best[1]:.2f} s | promedio={-sum(fits)/len(fits):.2f} s")

        # elitismo
        elite_idx = sorted(range(cfg.pop), key=lambda i: fits[i], reverse=True)[:cfg.elite]
        nueva = [pobl[i] for i in elite_idx]

        # reproducción
        while len(nueva) < cfg.pop:
            p1 = torneo_sel(pobl, fits, cfg.torneo, rng)
            p2 = torneo_sel(pobl, fits, cfg.torneo, rng)
            hijo = crossover(p1, p2, rng)
            hijo = mutar(hijo, cfg, rng).clip()
            nueva.append(hijo)
        pobl = nueva

    return best, hist  # best=(ctrl, lap_time, line)

# ============================================================
# 6) Main
# ============================================================

if __name__ == "__main__":
    track = generar_pista()
    best, hist = run_ga(track)
    print("\nMejor controlador encontrado:")
    print(best[0])
    print(f"Tiempo de vuelta estimado: {best[1]:.2f} s")
