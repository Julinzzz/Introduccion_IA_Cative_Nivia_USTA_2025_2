import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------
# Configuración
# ------------------------------
N_DRONES = 60
ITERATIONS = 100
FAILURE_ITER = 50   # en qué iteración falla un dron
FAILURE_INDEX = 5   # índice del dron que falla

# Parámetros PSO
W = 0.5
C1 = 1.2
C2 = 0.3
OBSTACLES = [(0, 0, 2)]  # ejemplo: obstáculo circular en el centro

# ------------------------------
# Clases
# ------------------------------
class Drone:
    def __init__(self, idx, position):
        self.idx = idx
        self.position = np.array(position, dtype=float)
        self.velocity = np.random.rand(2) * 0.5
        self.alive = True

    def move(self):
        if self.alive:
            self.position += self.velocity * 0.1

class Swarm:
    def __init__(self, n, formation="estrella"):
        self.drones = [Drone(i, np.random.rand(2) * 15 - 7.5) for i in range(n)]
        self.formation = formation
        self.targets = self.generate_targets(formation)
        self.pbest = [d.position.copy() for d in self.drones]
        self.gbest = np.mean([d.position for d in self.drones], axis=0)

    def generate_targets(self, formation):
        if formation == "estrella":
            pts = []
            R = 6   # radio externo
            r = 2.5 # radio interno
            angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
            for i, a in enumerate(angles):
                if i % 2 == 0:
                    pts.append(np.array([R*np.cos(a - np.pi/2), R*np.sin(a - np.pi/2)]))
                else:
                    pts.append(np.array([r*np.cos(a - np.pi/2), r*np.sin(a - np.pi/2)]))
            # bordes
            extended_pts = []
            for i in range(len(pts)):
                start, end = pts[i], pts[(i+1)%len(pts)]
                line_x = np.linspace(start[0], end[0], 4)
                line_y = np.linspace(start[1], end[1], 4)
                for j in range(len(line_x)):
                    extended_pts.append(np.array([line_x[j], line_y[j]]))
            idxs = np.linspace(0, len(extended_pts)-1, len(self.drones)).astype(int)
            return [extended_pts[i] for i in idxs]

        elif formation == "robot":
            pts = []
            side = 8
            x_vals = np.linspace(-side/2, side/2, 10)
            y_vals = np.linspace(-side/2, side/2, 10)
            for x in x_vals:
                pts.append(np.array([x, -side/2]))
                pts.append(np.array([x, side/2]))
            for y in y_vals:
                pts.append(np.array([-side/2, y]))
                pts.append(np.array([side/2, y]))
            eye_r = 1.0
            eye_angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
            for a in eye_angles:
                pts.append(np.array([-2 + eye_r*np.cos(a), 2 + eye_r*np.sin(a)]))
                pts.append(np.array([ 2 + eye_r*np.cos(a), 2 + eye_r*np.sin(a)]))
            mouth_x = np.linspace(-2, 2, 6)
            for x in mouth_x:
                pts.append(np.array([x, -2]))
            pts.append(np.array([-1, side/2 + 1]))
            pts.append(np.array([-2, side/2 + 2]))
            pts.append(np.array([1, side/2 + 1]))
            pts.append(np.array([2, side/2 + 2]))
            idxs = np.linspace(0, len(pts)-1, len(self.drones)).astype(int)
            return [pts[i] for i in idxs]

        elif formation == "dragon":
            pts = []
            body_y = np.linspace(-2, 3, 12)
            for i, y in enumerate(body_y):
                width = 0.3 if y < 1 else 0.6
                pts.append(np.array([0, y]))
                if i % 2 == 0:
                    pts.append(np.array([width, y]))
                    pts.append(np.array([-width, y]))
            wing_span = np.linspace(0, 2.5, 10)
            for y in wing_span:
                x = 5 - y*1.5
                for dx in [0, 0.5, -0.5]:
                    pts.append(np.array([x+dx, y]))
                    pts.append(np.array([-x-dx, y]))
            tail_y = np.linspace(-2, -6, 12)
            tail_x = np.sin(tail_y) * 0.8
            for i in range(len(tail_y)):
                pts.append(np.array([tail_x[i], tail_y[i]]))
            head = [np.array([0, 3.5]), np.array([0.3, 3.2]), np.array([-0.3, 3.2])]
            pts.extend(head)
            idxs = np.linspace(0, len(pts)-1, len(self.drones)).astype(int)
            return [pts[i] for i in idxs]
        else:
            raise ValueError("Formación no reconocida")

    def step(self, iteration, failure_iter, failure_idx):
        for i, drone in enumerate(self.drones):
            if iteration == failure_iter and i == failure_idx:
                drone.alive = False
            if drone.alive:
                target = self.targets[i]
                r1, r2 = np.random.rand(), np.random.rand()
                cognitive = C1 * r1 * (target - drone.position)
                social = C2 * r2 * (self.gbest - drone.position)
                drone.velocity = W*drone.velocity + cognitive + social
                # evitar obstáculos
                for (ox, oy, r) in OBSTACLES:
                    diff = drone.position - np.array([ox, oy])
                    dist = np.linalg.norm(diff)
                    if dist < r+1.5:
                        drone.velocity += diff * 0.3
                drone.move()
                # actualizar mejor personal
                if np.linalg.norm(drone.position - target) < np.linalg.norm(self.pbest[i] - target):
                    self.pbest[i] = drone.position.copy()
        alive_positions = [d.position for d in self.drones if d.alive]
        if alive_positions:
            self.gbest = np.mean(alive_positions, axis=0)

# ------------------------------
# Animación
# ------------------------------
def animate_swarm(swarm, iterations, failure_iter, failure_idx, filename):
    fig, ax = plt.subplots()
    ax.set_xlim(-15, 15)
    ax.set_ylim(-10, 12)
    ax.set_aspect("equal")

    alive_sc = ax.scatter([], [], c="blue", label="Drones activos")
    dead_sc = ax.scatter([], [], c="red", label="Drones fallidos")
    target_sc = ax.scatter([], [], c="green", marker="x", label="Objetivos")
    ax.legend()

    def init():
        alive_sc.set_offsets(np.empty((0, 2)))
        dead_sc.set_offsets(np.empty((0, 2)))
        target_sc.set_offsets(np.array(swarm.targets))
        return alive_sc, dead_sc, target_sc

    def update(frame):
        swarm.step(frame, failure_iter, failure_idx)
        alive_pos = np.array([d.position for d in swarm.drones if d.alive])
        dead_pos = np.array([d.position for d in swarm.drones if not d.alive])
        if len(alive_pos) > 0:
            alive_sc.set_offsets(alive_pos)
        else:
            alive_sc.set_offsets(np.empty((0, 2)))
        if len(dead_pos) > 0:
            dead_sc.set_offsets(dead_pos)
        else:
            dead_sc.set_offsets(np.empty((0, 2)))
        return alive_sc, dead_sc, target_sc

    ani = FuncAnimation(fig, update, frames=iterations, init_func=init,
                        blit=True, repeat=False)

    ani.save(filename, writer="pillow", fps=10)
    plt.close(fig)

# ------------------------------
# Main
# ------------------------------
def main():
    formations = ["estrella", "robot", "dragon"]
    for kind in formations:
        print(f"=== Simulación figura: {kind} ===")
        swarm = Swarm(N_DRONES, kind)
        animate_swarm(swarm, ITERATIONS, FAILURE_ITER, FAILURE_INDEX,
                      f"drones_{kind}.gif")
        print(f"GIF generado: drones_{kind}.gif")

if __name__ == "__main__":
    main()
