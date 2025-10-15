# 🐝 Simulación de Polinización con Drones - Algoritmo ABC (Artificial Bee Colony)

## 📘 Descripción General

Este proyecto implementa una **simulación del algoritmo ABC (Artificial Bee Colony)** aplicado a un **enjambre de drones polinizadores**.  
El objetivo principal es representar el comportamiento de las abejas artificiales (drones) en la búsqueda y polinización de flores, **considerando el consumo energético, la recarga automática y la priorización de tareas según el estado de batería**.

Cada dron actúa de forma autónoma, pero el sistema exhibe un **comportamiento colectivo inteligente**, optimizando la cobertura del área y garantizando la continuidad de la misión.

---

## ⚙️ Configuración General del Sistema

| Parámetro | Descripción | Valor |
|------------|--------------|--------|
| `AREA_SIZE` | Tamaño del área de simulación (m x m) | 10 |
| `N_DRONES` | Número de drones en el enjambre | 15 |
| `N_FLOWERS` | Número de flores a polinizar | 20 |
| `ITERATIONS` | Iteraciones de la simulación | 100 |
| `BATTERY_DECAY` | Tasa de descarga por movimiento | 0.02 |
| `RECHARGE_RATE` | Tasa de recarga por iteración | 0.05 |
| `BATTERY_THRESHOLD` | Nivel mínimo de batería para iniciar recarga | 0.2 |

---

## 🚁 Clases Principales

### **Clase `Drone`**
Representa un dron polinizador con las siguientes propiedades:
- `position`: coordenadas dentro del área de simulación.
- `battery`: nivel de energía actual (entre 0 y 1).
- `target`: objetivo actual (flor o estación de recarga).
- `recharging`: indica si el dron está en proceso de recarga.

**Comportamiento clave:**
- El dron se mueve hacia el objetivo con una velocidad proporcional a la distancia.
- Si la batería cae por debajo del umbral (`BATTERY_THRESHOLD`), el dron se dirige a la estación de recarga.
- Una vez cargado al 100%, retoma la polinización.

---

### **Clase `Flower`**
Modela una flor con posición aleatoria y estado (`activa` o `polinizada`):
- `active = True`: la flor está disponible para ser polinizada.
- `active = False`: la flor ha sido polinizada por algún dron.

---

## 🔄 Dinámica de Simulación

La simulación sigue la estructura de un ciclo continuo de comportamiento ABC:

1. **Búsqueda de flores activas:**  
   Los drones se asignan aleatoriamente a flores no polinizadas.

2. **Movimiento y polinización:**  
   Al alcanzar una flor, esta pasa al estado *polinizada* (verde en el gráfico).

3. **Gestión energética:**  
   Cada movimiento reduce la batería.  
   Cuando un dron cae por debajo del umbral energético, **interrumpe su tarea y se dirige a recargar**.

4. **Recarga automática:**  
   Los drones en la estación de recarga (ubicada en el origen `[0,0]`) recuperan energía hasta alcanzar el 100%.

5. **Reincorporación a la misión:**  
   Una vez recargados, los drones vuelven a asignarse a flores activas y continúan la polinización.

---

## 📊 Elementos Gráficos en la Animación

La simulación genera un **GIF dinámico** (`ABC_Drones_Polinizacion.gif`) con los siguientes elementos:

| Elemento | Color / Marcador | Descripción |
|-----------|------------------|--------------|
| 🌼 **Flores activas** | Amarillo (`x`) | Flores disponibles para polinizar |
| 🌿 **Flores polinizadas** | Verde | Flores ya polinizadas |
| 🚁 **Drones activos** | Verde / Amarillo / Rojo | Color indica nivel de batería |
| ⚡ **Estación de recarga** | Negro (`*`) | Punto de recarga energética |
| 📋 **Panel informativo** | Texto dinámico | Muestra estadísticas de cada iteración |

---

## 📈 Estadísticas Mostradas en Tiempo Real

Durante la ejecución, el cuadro informativo muestra:


### 🔍 Interpretación de las métricas:

- **Iteración:** indica el progreso total de la simulación.  
- **Flores polinizadas:** muestra el número de flores completadas frente al total.  
- **Batería promedio:** representa el nivel energético medio de todo el enjambre.  
- **Drones recargando:** contabiliza los drones que se encuentran en la estación de recarga.  

Estas métricas permiten monitorear tanto la eficiencia de polinización como el rendimiento energético del sistema.

---

## 🧠 Comportamiento Emergente del Enjambre

El modelo implementado demuestra varias propiedades clave de la **inteligencia de enjambre**:

- **Autonomía energética:** cada dron decide de manera individual cuándo recargar.  
- **Autoorganización:** el grupo mantiene una distribución equilibrada entre drones activos y recargando.  
- **Robustez colectiva:** la misión de polinización se mantiene estable incluso si varios drones están fuera de servicio temporalmente.  
- **Adaptabilidad:** la recarga automática evita la interrupción total de la tarea y mejora la eficiencia global.



