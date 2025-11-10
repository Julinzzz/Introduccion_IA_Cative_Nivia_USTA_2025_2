# caos_trafico.py
# -----------------------------------------------------------
# Demostraciones sencillas para "Sistemas caóticos en tráfico"
# Autor: J. Y. Nivia M.
# -----------------------------------------------------------

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt


# ===========================================================
# 1) Mapa logístico: sensibilidad a condiciones iniciales
# ===========================================================

def logistic_next(x: float, r: float = 3.9) -> float:
    return r * x * (1.0 - x)


def logistic_orbit(x0: float, r: float, n: int) -> np.ndarray:
    x = np.empty(n + 1, dtype=float)
    x[0] = x0
    for t in range(n):
        x[t + 1] = logistic_next(x[t], r)
    return x


def demo_sensitivity(r: float = 3.9, x0: float = 0.5000, y0: float = 0.5001, n: int = 3):
    x = logistic_orbit(x0, r, n)
    y = logistic_orbit(y0, r, n)

    print("\n=== Sensibilidad a condiciones iniciales (mapa logístico) ===")
    print(f"r = {r}, x0 = {x0}, y0 = {y0}")
    print("t    x_t             y_t             |x_t - y_t|")
    for t in range(n + 1):
        diff = abs(x[t] - y[t])
        print(f"{t:<2d}   {x[t]:.9f}   {y[t]:.9f}   {diff:.9e}")

    # gráfico log(|Δ_t|)
    delta = np.abs(x - y)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.semilogy(range(len(delta)), delta, marker="o")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$|\Delta_t|$")
    ax.set_title("Sensibilidad (log)")
    fig.tight_layout()
    fig.savefig("sensibilidad_logistico.png", dpi=180)
    plt.close(fig)


def bifurcation_sample(rs: List[float], burn: int = 220, keep: int = 90, x0: float = 0.501):
    """
    Ilustración de diagrama de bifurcación: para varios r se itera el mapa
    logístico y se plotean los últimos 'keep' estados.
    """
    xs, ys = [], []
    for r in rs:
        x = x0
        for _ in range(burn):
            x = logistic_next(x, r)
        for _ in range(keep):
            x = logistic_next(x, r)
            xs.append(r)
            ys.append(x)

    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.plot(xs, ys, ".", markersize=1.5)
    ax.set_xlabel("r")
    ax.set_ylabel(r"$x^*$")
    ax.set_title("Diagrama de bifurcación (muestra)")
    ax.set_xlim(min(rs) - 0.02, max(rs) + 0.02)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig("bifurcacion_logistico.png", dpi=180)
    plt.close(fig)


# ===========================================================
# 2) Modelo de tráfico: Nagel–Schreckenberg (NaSch)
# ===========================================================

@dataclass
class NaSchConfig:
    L: int = 400           # celdas en el anillo
    vmax: int = 5          # velocidad máxima (celdas/step)
    p: float = 0.25        # prob. de aleatoriedad (frenada)
    steps: int = 1500      # pasos totales
    burn_in: int = 500     # pasos para promediar (se descartan)


