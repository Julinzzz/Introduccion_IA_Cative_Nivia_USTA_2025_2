import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------
AREA_SIZE = 10
N_DRONES = 15
N_FLOWERS = 20
ITERATIONS = 100
BATTERY_DECAY = 0.02
RECHARGE_RATE = 0.05
BATTERY_THRESHOLD = 0.2

np.random.seed(42)

# ------------------------------
# CLASES
# ------------------------------
class Drone:
    def __init__(self):
        self.position = np.random.rand(2) * AREA_SIZE
        self.battery = 1.0
        self.target = None
        self.recharging = False

    def move_to(self, target, step=0.2):
        if self.recharging:
            self.battery = min(1.0, self.battery + RECHARGE_RATE)
            if self.battery >= 1.0:
                self.recharging = False
            return
        direction = target - self.position
        if np.linalg.norm(direction) > 0.1:
            self.position += step * direction / np.linalg.norm(direction)
            self.battery -= BATTERY_DECAY
        if self.battery <= BATTERY_THRESHOLD:
            self.recharging = True

class Flower:
    def __init__(self):
        self.position = np.random.rand(2) * AREA_SIZE
        self.active = True

# ------------------------------
# FUNCIÓN DE SIMULACIÓN
# ------------------------------
def simulate_abc(n_drones, n_flowers, iterations):
    drones = [Drone() for _ in range(n_drones)]
    flowers = [Flower() for _ in range(n_flowers)]
    recharge_station = np.array([0, 0])

    # Configurar figura
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, AREA_SIZE)
    ax.set_ylim(0, AREA_SIZE)
    ax.set_title("ABC - Polinización con Drones (con recarga y batería)", fontsize=10, weight='bold')
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_aspect("equal")

    # Elementos del gráfico
    flowers_sc = ax.scatter([], [], c="gold", marker="x", s=80, label="🌼 Flores activas")
    pollinated_sc = ax.scatter([], [], c="green", s=70, label="🌿 Flores polinizadas")
    drones_sc = ax.scatter([], [], s=80, label="🚁 Drones (color = batería)")
    recharge_sc = ax.scatter(*recharge_station, c="black", marker="*", s=150, label="⚡ Estación de recarga")
    info_text = ax.text(0.02, 0.97, "", transform=ax.transAxes, fontsize=9,
                        verticalalignment="top", bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"))

    ax.legend(loc="upper right", fontsize=8, framealpha=0.8)

    def init():
        flowers_sc.set_offsets(np.empty((0, 2)))
        pollinated_sc.set_offsets(np.empty((0, 2)))
        drones_sc.set_offsets(np.empty((0, 2)))
        return flowers_sc, pollinated_sc, drones_sc, recharge_sc, info_text

    def update(frame):
        active_positions = [f.position for f in flowers if f.active]
        pollinated_positions = [f.position for f in flowers if not f.active]
        drone_positions = []
        drone_colors = []

        for d in drones:
            if not d.recharging:
                # Si no tiene objetivo o ya lo alcanzó
                if d.target is None or np.linalg.norm(d.target - d.position) < 0.5:
                    available = [f for f in flowers if f.active]
                    if available:
                        d.target = available[np.random.randint(len(available))].position
                    else:
                        d.target = recharge_station

                d.move_to(d.target)
                # Si alcanzó flor activa, poliniza
                for f in flowers:
                    if f.active and np.linalg.norm(d.position - f.position) < 0.4:
                        f.active = False
            else:
                d.move_to(recharge_station)

            drone_positions.append(d.position)
            # Color según batería
            if d.battery > 0.6:
                drone_colors.append("limegreen")
            elif d.battery > 0.3:
                drone_colors.append("gold")
            else:
                drone_colors.append("red")

        # Evitar errores de listas vacías
        flowers_sc.set_offsets(np.array(active_positions) if active_positions else np.empty((0, 2)))
        pollinated_sc.set_offsets(np.array(pollinated_positions) if pollinated_positions else np.empty((0, 2)))
        drones_sc.set_offsets(np.array(drone_positions) if drone_positions else np.empty((0, 2)))
        drones_sc.set_color(drone_colors)

        avg_battery = np.mean([d.battery for d in drones])
        recharging_count = sum([d.recharging for d in drones])
        pollinated_count = sum([not f.active for f in flowers])
        info_text.set_text(
            f"Iteración: {frame+1}/{iterations}\n"
            f"Flores polinizadas: {pollinated_count} / {n_flowers}\n"
            f"Batería promedio: {avg_battery:.2f}\n"
            f"Drones recargando: {recharging_count}"
        )

        return flowers_sc, pollinated_sc, drones_sc, recharge_sc, info_text

    ani = FuncAnimation(fig, update, frames=iterations, init_func=init, blit=False, repeat=False)
    ani.save("ABC_Drones_Polinizacion.gif", writer="pillow", fps=5)
    plt.close(fig)

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    simulate_abc(N_DRONES, N_FLOWERS, ITERATIONS)
    print("✅ Simulación completada: ABC_Drones_Polinizacion.gif generado correctamente.")
