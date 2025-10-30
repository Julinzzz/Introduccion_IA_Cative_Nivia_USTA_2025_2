# Nivia Julian - Quiz Mochila Fraccional (Greedy)
# ---------------------------------------------------------------
# Algoritmo voraz para maximizar el valor en una mochila con capacidad fija.
# - Ordena los objetos por densidad (valor/peso) de mayor a menor
# - Toma objetos completos mientras haya espacio
# - Del último toma solo la fracción necesaria
# - Imprime (objeto, fracción, peso usado, valor aportado) y los totales
#
# Detalles:
# * Complejidad: O(n log n) por la ordenación
# * Aplica SOLO a mochila fraccional; para 0-1 no garantiza óptimo
# ---------------------------------------------------------------


# Datos: (nombre, peso, valor)
items = [
    ("A", 10, 60),
    ("B", 20, 100),
    ("C", 30, 120),
]
capacidad = 50

# Ordenar por densidad de valor (valor/peso), de mayor a menor
items = sorted(items, key=lambda x: x[2] / x[1], reverse=True)

valor_total = 0.0
seleccion = []  # (nombre, fraccion_tomada, peso_usado, valor_aportado)
restante = capacidad

for nombre, peso, valor in items:
    if restante == 0:
        break
    if peso <= restante:
        seleccion.append((nombre, 1.0, peso, valor))
        valor_total += valor
        restante -= peso
    else:
        frac = restante / peso
        aporte = valor * frac
        seleccion.append((nombre, frac, restante, aporte))
        valor_total += aporte
        restante = 0  # mochila llena

# Mostrar resultado
print("Selección (objeto, fracción, peso usado, valor ganado):")
for nombre, frac, p_usado, v_aportado in seleccion:
    print(f"{nombre}: {frac:.2f}  {p_usado} kg  {v_aportado:.0f} monedas")

print(f"\nPeso total usado: {capacidad - restante} kg")
print(f"Valor total: {valor_total:.0f} monedas")
