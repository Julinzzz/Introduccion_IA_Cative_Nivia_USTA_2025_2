import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parámetros del campo de potencial
K_atractivo = 0.5
K_repulsivo = 3.0
radio_repulsion = 3.0

# Función para calcular el campo de potencial
def calcular_potencial(posicion_agente, objetivo, obstaculos, epsilon=0.25):
    # Potencial de atracción hacia el objetivo
    potencial_atractivo = 0.5 * K_atractivo * np.linalg.norm(objetivo - posicion_agente)**2
    
    # Potencial de repulsión de los obstáculos
    potencial_repulsivo = 0
    for obstaculo in obstaculos:
        distancia = np.linalg.norm(posicion_agente - obstaculo)
        if 1 <= distancia < radio_repulsion:
            potencial_repulsivo += 0.5 * K_repulsivo * (1 / distancia - 1 / radio_repulsion)**2
        elif epsilon < distancia < 1:
            potencial_repulsivo += 0.5 * K_repulsivo * (1 / distancia - 1 / radio_repulsion)
        else:
            potencial_repulsivo += 0

    # Potencial total como suma de los potenciales de atracción y repulsión
    potencial_total = potencial_atractivo + potencial_repulsivo
    return potencial_total

# Función para calcular el gradiente del campo de potencial en un punto dado
def calcular_gradiente(posicion_agente, objetivo, obstaculos, epsilon=0.15):
    gradiente = np.zeros(2)
    for i in range(2):
        delta_pos = np.zeros(2)
        delta_pos[i] = epsilon
        potencial_pos = calcular_potencial(posicion_agente + delta_pos, objetivo, obstaculos)
        potencial_neg = calcular_potencial(posicion_agente - delta_pos, objetivo, obstaculos)
        gradiente[i] = (potencial_pos - potencial_neg) / (2 * epsilon)
    return gradiente

# Función de actualización para la animación
def update(frame):
    global agente_posicion, historial_energia_potencial
    # Calcula el gradiente del campo de potencial en la posición actual del agente
    gradiente = calcular_gradiente(agente_posicion, objetivo, obstaculos)
    # Actualiza la posición del agente en función del gradiente
    agente_posicion -= gradiente * 0.1  # Multiplicamos por un factor de aprendizaje para controlar la velocidad de movimiento
    
    # Calcula y almacena la energía potencial en el historial
    energia_potencial = calcular_potencial(agente_posicion, objetivo, obstaculos)
    historial_energia_potencial.append(energia_potencial)
    
    
    # Actualiza la posición del agente en la visualización
    ax.clear()
    ax.scatter(agente_posicion[0], agente_posicion[1], color='red', marker='o', s=200)  # Dibuja la posición del agente
    ax.scatter(objetivo[0], objetivo[1], color='green', marker='x', s=100)  # Dibuja el objetivo
    for obstaculo in obstaculos:
        ax.scatter(obstaculo[0], obstaculo[1], color='black', marker='x', s=100)  # Dibuja los obstáculos
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)
    ax.set_title('Movimiento del Agente hacia el Objetivo')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # Muestra la energía potencial a lo largo del tiempo
    ax2.clear()
    ax2.plot(historial_energia_potencial, label='Energía Potencial')
    ax2.set_title('Evolución de la Energía Potencial')
    ax2.set_xlabel('Iteración')
    ax2.set_ylabel('Energía Potencial')
    ax2.legend()

# Configuración inicial de la visualización
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Parámetros y variables iniciales
agente_posicion = np.array([1.0, 1.0])  # Posición inicial del agente
objetivo = np.array([12, 12])  # Posición del objetivo
#Prueba con Varios Obstáculos
#obstaculos = np.array([[3, 4], [8, 6]])  # Posiciones de los obstáculos-Número= 2 Obstáculos
#obstaculos = np.array([[3, 4],[5, 5], [8, 6]])  # Posiciones de los obstáculos-Número= 3 Obstáculos
#obstaculos = np.array([[3, 4],[6, 5], [8, 8],[10,9]])  # Posiciones de los obstáculos-Número= 4 Obstáculos
#obstaculos = np.array([[3, 4],[6, 5], [8, 8],[10,9],[11,10],[12,10]])  # Posiciones de los obstáculos-Número= 6 Obstáculos
#Obstáculos más complejos
#obstaculos = np.array([[2, 3],[2, 4],[3, 3],[3,4],[4, 5],[4, 6],[5, 5],[5,6],[6, 7],[6, 8], [7, 7],[7,8],[8, 9],[8, 10], [9, 9],[9,10],[10,10],[11,11]])  # Posiciones de los obstáculos-Número= 18 Obstáculos
#obstaculos = np.array([[2, 3],[2, 4],[3, 3],[3,4],[4,3],[4,4],[5,3],[5,4],  [4, 5],[4, 6], [5, 5],[5,6],[6, 7],[6, 8], [7, 7],[7,8],[8,7],[8,8],[9,7],[9,8],[8, 9],[8, 10], [9, 9],[9,10],[10,10],[10,11],[11,10],[11,11]])  # Posiciones de los obstáculos-Número= 28 Obstáculos
#obstaculos = np.array([[2, 3],[2, 4],[3, 3],[3,4],[4,3],[4,4],[5,3],[5,4],  [7, 5],[7, 6],[8, 5],[8,6],  [9, 7],[9, 7],[10, 8],[10,8], [11, 7],[11, 8],[12, 7],[12,8]])  # Posiciones de los obstáculos-Número= 18 Obstáculos
#obstaculos = np.array([[2, 3],[2, 4],[3, 3],[3,4], [5,3],[5,4],[6,3],[6,4], [5, 5],[5, 6],[6, 5],[6,6],  [7, 5],[7, 6],[8, 5],[8,6],  [5, 9],[5, 10],[6, 9],[6,10],  [7, 9],[7, 10],[8, 9],[8,10], [10, 8],[10, 9],[11, 8],[11,9], [12, 8],[12, 9],[13, 8],[13,9]])  # Posiciones de los obstáculos-Número= 28 Obstáculos
#Ejercicio que no puede resolver
#obstaculos = np.array([[2, 3],[2, 4],[3, 3],[3,4],[4, 5],[4, 6], [5, 5],[5,6],[6, 7],[6, 8], [7, 7],[7,8],[8,5],[8,6],[9,5],[9,6],[8, 9],[8, 10], [9, 9],[9,10],[10,10],[11,11]])  # Posiciones de los obstáculos-Número= 22 Obstáculos

#Herradura
obstaculos = np.array([[2, 2],[2, 3], [2, 4],[2, 5],[2, 6],[2, 7],[2, 8],[2, 9], [2, 10],[10, 10], 
                        [10, 9],[10, 8],[10, 7],[10, 6],[10, 5],[10, 4],[10, 3],[10, 2], 
                        [9, 2], [9, 3],[9, 4],[9, 5],[9, 6],[9, 7],[9, 8],[9, 9], 
                        [3, 9],[3, 8],[3, 7],[3, 6],[3, 5],[3, 4],[3, 3], [3, 2],
                        [4,9],[5,9],[6,9],[7,9],[8,9],[3,10],[4,10],[5,10],[6,10],
                        [7,10],[8,10],[9,10]])


historial_energia_potencial = []  # Historial de la energía potencial

# Generación de la animación
ani = FuncAnimation(fig, update, frames=200, interval=200)
plt.show()
