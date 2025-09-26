# Búsqueda Coordinada con PSO para Drones de Rescate (5×5 km)

**Autor:** Julian Yesid Nivia Mendez  

---

## 1. Propósito del documento

Este documento describe, el diseño, la implementación en Python de un algoritmo de **Optimización por Enjambre de Partículas (PSO)** para coordinar un equipo de **10 drones** que realizan una misión de búsqueda y rescate en una zona costera **5×5 km** tras un evento de tsunami. El objetivo del algoritmo es **maximizar la probabilidad de hallar supervivientes** cubriendo con sensores las zonas más prometedoras del mapa, **respetando restricciones operativas** (distancia máxima por dron) y desincentivando **solapamientos redundantes**. Este algoritmo, corresponde al Quiz #5 del espacio académico.

---

## 2. Planteamiento del problema

### 2.1. Contexto
Tras un desastre natural, se requiere planear rápidamente trayectorias para múltiples drones que, actuando de forma coordinada, inspeccionen un área extensa priorizando regiones con mayor **probabilidad a priori** de hallar señales de vida. Este problema es representativo de **Introducción a la IA** por integrar: modelado del entorno, función objetivo compuesta, optimización estocástica y análisis de trade–offs (cobertura vs. redundancia vs. restricciones físicas).

### 2.2. Dominio y unidades
- Área rectangular: [0,5000] m × [0,5000] m.
- Número de drones: N = 10.
- Radio de detección del sensor: r = 200 m.
- Velocidad de crucero: v = 12 m/s.
- Tiempo máximo de misión: T = 120 min = 7200 s.
- Presupuesto de recorrido por dron: B = v·T = 86.4 km.

### 2.3. Variables de decisión
Cada dron visita W waypoints en orden (por defecto W = 4). Para N drones se optimizan 2·N·W variables continuas (coordenadas x,y en metros).

### 2.4. Mapa de probabilidad
El entorno se discretiza en una malla regular **GRID × GRID** (por defecto **100 × 100**). Cada celda c almacena una probabilidad relativa P(c) ∈ [0,1] de hallar supervivientes. En ausencia de un mapa real, el código genera un **mapa sintético** mediante mezcla de gaussianas más un término de ruido suave, normalizado a [0,1].

---

## 3. Formulación matemática

### 3.1. Cobertura
Sea S_d el conjunto de celdas cubiertas por el dron d (celda cubierta si la distancia desde el centro de la celda a **algún** waypoint del dron es ≤ r). La **cobertura total** es la unión S.

### 3.2. Penalización por solapamiento
Para fomentar la **diversidad espacial**, se penaliza la cobertura con alta redundancia. Si m(c) es el número de drones que cubren la celda c, el solapamiento relevante es max(m(c)−1, 0). Se descuenta una fracción α de la probabilidad acumulada en celdas solapadas (en el código α = 0.10).

### 3.3. Restricción de recorrido
La longitud de ruta del dron d (partiendo de (0,0)), donde p_i son los waypoints y s=(0,0). Si L_d > B se penaliza linealmente el exceso con factor β grande (en el código β = 10^4 sobre kilómetros excedidos).

### 3.4. Función objetivo (maximización)
Maximizar:

J

Como el PSO implementado **minimiza**, se usa −J como costo.

---

## 4. Algoritmo de Optimización por Enjambre de Partículas (PSO)

### 4.1. Idea central
PSO mantiene una **población de partículas** (soluciones candidatas). Cada partícula x_i tiene una **mejor posición personal** p_i y el enjambre guarda la **mejor global** g. En cada iteración:
Parámetros típicos usados: ω = 0.72, c1 = c2 = 1.49.

### 4.2. Razones para PSO en este contexto
- Maneja **variables continuas** con **no convexidad** (uniones y penalizaciones).
- Es **simple de implementar** y ajustar en un curso introductorio.
- Permite **paralelizar la evaluación** de partículas si se desea.

---

## 5. Estructura del código

Archivo: `Nivia_Julian_Quiz_5.py`.

1) **Parámetros del problema**: tamaño del área, número de drones, radio del sensor, velocidad, tiempo, W, GRID, semilla SEED.
2) **Generación del mapa de probabilidad**: `build_probability_map()` produce `PROB ∈ [0,1]^{GRID×GRID}` mediante mezcla de gaussianas.
3) **Funciones de apoyo**:
   - `coverage_mask_from_points(points_xy, radius)`: máscara booleana de celdas cubiertas por una lista de waypoints.
   - `route_length(points_xy, start=(0,0))`: longitud de la ruta concatenada desde el origen.
   - `decode_position(x)`: mapea el vector plano de decisión a listas de W puntos por dron.
4) **Función objetivo `objective(x)`**: computa −J combinando cobertura, solapamiento y penalización de recorrido.
5) **Clase `PSO`**: implementación ligera con inicialización, actualización por iteración y seguimiento de mejores personales y globales.
6) **Bloque main**: ejecuta la optimización, reporta métricas e **incluye visualización** de trayectorias y discos de cobertura sobre el mapa.

