# README02.md  
## Simulación ACO - Drones en Rescate

Este archivo documenta en detalle la implementación y resultados del **Punto 2** del proyecto: un sistema de drones que utilizan el algoritmo de **Colonias de Hormigas (ACO)** para misiones de rescate.  

---

## 📌 Descripción general

El código simula un **enjambre de drones** en un entorno de cuadrícula con obstáculos, supervivientes y una base de operaciones. Los drones emplean principios de **ACO (Ant Colony Optimization)** para:  

- **Maximizar la cobertura del área** de búsqueda.  
- **Localizar supervivientes** en ubicaciones aleatorias.  
- **Evitar obstáculos** y adaptarse a cambios en el entorno.  
- **Optimizar la energía consumida** en el proceso.  

---

## ⚙️ Configuración inicial

- **Tamaño del mapa:** 20x20.  
- **Número de drones:** 20.  
- **Iteraciones:** 100.  
- **Supervivientes:** 8.  
- **Obstáculos:** probabilidad del 15%.  
- **Base:** ubicada en `(0,0)`.  

---

## 🔬 Algoritmo ACO aplicado

- **Feromonas iniciales:** pequeñas cantidades distribuidas en la cuadrícula.  
- **Movilidad de drones:** cada drone explora en función de:
  - Feromonas acumuladas.  
  - Distancia (heurística).  
  - Penalización por revisitar zonas.  
- **Actualización de feromonas:**  
  - Evaporación controlada por `ρ`.  
  - Refuerzo proporcional al recorrido (`Q/L`).  
  - Refuerzo extra en posiciones con supervivientes encontrados.  

---

## 📊 Métricas calculadas

1. **Cobertura (%)**

2. **Supervivientes encontrados**: cantidad localizada vs. total.  

3. **Energía consumida**: pasos acumulados por todos los drones.  

---

## 🎨 Visualización

La figura generada al final de la simulación incluye:  

- **Obstáculos** → cuadrados negros.  
- **Base** → cuadrado azul.  
- **Supervivientes encontrados** → círculos verdes.  
- **Supervivientes no encontrados** → círculos rojos.  
- **Cobertura** → puntos amarillos.  
- **Feromonas** → mapa de calor (escala roja).  

Además, en la esquina inferior izquierda se muestran los valores de:  
- Porcentaje de cobertura.  
- Energía consumida.  
- Número de supervivientes encontrados.  

---

## 📈 Ejemplo de resultados

- **Cobertura alcanzada:** 62.4 %  
- **Supervivientes encontrados:** 6 de 8  
- **Energía consumida:** 120,000 unidades  

Interpretación:  
- El algoritmo logra coordinar drones descentralizados y explorar buena parte del entorno.  
- La cobertura no siempre es total, pero se optimiza el uso de recursos.  
- Los drones se adaptan dinámicamente al introducir nuevos obstáculos.  

---

## 📌 Conclusión

El uso de ACO en enjambres de drones permite:  
- Un comportamiento colectivo emergente.  
- Cobertura eficiente del terreno.  
- Búsqueda y rescate de supervivientes en condiciones adversas.  

Sin embargo, su rendimiento depende fuertemente de:  
- La calibración de parámetros (`α`, `β`, `ρ`, `Q`).  
- El número de drones disponibles.  
- La densidad de obstáculos en el terreno.  

---
