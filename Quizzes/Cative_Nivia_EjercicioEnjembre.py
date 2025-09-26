import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class BeeSwarmPSO:
    def __init__(self, n_bees=12, max_iter=40):
        # Área de búsqueda
        self.bounds = [0, 10]
        self.n_bees = n_bees
        self.max_iter = max_iter

        # Flores (x, y, nivel de néctar)
        self.flowers = np.array([
            [2, 3, 50],
            [7, 8, 80],
            [5, 2, 10],  # la más dulce
            [9, 5, 60]
        ])

        # Inicializar abejas en posiciones aleatorias
        self.bees = np.random.uniform(self.bounds[0], self.bounds[1], (self.n_bees, 2))
        self.velocities = np.zeros((self.n_bees, 2))

        # Mejor posición personal y global
        self.personal_best = self.bees.copy()
        self.personal_best_fitness = np.array([self.fitness(p) for p in self.bees])
        self.global_best = self.bees[np.argmax(self.personal_best_fitness)]
        self.global_best_fitness = np.max(self.personal_best_fitness)

        # Historial
        self.history = [self.bees.copy()]

    def fitness(self, position):
        """Aptitud = dulzura de la flor más cercana"""
        distances = np.linalg.norm(self.flowers[:, :2] - position, axis=1)
        idx = np.argmin(distances)
        nectar = self.flowers[idx, 2]
        return nectar / (1 + distances[idx])  # cuanto más cerca y más dulce, mejor

    def navigate(self):
        for iteration in range(self.max_iter):
            for i in range(self.n_bees):
                r1, r2 = np.random.rand(2)

                inertia = 0.5 * self.velocities[i]
                memory = 1.5 * r1 * (self.personal_best[i] - self.bees[i])
                social = 1.5 * r2 * (self.global_best - self.bees[i])

                self.velocities[i] = inertia + memory + social
                self.bees[i] += self.velocities[i]

                # Limitar área
                self.bees[i] = np.clip(self.bees[i], self.bounds[0], self.bounds[1])

                # Evaluar
                current_fitness = self.fitness(self.bees[i])

                # Actualizar mejores
                if current_fitness > self.personal_best_fitness[i]:
                    self.personal_best[i] = self.bees[i]
                    self.personal_best_fitness[i] = current_fitness

                    if current_fitness > self.global_best_fitness:
                        self.global_best = self.bees[i]
                        self.global_best_fitness = current_fitness

            self.history.append(self.bees.copy())

            if (iteration + 1) % 10 == 0:
                print(f"Iteración {iteration+1}: mejor néctar = {self.global_best_fitness:.2f}")

        return self.global_best, self.global_best_fitness

    def visualize(self):
        fig, ax = plt.subplots(figsize=(8, 6))

        # Dibujar flores
        for f in self.flowers:
            ax.scatter(f[0], f[1], s=f[2], c="pink", edgecolors="black", label="Flor")

        bees_plot = ax.scatter([], [], c="yellow", edgecolors="black", s=80, label="Abejas")
        best_bee_plot = ax.scatter([], [], c="red", edgecolors="black", s=120, label="Mejor abeja")

        ax.set_xlim(self.bounds)
        ax.set_ylim(self.bounds)
        ax.set_title("Enjambre de abejas buscando flores (PSO)")
        ax.legend()
        ax.grid(True)

        def update(frame):
            bees = self.history[frame]
            bees_plot.set_offsets(bees)
            best_bee_plot.set_offsets([self.global_best])
            return bees_plot, best_bee_plot

        ani = FuncAnimation(fig, update, frames=len(self.history),
                            interval=300, blit=True, repeat=False)

        # Guardar como GIF
        try:
            ani.save('bee_swarm.gif', writer='pillow', fps=5)
            print("✅ Animación guardada como 'bee_swarm.gif'")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el GIF: {e}")

        plt.show()


# Ejecutar simulación
swarm = BeeSwarmPSO(n_bees=12, max_iter=40)
best_pos, best_fit = swarm.navigate()

print(f"\n🌸 La mejor flor encontrada está en {best_pos} con néctar = {best_fit:.2f}")
swarm.visualize()

