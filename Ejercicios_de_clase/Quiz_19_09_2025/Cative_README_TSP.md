# TSP con Algoritmo Genético — Documentación detallada

Este repositorio contiene una implementación en Python de un **Algoritmo Genético (AG)** para resolver una instancia pequeña del **Problema del Agente Viajero (TSP)**.  
A continuación se explica, paso a paso, la estructura del código `tsp_genetico.py`, las funciones principales, parámetros y uso recomendado.

---

## Estructura del proyecto

```
.

├─ tsp_genetico.py      # Código fuente principal (Algoritmo Genético y visualización)
└─ README.md            # Este archivo: explicación detallada del código
```

---

## Requisitos

- Python 3.8 o superior
- Paquetes:
  - `numpy`
  - `matplotlib`

Instalación rápida:

```bash
pip install numpy matplotlib
```

---

## Descripción general del enfoque

El código resuelve el TSP para 8 ciudades predefinidas (`'A'..'H'`) codificadas como coordenadas 2D.  
Cada individuo de la población es una **ruta**: una lista con el orden en el que se visitan las ciudades (por ejemplo `['A','C','B',... ]`).

El objetivo del AG es **minimizar** la distancia total de la ruta (incluyendo el regreso a la ciudad inicial).

---

## Resumen de archivos

### `tsp_genetico.py`
Contiene:
- Definición de las ciudades y sus coordenadas.
- Funciones auxiliares para calcular distancias y fitness.
- Operadores genéticos: selección por torneo, cruce ordenado OX, y mutación por intercambio.
- Bucle principal del AG (`algoritmo_genetico`) con parámetros ajustables.
- Funciones de visualización: `graficar_ruta` y `graficar_convergencia`.

---

## Explicación del código (función por función)

### Definición de ciudades
```python
ciudades = {
    'A': (0, 0),
    'B': (1, 5),
    'C': (2, 3),
    'D': (5, 2),
    'E': (6, 6),
    'F': (7, 1),
    'G': (8, 4),
    'H': (9, 9)
}
```
- `nombres = list(ciudades.keys())` → lista `['A','B',...,'H']`.
- `coords = list(ciudades.values())` → lista de tuplas con coordenadas.

### `distancia(a, b)`
Calcula la distancia euclidiana entre dos puntos `a` y `b` (tuplas `(x,y)`).

### `distancia_total(ruta)`
Recibe una ruta (lista de nombres de ciudades) y devuelve la distancia total del ciclo que visita todas las ciudades y regresa al inicio:
- Suma las distancias entre pares consecutivos y añade la distancia del último al primero.

### `fitness(ruta)`
Retorna la aptitud de una ruta como `1 / (distancia_total + eps)`.  
Se usa en algunas variantes de AG, aunque en este script directamente se trabaja con distancias para comparación (minimizar).

### `seleccion(poblacion, distancias)`
Implementa selección por **torneo** (tamaño 3):
- Toma 3 individuos (ruta, distancia) aleatorios y devuelve el que tiene **menor** distancia (mejor).

### `cruce_ordenado(padre1, padre2)`
Cruce Ordered Crossover (OX):
- Selecciona un segmento `[a:b]` del `padre1` y lo copia al hijo en la misma posición.
- Completa los elementos faltantes con el orden que aparecen en `padre2`.
- Garantiza que el hijo sea una permutación válida sin repetidos.

### `mutacion(ruta, tasa=0.2)`
Mutación por intercambio (swap):
- Con probabilidad `tasa` selecciona dos índices `i,j` y los intercambia.
- Mantiene la validez de la ruta (sigue siendo una permutación).

### `algoritmo_genetico(generaciones=200, poblacion_size=50, tasa_mutacion=0.2)`
Bucle principal:
1. Crea población inicial: `poblacion_size` permutaciones aleatorias de `nombres`.
2. Para cada generación:
   - Calcula `distancias = [distancia_total(r) for r in poblacion]`.
   - Actualiza el mejor global si aparece una ruta mejor.
   - Crea `nueva_poblacion` mediante: selección (dos padres por niño), cruce OX, y mutación.
3. Devuelve `mejor_ruta`, `mejor_distancia` y `historial` (mejor distancia por generación).

**Parámetros útiles a ajustar**:
- `generaciones`: más generaciones → mejor exploración pero mayor tiempo.
- `poblacion_size`: población más grande → mayor diversidad.
- `tasa_mutacion`: controla exploración local; valores típicos 0.05–0.3.

### `graficar_ruta(ruta, dist)`
Dibuja en Matplotlib:
- Ciudades como puntos etiquetados con su letra.
- Flechas dirigidas (`FancyArrowPatch`) entre ciudades en el orden de la ruta.
- Caja con la ruta final y la distancia total.

**Nota**: si deseas guardar la figura como PNG, reemplaza `plt.show()` por:
```python
plt.savefig('mejor_ruta.png', dpi=300, bbox_inches='tight')
```

### `graficar_convergencia(historial)`
Dibuja la curva del mejor valor encontrado por generación (útil para evaluar convergencia y comparar parámetros).

---

## Ejecución (ejemplo)

```bash
python tsp_genetico.py
```

Salida esperada (ejemplo):

```
Mejor ruta encontrada: ['A', 'C', 'D', 'F', 'G', 'H', 'E', 'B']
Distancia total: 22.345678
```

Después se muestran dos ventanas:
1. Gráfica con la mejor ruta (flechas entre nodos).
2. Gráfica de convergencia.

---

## Recomendaciones y mejoras propuestas

1. **Semilla para reproducibilidad**  
   Para resultados reproducibles añade al inicio:
   ```python
   random.seed(42)
   np.random.seed(42)
   ```

2. **Mejoras en selección y reemplazo**  
   - Implementar elitismo (mantener los k mejores de una generación a la siguiente).
   - Usar selección por ruleta o torneo de tamaño variable.

3. **Técnicas híbridas**  
   - Aplicar búsqueda local (2-opt) a cada hijo para afinar soluciones (memetic algorithm).

4. **Paralelización**  
   - Evaluar distancias en paralelo para poblaciones grandes (multiprocessing).

5. **Guardar resultados**  
   - Guardar la mejor ruta y la figura automáticamente en archivos para documentación.

---

## Preguntas frecuentes (FAQ)

**Q: ¿El algoritmo garantiza hallar la solución óptima?**  
A: No. Los AG son heurísticos que suelen encontrar buenas soluciones, pero no garantizan óptimo global. Ajustar parámetros y/o usar búsquedas locales mejora resultados.

**Q: ¿Puedo usar coordenadas reales distintas?**  
A: Sí. Cambia el diccionario `ciudades` por tus coordenadas y ejecuta de nuevo.

**Q: ¿Cómo comparar distintas tasas de mutación?**  
A: Ejecuta varias veces el AG cambiando `tasa_mutacion` y grafica la curva de convergencia de cada experimento en la misma figura.

---

## Licencia y autor

- Autor: Cristian (puedes reemplazar por tu nombre)
- Licencia: MIT (puedes adaptarla)

---

Si quieres, genero un archivo `README.md` actualizado en el ZIP del proyecto y lo dejo listo para descargar. ¿Quieres que lo incluya ahora?  
