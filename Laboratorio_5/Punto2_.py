# Introducción a la IA – Algoritmos voraces (Greedy)
# Problema: dar cambio de 63 usando monedas [50, 20, 10, 5, 1]
# Estrategia: siempre elegir la moneda más grande posible en cada paso.

from typing import List, Dict, Tuple

def cambio_voraz(monto: int, monedas: List[int]) -> Dict[int, int]:
    monedas = sorted(monedas, reverse=True)
    uso = {m: 0 for m in monedas}
    restante = monto
    for m in monedas:
        if restante <= 0: break
        cnt, restante = divmod(restante, m)
        uso[m] = cnt
    return uso

def total_monedas(uso: Dict[int,int]) -> int:
    return sum(uso.values())

if __name__ == "__main__":
    monto = 103
    monedas = [50, 20, 10, 5, 1]
    uso = cambio_voraz(monto, monedas)

    print(f"Monto: {monto}")
    print("Monedas usadas (greedy):")
    for m in monedas:
        if uso[m]:
            print(f"  {m}: {uso[m]}")
    print(f"Total de monedas: {total_monedas(uso)}")
    # Para este sistema canónico, greedy devuelve: 50 + 10 + 1 + 1 + 1 (=5 monedas).