class NaSch:
    """
    Implementación mínima del modelo NaSch (1 carril, anillo).
    """
    def __init__(self, L: int, vmax: int, p: float):
        self.L = L
        self.vmax = vmax
        self.p = p
        self.occ = np.full(L, -1, dtype=int)  # -1 = vacío; >=0 = índice de vehículo
        self.pos = None
        self.vel = None

    def init_state(self, density: float, seed: int = 123):
        rng = np.random.default_rng(seed)
        M = int(round(self.L * density))
        positions = rng.choice(self.L, size=M, replace=False)
        self.pos = np.sort(positions)
        self.vel = np.zeros(M, dtype=int)
        self.occ[:] = -1
        self.occ[self.pos] = np.arange(M)

    def step(self):
        M = self.pos.size
        # 1) Acelerar
        self.vel = np.minimum(self.vel + 1, self.vmax)

        # 2) Frenar por distancia al vehículo de adelante
        # calcular gaps
        next_idx = (np.arange(M) + 1) % M
        gaps = (self.pos[next_idx] - self.pos - 1) % self.L
        self.vel = np.minimum(self.vel, gaps)

        # 3) Aleatoriedad
        rnd = np.random.random(M)
        self.vel = np.where((self.vel > 0) & (rnd < self.p), self.vel - 1, self.vel)

        # 4) Mover
        self.occ[:] = -1
        self.pos = (self.pos + self.vel) % self.L
        self.occ[self.pos] = np.arange(M)

        return self.vel.mean()  # útil para flujo medio

    def simulate(self, steps: int, burn_in: int) -> Tuple[float, List[np.ndarray]]:
        v_hist = []
        for t in range(steps):
            vmean = self.step()
            v_hist.append(vmean)
        # flujo q = rho * <v>, con promedio tras burn-in
        v_avg = np.mean(v_hist[burn_in:])
        return v_avg, v_hist


def fundamental_diagram(cfg: NaSchConfig,
                        rhos: np.ndarray,
                        seed: int = 123) -> Tuple[np.ndarray, np.ndarray]:
    qs = []
    for rho in rhos:
        model = NaSch(cfg.L, cfg.vmax, cfg.p)
        model.init_state(float(rho), seed=seed)
        v_avg, _ = model.simulate(cfg.steps, cfg.burn_in)
        q = float(rho) * v_avg
        qs.append(q)
    return rhos, np.array(qs)


def space_time_diagram(rho: float, cfg: NaSchConfig, T: int = 200, seed: int = 7):
    model = NaSch(cfg.L, cfg.vmax, cfg.p)
    model.init_state(rho, seed=seed)

    frames = np.zeros((T, cfg.L), dtype=int)
    for t in range(T):
        frames[t, model.pos] = 1
        model.step()

    # plot
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.imshow(1 - frames, aspect="auto", cmap="gray_r", interpolation="nearest")
    ax.set_xlabel("Espacio (celdas)")
    ax.set_ylabel("Tiempo (steps)")
    ax.set_title(f"Diagrama espacio–tiempo NaSch (ρ={rho:.2f}, p={cfg.p}, v_max={cfg.vmax})")
    fig.tight_layout()
    fig.savefig("nasch_espacio_tiempo.png", dpi=180)
    plt.close(fig)


# ===========================================================
# 3) Ejecución de todos los demos
# ===========================================================

def main():
    # --- Sensibilidad y bifurcación (logístico)
    demo_sensitivity(r=3.9, x0=0.5000, y0=0.5001, n=3)
    rs = np.array([2.8, 3.0, 3.2, 3.4, 3.5, 3.55, 3.6, 3.65, 3.7, 3.8, 3.9])
    bifurcation_sample(rs.tolist())

    # --- NaSch: diagrama fundamental y espacio–tiempo
    cfg = NaSchConfig(L=400, vmax=5, p=0.25, steps=1500, burn_in=500)
    rhos = np.linspace(0.02, 0.95, 22)
    rhos, qs = fundamental_diagram(cfg, rhos)

    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(rhos, qs, marker="o", lw=1)
    ax.set_xlabel(r"Densidad $\rho$")
    ax.set_ylabel(r"Flujo $q=\rho\,\langle v\rangle$")
    ax.set_title("Diagrama fundamental (NaSch)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("fundamental_nasch.png", dpi=180)
    plt.close(fig)

    # espacio–tiempo para una densidad representativa (cerca de la crítica)
    space_time_diagram(rho=0.22, cfg=cfg, T=220, seed=42)

    print("\nFiguras guardadas:")
    print("  - sensibilidad_logistico.png")
    print("  - bifurcacion_logistico.png")
    print("  - fundamental_nasch.png")
    print("  - nasch_espacio_tiempo.png")
    print("\nListo. Puedes insertar estas imágenes en las diapositivas correspondientes.")


if __name__ == "__main__":
    main()
