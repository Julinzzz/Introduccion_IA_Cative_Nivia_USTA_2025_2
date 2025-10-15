# Documentación del Código: PSO aplicado a Drones en Formación

## 1. Introducción
Este código implementa un modelo de **Optimización por Enjambre de Partículas (PSO)** aplicado al control de un conjunto de drones.  
El objetivo principal es organizar drones en formaciones predefinidas (estrella, robot y dragón), considerando:
- Fallos en algunos drones.
- Presencia de obstáculos en el espacio.
- Comportamiento colectivo emergente basado en la lógica de PSO.

Se incluye un módulo de visualización en **matplotlib** para observar la dinámica de los drones en cada formación.

---

## 2. Estructura General del Código

El código se divide en los siguientes bloques principales:

### 2.1 Configuración Inicial
- **Número de drones (`N_DRONES`)**: Cantidad de agentes en el enjambre.
- **Número de iteraciones (`ITERATIONS`)**: Duración de la simulación.
- **Fallos (`FAILURE_ITER`, `FAILURE_INDEX`)**: Iteración y dron en el que ocurre una falla.
- **Parámetros de PSO (`W`, `C1`, `C2`)**:
  - `W`: coeficiente de inercia.
  - `C1`: componente cognitiva (aprendizaje individual).
  - `C2`: componente social (influencia del grupo).
- **Obstáculos (`OBSTACLES`)**: Representados como círculos en el espacio.

---

### 2.2 Clase `Drone`
Cada dron es un agente autónomo definido por:
- **Atributos**:
  - `idx`: identificador único.
  - `position`: posición actual en el plano.
  - `velocity`: vector de velocidad.
  - `alive`: estado (activo o fallido).
- **Métodos**:
  - `move()`: actualiza la posición del dron en función de su velocidad.

---

### 2.3 Clase `Swarm`
Gestiona al conjunto de drones:
- **Inicialización**:
  - Genera un enjambre de drones en posiciones aleatorias.
  - Define la **formación objetivo** según el patrón elegido (`estrella`, `robot`, `dragon`).
- **Métodos principales**:
  - `generate_targets(formation)`: Calcula los puntos objetivo que conforman la figura deseada.
  - `step()`: Actualiza la posición de cada dron considerando:
    - **Cognición individual**: atracción hacia su objetivo específico.
    - **Componente social**: atracción hacia el centro de masa del enjambre.
    - **Evitación de obstáculos**: desviación de trayectorias peligrosas.
    - **Fallas**: algunos drones dejan de actualizarse en la simulación.
  - Actualiza `pbest` (mejor posición individual) y `gbest` (mejor posición global).

---

### 2.4 Visualización: `animate_swarm`
- Genera animaciones usando `matplotlib.animation.FuncAnimation`.
- Representa gráficamente:
  - **Drones activos**: puntos azules.
  - **Drones fallidos**: puntos rojos.
  - **Objetivos de la formación**: cruces verdes.
  - **Obstáculos**: círculos grises.
- Exporta las animaciones en formato `.gif`.

---

### 2.5 Función Principal `main`
- Ejecuta simulaciones para las tres formaciones:
  1. **Estrella**  
  2. **Robot**  
  3. **Dragón**  
- Llama a `animate_swarm` para generar los GIFs correspondientes:
  - `drones_estrella.gif`
  - `drones_robot.gif`
  - `drones_dragon.gif`

---

## 3. Flujo de Ejecución
1. Inicialización de parámetros y configuración.
2. Creación del enjambre con la clase `Swarm`.
3. Generación de los puntos objetivo según la formación seleccionada.
4. Iteración de la simulación:
   - Movimiento de cada dron (PSO).
   - Actualización de estados (fallos, posiciones, mejores soluciones).
5. Visualización animada de la evolución del enjambre.
6. Exportación de resultados en GIF.

---

## 4. Resultados Esperados
- Los drones forman patrones predefinidos (estrella, robot, dragón).
- El enjambre mantiene la cohesión incluso ante fallos individuales.
- Los obstáculos modifican las trayectorias de los drones.
- Se evidencia el comportamiento adaptativo del algoritmo PSO.

---

## 5. Conclusión
Este código demuestra la viabilidad de aplicar **PSO en sistemas multiagente** para coordinar drones en formaciones complejas, considerando entornos dinámicos con fallos y obstáculos.  
El enfoque es escalable y puede extenderse a otros escenarios de cooperación en robótica.

---
