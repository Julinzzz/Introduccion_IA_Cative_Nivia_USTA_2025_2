# -*- coding: utf-8 -*-
"""
PUNTO 1
Análisis "desde cero" de la función: f(x) = x^2 - 3x + 4

Incluye:
- Derivada y segunda derivada con SymPy
- Puntos críticos (f'(x)=0) y clasificación con la 2da derivada
- Nota sobre inexistencia de máximo global
- Evaluación de máximo/mínimo en un intervalo DOMINIO_ACOTADO
- Gráfico de la función con el vértice (mínimo) marcado en la figura
  y mostrado en pantalla.

Requisitos: sympy, numpy, matplotlib
Ejecutar: python punto1_derivada.py
"""
from __future__ import annotations

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from typing import Tuple

# =================== CONFIGURACION ===================
DOMINIO_ACOTADO: Tuple[float, float] | None = (-5.0, 5.0)
# =====================================================

# Definir símbolo y función
x = sp.symbols('x', real=True)
f = x**2 - 3*x + 4

def main():
    print("="*70)
    print("PUNTO 1 – f(x) = x^2 - 3x + 4 (derivada y análisis desde cero)")
    print("="*70)

    # Derivadas
    f1 = sp.diff(f, x)
    f2 = sp.diff(f1, x)
    print(f"f(x)   = {sp.simplify(f)}")
    print(f"f'(x)  = {sp.simplify(f1)}")
    print(f"f''(x) = {sp.simplify(f2)}")

    # Puntos críticos: f'(x)=0
    criticos = sp.solve(sp.Eq(f1, 0), x)  # soluciones simbólicas
    print("\nPuntos críticos (f'(x)=0):")
    for c in criticos:
        fc = sp.N(f.subs(x, c))
        print(f"  x* = {sp.N(c)}  ->  f(x*) = {fc}")

    # Clasificación (segunda derivada)
    print("\nClasificación por f''(x):")
    for c in criticos:
        valor_segunda = sp.N(f2.subs(x, c))
        if valor_segunda > 0:
            desc = "mínimo local (y global, parábola abre hacia arriba)"
        elif valor_segunda < 0:
            desc = "máximo local"
        else:
            desc = "indeterminado (f''=0)"
        print(f"  En x = {sp.N(c)}: f''(x) = {valor_segunda} -> {desc}")

    # Observación general
    print("\nComo el coeficiente de x^2 es positivo, la parábola abre hacia arriba:")
    print("=> NO existe máximo global en R. Sí existe mínimo global en el vértice.\n")

    # (Opcional) máximo/mínimo en intervalo acotado
    if DOMINIO_ACOTADO is not None:
        a, b = map(float, DOMINIO_ACOTADO)
        fa = float(sp.N(f.subs(x, a)))
        fb = float(sp.N(f.subs(x, b)))
        candidatos = [(a, fa), (b, fb)]
        for c in criticos:
            c_f = float(sp.N(c))
            if a <= c_f <= b:
                candidatos.append((c_f, float(sp.N(f.subs(x, c_f)))))
        xmin, fmin = min(candidatos, key=lambda t: t[1])
        xmax, fmax = max(candidatos, key=lambda t: t[1])
        print(f"En el intervalo [{a}, {b}]:")
        print(f"  f mínimo = {fmin:.6f} en x = {xmin:.6f}")
        print(f"  f máximo = {fmax:.6f} en x = {xmax:.6f}\n")

    # Gráfico con el vértice
    xc = float(sp.N(criticos[0])) if criticos else 0.0
    xs = np.linspace(xc-6, xc+6, 400)
    ys = xs**2 - 3*xs + 4

    plt.figure(figsize=(7,5))
    plt.plot(xs, ys, linewidth=2)
    if criticos:
        c = float(sp.N(criticos[0]))
        fc = float(sp.N(f.subs(x, c)))
        # Punto mínimo marcado
        plt.scatter([c], [fc], s=80, zorder=5)
        plt.annotate("mínimo\n"
                     f"x={c:.2f}, f(x)={fc:.2f}",
                     (c, fc), xytext=(15, 18),
                     textcoords="offset points",
                     arrowprops=dict(arrowstyle="->", lw=1.5))
        plt.axvline(c, linestyle="--", linewidth=1)
        plt.axhline(fc, linestyle="--", linewidth=1)
        print(f"\nMínimo global en x = {c:.6f} con f(x) = {fc:.6f}")

    plt.grid(True)
    plt.xlabel("x"); plt.ylabel("f(x)")
    plt.title("f(x)=x^2-3x+4 con mínimo marcado")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
