# Primer_punto.py — Commit 1
# -----------------------------------------------------------------------------

from collections import deque

# Dimensión del tablero (3x3)
N = 3

# Estado objetivo (puedes cambiarlo si tu laboratorio usa otro final)
GOAL = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

# Movimientos posibles del hueco (0): izquierda, derecha, arriba, abajo
ROW = [0, 0, -1, 1]
COL = [-1, 1, 0, 0]
MOVE_NAME = ["izquierda", "derecha", "arriba", "abajo"]  # solo informativo en este commit

class PuzzleState:
    """
    Representa un estado del puzzle.
    - board: matriz 3x3
    - x, y : coordenadas del hueco (0) dentro del tablero
    - depth: nivel del estado (número de movimientos desde el inicio)
    """
    def __init__(self, board, x, y, depth):
        self.board = board
        self.x = x
        self.y = y
        self.depth = depth

def is_goal_state(board):
    """Comprueba si el tablero actual es igual al objetivo GOAL."""
    return board == GOAL

def is_valid(x, y):
    """Verifica que (x, y) caiga dentro del tablero 3x3."""
    return 0 <= x < N and 0 <= y < N

def print_board(board):
    """Imprime el tablero; deja 0 tal cual para ver el hueco."""
    for row in board:
        print(" ".join(map(str, row)))
    print("--------")

def solve_puzzle_bfs(start, x, y):
    """
    BFS clásico:
    - Usamos una cola (deque) para procesar primero los estados más superficiales.
    - 'visited' evita re-explorar tableros ya vistos (mismo contenido).
    """
    q = deque()
    visited = set()

    q.append(PuzzleState(start, x, y, 0))
    visited.add(tuple(map(tuple, start)))  # listas -> tuplas para que sean "hashables"

    while q:
        curr = q.popleft()

        # Mostrar el estado que estamos expandiendo
        print(f"Depth: {curr.depth}")
        print_board(curr.board)

        # ¿Llegamos a la meta?
        if is_goal_state(curr.board):
            print(f"¡Meta alcanzada en profundidad {curr.depth}!")
            return

        # Generar movimientos del hueco
        for i in range(4):
            nx = curr.x + ROW[i]
            ny = curr.y + COL[i]

            if is_valid(nx, ny):
                # Copiar tablero y aplicar el intercambio (mover el hueco)
                new_board = [r[:] for r in curr.board]
                new_board[curr.x][curr.y], new_board[nx][ny] = new_board[nx][ny], new_board[curr.x][curr.y]

                key = tuple(map(tuple, new_board))
                if key not in visited:
                    visited.add(key)
                    q.append(PuzzleState(new_board, nx, ny, curr.depth + 1))

    print("No se encontró solución (BFS agotó el espacio sin hallar la meta).")

if __name__ == "__main__":
    # Estado inicial (ajústalo al de tu laboratorio)
    start = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5]
    ]
    # Localizamos el hueco (0) automáticamente
    zx, zy = next((i, j) for i in range(N) for j in range(N) if start[i][j] == 0)

    print("Estado inicial:")
    print_board(start)

    solve_puzzle_bfs(start, zx, zy)
