# Quiz_18_Sept

Este documento explica el desarrollo del **Problema del Agente Viajero (TSP)** utilizando un **Algoritmo Genético (GA)** en Python, tal como se planteó en el quiz práctico.

---

## 1. Descripción del Problema

El **problema del agente viajero (TSP)** consiste en encontrar la ruta más corta que permita visitar un conjunto de ciudades exactamente **una vez** y regresar al punto de inicio.

En este caso se nos dan 8 ciudades con sus coordenadas en el plano 2D:

```python
ciudades = {
    'A': (0, 0),
    'B': (1, 5),
    'C': (2, 3),
    'D': (5, 2),
    'E': (6, 6),
    'F': (7, 1),
    'G': (8, 4),
    'H': (9, 9),
}
```

---

## 2. Componentes del Algoritmo Genético

Un **algoritmo genético (GA)** se inspira en los principios de la evolución biológica: selección, cruce y mutación.

### 2.1 Representación de Individuos
Cada **individuo** es una permutación de las ciudades, representando un posible recorrido.

Ejemplo:
```
['A', 'C', 'B', 'E', 'D', 'H', 'F', 'G']
```

### 2.2 Función de Evaluación
La **distancia total de la ruta** se calcula usando la distancia euclidiana entre ciudades consecutivas, regresando al punto inicial:

```python
def distancia_ruta(ruta):
    total = 0.0
    for i in range(len(ruta)):
        c1 = ruta[i]
        c2 = ruta[(i + 1) % len(ruta)]
        total += distancia_euclidiana(ciudades[c1], ciudades[c2])
    return total
```

### 2.3 Población Inicial
Se generan rutas aleatorias como población inicial:

```python
def crear_poblacion_inicial(tam_poblacion):
    base = list(ciudades.keys())
    poblacion = []
    for _ in range(tam_poblacion):
        individuo = base[:]
        random.shuffle(individuo)
        poblacion.append(individuo)
    return poblacion
```

### 2.4 Selección (Torneo)
Se eligen varios individuos al azar y se escoge el mejor (menor distancia).

### 2.5 Cruce (Ordered Crossover - OX)
Combina segmentos de dos padres para crear hijos válidos (sin repetir ciudades).

### 2.6 Mutación (Swap)
Intercambia dos ciudades al azar con cierta probabilidad para mantener diversidad.

---

## 3. Algoritmo Genético Principal

1. **Inicialización**: generar población inicial.
2. **Evaluación**: calcular distancias de cada ruta.
3. **Selección**: elegir padres por torneo.
4. **Cruce**: aplicar OX con probabilidad definida.
5. **Mutación**: intercambio aleatorio con probabilidad definida.
6. **Elitismo**: conservar los mejores individuos.
7. **Iterar**: repetir por N generaciones.

---

## 4. Ejecución y Resultados

El algoritmo se ejecuta de la siguiente manera:

```bash
python tsp_ga.py
```

Ejemplo de salida durante la ejecución:

```
Gen   50 | mejor distancia: 25.1372 | ruta: A-C-B-E-D-F-G-H
Gen  100 | mejor distancia: 23.9541 | ruta: A-B-C-D-F-G-E-H
...
== Resultado final ==
Mejor ruta encontrada: A -> C -> B -> E -> D -> F -> G -> H -> A
Distancia total: 23.9541
```

---

## 5. Conclusiones

- El **TSP** es un problema NP-difícil, por lo que no existe un método exacto eficiente para grandes cantidades de ciudades.  
- Los **algoritmos genéticos** ofrecen una buena solución aproximada en tiempos razonables.  
- La implementación presentada permite experimentar con distintos parámetros: tamaño de población, generaciones, tasa de mutación y tipo de selección.  

---

📌 **Nota:** Este código es totalmente modificable para más ciudades o para cambiar la estrategia de selección/mutación.