---

## 6. Decisiones de modelado y supuestos

- **Waypoints discretos por dron (W=4)**: compromiso entre expresividad de trayectorias y tiempo de cómputo.
- **Cobertura por discos en cada waypoint**: representa barridos locales (patrones de búsqueda) alrededor de puntos clave.
- **Punto de partida común (0,0)**: fácil de modificar si cada dron despega desde ubicaciones distintas.
- **Recorrido sin regreso a base**: se modela el tramo de ida; añadir retorno es inmediato sumando ||s − p_W||.
- **Mapa sintético**: permite probar el algoritmo sin datos reales. Sustituible por un raster real [0,1] manteniendo dimensiones GRID×GRID.

---

## 7. Complejidad y rendimiento

- **Evaluación de cobertura**: distancia de GRID^2 celdas a K = N·W puntos. Complejidad O(GRID^2·K). Para GRID=100 y K=40 es manejable en portátil.
- **Memoria**: la matriz de distancias puede ser grande; si se aumenta GRID o W, conviene **bloquear la evaluación** por lotes.
- **Paralelización**: la evaluación por partículas es independiente; puede vectorizarse o distribuirse.

---

## 8. Uso y ejecución

### 8.1. Dependencias
- Python 3.9+
- numpy, matplotlib

### 8.2. Ejecución
```bash
python Nivia_Julian_Quiz_5.py
```

El script imprime métricas por dron (distancia) y totales (porcentaje de masa de probabilidad cubierta, solapamiento penalizado y valor de la función objetivo), y muestra una figura con:
- **Mapa de probabilidad** (fondo).
- **Trayectorias óptimas** desde (0,0) hacia los waypoints de cada dron.
- **Discos de cobertura** de radio SENSOR_R alrededor de cada waypoint.

### 8.3. Personalización rápida
- `W`: más flexibilidad de ruta (costo computacional mayor).
- `GRID`: refina la malla del mapa (mayor precisión/costo).
- `SENSOR_R`, `SPEED`, `T_MAX_MIN`: adaptan el modelo físico.
- Coeficientes de penalización (`alpha`, `beta` en `objective`) para balancear **exploración vs. redundancia** y **restricciones**.

---

## 9. Validación y verificación básica

- **Reproducibilidad**: se utiliza `SEED=42`. Cambiar la semilla generará mapas y trayectorias distintas.
- **Sanidad geométrica**: las coordenadas se recortan a [0, AREA]. El radio de detección se aplica de forma isotrópica.
- **Límites de recorrido**: si L_d ≫ B, la penalización domina y empuja a rutas más cortas.
- **Cobertura efectiva**: la métrica principal no es “área geométrica” sino **masa de probabilidad**; cubrir 20% del área con alta probabilidad puede ser **mejor** que 40% en zonas frías.

---

## 10. Extensiones recomendadas

1. **Mapa real**: cargar GeoTIFF/PNG con probabilidades estimadas por modelos de percepción o informes humanitarios.
2. **Costo energético**: reemplazar la longitud de ruta por **consumo de batería** dependiente de viento, carga útil y maniobras.
3. **Dinámica de movimiento**: modelar cinemática y **tiempos de barrido** locales por patrón (lawnmower, espiral).
4. **Evitar colisiones y no–fly zones**: restricciones de separación y polígonos prohibidos.
5. **Replaneación online (MPC)**: ejecutar PSO en ventanas deslizantes con retroalimentación sensorial.
6. **Multi–objetivo**: pasar a **NSGA‑II** para explorar frentes (cobertura, tiempo, energía).
7. **Asignación tarea–región**: descomponer por **clustering** de altas probabilidades y luego optimizar rutas intra–cluster.

---

## 11. Mapa de símbolos y variables

| Símbolo / Variable | Significado | Valor por defecto |
|---|---|---|
| `AREA` | Longitud del lado del cuadrado (m) | 5000 |
| `N_DRONES` | Número de drones | 10 |
| `W` | Waypoints por dron | 4 |
| `SENSOR_R` | Radio de detección (m) | 200 |
| `SPEED` | Velocidad (m/s) | 12 |
| `T_MAX_MIN` | Tiempo máximo (min) | 120 |
| `BUDGET_PER_DRONE` | Presupuesto de recorrido (m) | `SPEED*T_MAX` |
| `GRID` | Resolución de la malla | 100 |
| `SEED` | Semilla aleatoria | 42 |

---

## 12. Conclusión

El ejercicio implementa un sistema de **planificación de cobertura** con múltiples drones, combinando modelado probabilístico del entorno y **optimización heurística** (PSO). El diseño privilegia la **cobertura de alta probabilidad**, desincentiva solapamientos innecesarios y respeta **restricciones operativas**. El marco es extensible a escenarios más realistas e integra de manera natural otros enfoques de IA (aprendizaje para estimar mapas, métodos multi–objetivo y control en línea).

---
