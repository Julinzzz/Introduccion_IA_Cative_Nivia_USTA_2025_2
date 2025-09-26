# 🛰️ Optimización de Búsqueda con Drones usando PSO

Este proyecto implementa un **algoritmo de Optimización por Enjambre de Partículas (PSO)** para coordinar un equipo de **10 drones autónomos** en un área de **5 km × 5 km**, con el objetivo de **maximizar la probabilidad de encontrar sobrevivientes y cubrir la mayor zona posible** después de un desastre natural.

---

## 📖 Contexto

Tras un evento catastrófico (por ejemplo, un **tsunami** o una **inundación masiva**), una zona costera de 25 km² queda afectada y se reportan personas desaparecidas.  

Se requiere desplegar drones equipados con sensores de búsqueda en un área de difícil acceso para humanos. El reto es definir cómo **posicionar y coordinar los drones** para:  

1. Cubrir la mayor área posible.  
2. Maximizar la probabilidad de detectar sobrevivientes.  
3. Evitar redundancia manteniendo a los drones dispersos.  

---

## ⚙️ Datos del Problema

- **Área de búsqueda:** 5 km × 5 km (5000 × 5000 metros).  
- **Número de drones:** 10.  
- **Radio de detección:** 200 m por dron.  
- **Tiempo de búsqueda máximo:** 120 minutos (simulación).  
- **Mapa de probabilidades:** incluye "hotspots" o zonas con mayor probabilidad de supervivientes.  

Cada dron debe ubicarse en una coordenada `(x, y)` dentro del área. El algoritmo optimiza estas posiciones.  

---

## 🚀 Algoritmo PSO

El **Particle Swarm Optimization (PSO)** es un algoritmo bioinspirado en el comportamiento de **bandadas de aves** y **bancos de peces**.  

En este caso:  
- Cada **partícula** representa una posible configuración de **10 drones** (20 variables: coordenadas x,y de cada dron).  
- Las partículas se mueven en el espacio de búsqueda ajustando su posición y velocidad en función de:  
  - su mejor solución personal (`pbest`),  
  - la mejor solución global del enjambre (`gbest`).  

### 🔢 Función Objetivo
La evaluación de cada configuración de drones combina tres métricas:  

1. **Probabilidad cubierta (`prob_cubierta`)**  
   - Suma de probabilidades en las celdas dentro del radio de detección de algún dron.  

2. **Área cubierta (`area_pct`)**  
   - Porcentaje de celdas del área total que quedan dentro de algún radio de detección.  

3. **Dispersión (`spread`)**  
   - Distancia media entre drones, normalizada.  
   - Evita que todos se concentren en un mismo punto.  

La función objetivo final es una **combinación ponderada** de estas tres métricas.  

---

## 📊 Ejemplo de salida

Durante la ejecución, el programa muestra información por iteración:

```
Iter 200/250  Score=0.08298  prob_cubierta=469.368  area_pct=5.14%  spread=0.4054  tiempo=56.2s
```

### Significado:
- **Iter 200/250** → Iteración actual / total de iteraciones.  
- **Score** → Valor de la función objetivo combinada (mientras más alto, mejor).  
- **prob_cubierta** → Probabilidad total captada por los drones.  
- **area_pct** → Porcentaje del área de 5×5 km cubierta.  
- **spread** → Dispersión de drones (0 = juntos, 1 = muy separados).  
- **tiempo** → Tiempo transcurrido en segundos desde el inicio.  

---

## 📈 Visualizaciones

El programa genera tres gráficas principales:

1. **Mapa de probabilidad + drones finales**  
   - Fondo: mapa de probabilidad.  
   - Puntos: posiciones finales de cada dron.  
   - Círculos: radios de detección (200 m).  

2. **Evolución del Score**  
   - Muestra cómo mejora la optimización con cada iteración.  

3. **Mapa de Cobertura**  
   - Muestra qué zonas del área quedaron cubiertas al final.  

---

## 🖥️ Ejecución en Visual Studio Code

### 1. Requisitos
- Python 3.8 o superior.  
- Librerías necesarias:
  ```bash
  pip install numpy matplotlib
  ```

### 2. Pasos
1. Abrir la carpeta del proyecto en **Visual Studio Code**.  
2. Crear un archivo `pso_drones_optimizado.py` y pegar el código del proyecto.  
3. Abrir la terminal en VS Code y ejecutar:  
   ```bash
   python pso_drones_optimizado.py
   ```

---

## 📌 Posibles mejoras

- Optimización de **trayectorias dinámicas** en lugar de posiciones estáticas.  
- Considerar **restricciones de batería** o **zonas prohibidas**.  
- Exportar resultados en formatos como **CSV/KML** para integración con mapas reales.  
- Simulación en tiempo real con software de control de drones.  

---

✍️ **Autores:** Proyecto académico de optimización por enjambre de partículas aplicado a búsqueda y rescate con drones.  
