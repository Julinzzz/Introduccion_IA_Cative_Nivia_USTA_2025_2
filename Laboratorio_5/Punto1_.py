# ----------------------------------------------
# Introducción a la IA – Búsqueda Local (Hill Climbing)
# Problema: Organización de 6 sillas y 6 personas.
# Vecindario: intercambiar (swap) exactamente DOS personas por turno.
# Evaluación: "satisfacción total" = suma de satisfacciones de personas vecinas.
#             Usamos mesa circular: cada persona tiene dos vecinos.
# ----------------------------------------------

import random
from typing import List, Tuple

# === 1) Modelo del problema ===============================================
# Personas
PERSONAS = ["A", "B", "C", "D", "E", "F"]

# Matriz de satisfacciones S[i][j] = cuánto disfruta i sentarse al lado de j.
S = {
    "A": {"A": 0,  "B":  2, "C": -1, "D":  4, "E":  0, "F":  1},
    "B": {"A":  1, "B":  0, "C":  3, "D": -2, "E":  2, "F":  0},
    "C": {"A": -1, "B":  0, "C":  0, "D":  5, "E": -2, "F":  2},
    "D": {"A":  4, "B": -3, "C":  2, "D":  0, "E":  1, "F": -1},
    "E": {"A":  0, "B":  3, "C": -2, "D":  1, "E":  0, "F":  4},
    "F": {"A":  2, "B":  0, "C":  2, "D": -1, "E":  3, "F":  0},
}

def satisfaccion_total(disposicion: List[str]) -> int:
    """
    Suma la satisfacción bilateral de vecinos en una mesa circular.
    Para cada pareja vecina (i,j), suma S[i][j] + S[j][i] una sola vez.
    """
    n = len(disposicion)
    total = 0
    for k in range(n):                # pareja (k, k+1) y cierre (n-1, 0)
        a = disposicion[k]
        b = disposicion[(k + 1) % n]
        total += S[a][b] + S[b][a]
    return total

# === 2) Vecindario: mover exactamente dos personas (swap) ==================
def mejores_vecinos_swap(disposicion: List[str]) -> List[Tuple[int, int, int]]:
    """
    Devuelve lista ordenada de vecinos (i,j,ganancia) para todos los swaps i<j.
    'ganancia' = nueva_satisfaccion - satisfaccion_actual.
    """
    base = satisfaccion_total(disposicion)
    n = len(disposicion)
    candidatos = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            disp = disposicion.copy()
            disp[i], disp[j] = disp[j], disp[i]
            candidatos.append((i, j, satisfaccion_total(disp) - base))
    # Ordenar por ganancia descendente
    candidatos.sort(key=lambda x: x[2], reverse=True)
    return candidatos

# === 3) Hill Climbing con primer/mejor ascenso =============================
def hill_climbing(
    inicial: List[str] = None,
    modo: str = "mejor",         # "mejor" = best-ascent, "primero" = first-ascent
    max_iter: int = 500,
    verbose: bool = True
) -> Tuple[List[str], int, int]:
    """
    Realiza ascenso de colina con vecindario de swaps (dos personas por turno).
    Retorna (mejor_disposición, mejor_valor, iteraciones_realizadas).
    """
    if inicial is None:
        actual = PERSONAS.copy()
        random.shuffle(actual)
    else:
        actual = inicial.copy()

    valor = satisfaccion_total(actual)

    if verbose:
        print(f"Inicio: {actual}  ->  valor = {valor}")

    for it in range(1, max_iter + 1):
        vecinos = mejores_vecinos_swap(actual)

        # Si no hay mejora posible, estamos en óptimo local
        if not vecinos or vecinos[0][2] <= 0:
            if verbose:
                print(f"Óptimo local en iter {it-1}: {actual}  ->  valor = {valor}")
            return actual, valor, it - 1

        if modo == "primero":
            # Toma el primer vecino que mejore (>0)
            elegido = next((v for v in vecinos if v[2] > 0), None)
        else:  # "mejor"
            # Toma el mejor vecino (mayor ganancia)
            elegido = vecinos[0]

        i, j, ganancia = elegido
        actual[i], actual[j] = actual[j], actual[i]
        valor += ganancia

        if verbose:
            print(f"Iter {it:02d}: swap({i},{j})  ganancia={ganancia:+}  "
                  f"-> {actual}  valor={valor}")

    if verbose:
        print(f"Paro por max_iter. Último: {actual} -> valor={valor}")
    return actual, valor, max_iter

# === 4) Random-Restarts para escapar de óptimos locales ====================
def hill_climbing_random_restarts(
    reinicios: int = 20,
    modo: str = "mejor",
    max_iter: int = 300,
    seed: int = 42,
    verbose: bool = False
) -> Tuple[List[str], int]:
    """
    Ejecuta múltiples reinicios aleatorios y conserva la mejor solución.
    """
    random.seed(seed)
    mejor_disp, mejor_val = None, float("-inf")
    for r in range(reinicios):
        disp, val, _ = hill_climbing(inicial=None, modo=modo, max_iter=max_iter, verbose=verbose)
        if val > mejor_val:
            mejor_disp, mejor_val = disp, val
    # Resumen final
    print(f"\nMejor solución tras {reinicios} reinicios:")
    print(f"{mejor_disp}  ->  satisfacción total = {mejor_val}")
    return mejor_disp, mejor_val

# === 5) Ejecución ejemplo ==================================================
if __name__ == "__main__":
    # Posible ejecutarlo con dos opciones
    # Opción A: una corrida con traza (mejor-ascenso)
    _ = hill_climbing(modo="mejor", verbose=True)

    # Opción B: varias corridas con reinicios (silenciosas) y resumen final
    # _ = hill_climbing_random_restarts(reinicios=30, modo="primero", verbose=False)
