import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def calcular_potencial(posicion_agente, objetivo, obstaculos):
    potencial_atractivo = 0.5 * K_atractivo * np.linalg.norm(objetivo - posicion_agente)**2
    
    potencial_repulsivo = 0
    for obstaculo in obstaculos:
        distancia = np.linalg.norm(posicion_agente - obstaculo)
        if distancia < radio_repulsion:
            potencial_repulsivo += 0.5 * K_repulsivo * (1/distancia - 1/radio_repulsion)**2
    
    potencial_total = potencial_atractivo + potencial_repulsivo
    return potencial_total

def calcular_direccion(posicion_agente, objetivo, obstaculos, delta=0.01):
    gradiente_x = (calcular_potencial([posicion_agente[0] + delta, posicion_agente[1]], objetivo, obstaculos) - 
                    calcular_potencial([posicion_agente[0] - delta, posicion_agente[1]], objetivo, obstaculos)) / (2 * delta)
    
    gradiente_y = (calcular_potencial([posicion_agente[0], posicion_agente[1] + delta], objetivo, obstaculos) - 
                    calcular_potencial([posicion_agente[0], posicion_agente[1] - delta], objetivo, obstaculos)) / (2 * delta)
    
    return np.array([gradiente_x, gradiente_y], dtype=np.float64)

def visualizar_campo_potencial(objetivo, obstaculos, trayectoria):
    x_range = np.linspace(-2, 12, 100)
    y_range = np.linspace(-2, 12, 100)
    potencial_grid = np.zeros((len(x_range), len(y_range)))

    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            posicion_agente = np.array([x, y])
            potencial_grid[i, j] = calcular_potencial(posicion_agente, objetivo, obstaculos)

    fig, ax = plt.subplots()
    contorno = ax.contourf(x_range, y_range, potencial_grid, cmap='viridis', levels=20)
    
    def update(frame):
        if frame < len(trayectoria):
            x, y = trayectoria[frame]
            ax.plot(x, y, 'bo', markersize=8)
    
    ani = FuncAnimation(fig, update, frames=len(trayectoria), repeat=False)
    
    # Contornos para obstáculos
    for obstaculo in obstaculos:
        plt.scatter(obstaculo[0], obstaculo[1], color='black', marker='x', s=100, linewidth=2)
    
    # Contorno para el objetivo
    plt.scatter(objetivo[0], objetivo[1], color='red', marker='o', s=100, linewidth=2)
    
    plt.colorbar(contorno, label='Campo de Potencial')
    plt.title('Campo de Potencial Artificial')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

# Parámetros del campo de potencial
K_atractivo = 0.5
K_repulsivo = 1.0
radio_repulsion = 5.0

# Definir posición del objetivo y posiciones de obstáculos
objetivo = np.array([10, 10], dtype=np.float64)
obstaculos = np.array([[2, 2], [2, 2.7], [2.7, 2.7],[2.7, 2],], dtype=np.float64)

# Simular el movimiento del agente y almacenar la trayectoria
trayectoria = []
posicion_actual = np.array([0, 0], dtype=np.float64)
for _ in range(100):
    trayectoria.append(posicion_actual.copy())
    direccion = -calcular_direccion(posicion_actual, objetivo, obstaculos)  # Corrección aquí
    posicion_actual += 0.1 * direccion  # Ajustar la tasa de aprendizaje según sea necesario

# Visualizar el campo de potencial animado con la trayectoria del objetivo
visualizar_campo_potencial(objetivo, obstaculos, trayectoria)
