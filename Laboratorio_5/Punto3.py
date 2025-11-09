# Introducción a la IA – Juegos adversariales
# Juego: Piedra–Papel–Tijera (simultáneo, suma cero).
# Si ambos jugadores son racionales y conocen el juego,
# la estrategia óptima es el equilibrio mixto: jugar cada opción con prob. 1/3.

import random

ACCIONES = ("piedra","papel","tijera")

def rps_equilibrio() -> str:
    """Devuelve una jugada siguiendo el equilibrio de Nash: uniforme en {R,P,S}."""
    return random.choice(ACCIONES)

# Útil para ver qué pasaría si el rival NO fuese plenamente racional.
PAGA = { # utilidad desde la perspectiva de la fila
    "piedra":  {"piedra":0,  "papel":-1, "tijera":1},
    "papel":   {"piedra":1,  "papel":0,  "tijera":-1},
    "tijera":  {"piedra":-1, "papel":1,  "tijera":0},
}

def mejor_respuesta(freq_opp: dict) -> str:
    """
    Dadas frecuencias del oponente (dict con claves ACCIONES que suman 1),
    retorna la acción con mayor utilidad esperada.
    """
    mejor, val_mejor = None, float("-inf")
    for a in ACCIONES:
        u = sum(PAGA[a][b] * freq_opp.get(b,0.0) for b in ACCIONES)
        if u > val_mejor:
            mejor, val_mejor = a, u
    return mejor

if __name__ == "__main__":
    # Jugada óptima contra rival racional (equilibrio):
    print("Jugada (equilibrio de Nash):", rps_equilibrio())
    freq = {"piedra":0.6, "papel":0.3, "tijera":0.1}
    print("Mejor respuesta a sesgo observado:", mejor_respuesta(freq))

