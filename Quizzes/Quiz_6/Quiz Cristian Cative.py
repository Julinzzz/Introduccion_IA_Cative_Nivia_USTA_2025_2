# ============================================================
# Problema de la Mochila Fraccionaria (Algoritmo Voraz)
# Autor: Cristian Cative
# Curso: Introducción a la Inteligencia Artificial - USTA
# ============================================================

# Importar librerías
import pandas as pd

# ------------------------------------------------------------
# DATOS DEL PROBLEMA
# ------------------------------------------------------------
# Capacidad máxima de la mochila
capacidad = 50  # kg

# Objetos disponibles (nombre, peso, valor)
objetos = [
    {"objeto": "A", "peso": 10, "valor": 60},
    {"objeto": "B", "peso": 20, "valor": 100},
    {"objeto": "C", "peso": 30, "valor": 120}
]

# Crear DataFrame para mostrar los datos iniciales
df = pd.DataFrame(objetos)
df["valor/peso"] = df["valor"] / df["peso"]
print("\n📦 Datos de los objetos disponibles:\n")
print(df.to_string(index=False))

# ------------------------------------------------------------
# FUNCIÓN DEL ALGORITMO VORAZ
# ------------------------------------------------------------
def mochila_fraccional(objetos, capacidad):
    # Ordenar los objetos según su valor/peso (de mayor a menor)
    objetos = sorted(objetos, key=lambda x: x["valor"] / x["peso"], reverse=True)

    valor_total = 0.0
    seleccion = []

    for obj in objetos:
        if capacidad == 0:
            break  # La mochila está llena

        # Si el objeto completo cabe, lo agregamos todo
        if obj["peso"] <= capacidad:
            seleccion.append((obj["objeto"], obj["peso"], obj["valor"], 1.0))
            capacidad -= obj["peso"]
            valor_total += obj["valor"]
        else:
            # Tomar una fracción del objeto
            fraccion = capacidad / obj["peso"]
            valor_fraccion = obj["valor"] * fraccion
            seleccion.append((obj["objeto"], obj["peso"] * fraccion, valor_fraccion, fraccion))
            valor_total += valor_fraccion
            capacidad = 0  # Se llena la mochila

    return seleccion, valor_total


# ------------------------------------------------------------
# EJECUCIÓN DEL ALGORITMO
# ------------------------------------------------------------
seleccion, valor_total = mochila_fraccional(objetos, capacidad)

# Mostrar resultados
print("\n🎒 Resultado de la combinación óptima:\n")
for obj, peso_usado, valor_obtenido, fraccion in seleccion:
    print(f" - Objeto {obj}: {fraccion*100:.1f}% ({peso_usado:.1f} kg, {valor_obtenido:.1f} monedas de oro)")

print(f"\n💰 Valor total máximo obtenido: {valor_total:.1f} monedas de oro")

# ------------------------------------------------------------
# ANÁLISIS DEL ALGORITMO VORAZ
# ------------------------------------------------------------
print("\n📘 Análisis del algoritmo voraz:")
print("""
El algoritmo voraz selecciona los objetos con el mayor valor/peso primero,
tomando fracciones si es necesario. En este caso:

• Se toma todo el objeto B (20 kg, 100 monedas)
• Se toma todo el objeto A (10 kg, 60 monedas)
• Se toma 20/30 = 66.7% del objeto C (20 kg, 80 monedas)

→ Combinación total = 50 kg, valor máximo = 240 monedas de oro.

✔️ Apropiado cuando se pueden dividir los objetos (problema fraccional).
❌ No apropiado cuando los objetos son indivisibles (problema de mochila entera).
      
⚠️ Limitaciones:
 - No garantiza la solución óptima en la 'Mochila entera' (0-1 Knapsack).
 - No considera combinaciones entre objetos, solo decisiones locales.
 - Puede fallar si los valores o pesos no son proporcionales (casos discretos)
""")

