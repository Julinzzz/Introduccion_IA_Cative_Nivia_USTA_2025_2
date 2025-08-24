# Primer_punto.py — Commit 2 (BFS con ruta)
# -----------------------------------------------------------------------------
# Mejoras:
# - Ahora se reconstruye la RUTA ÓPTIMA: secuencia de movimientos y tableros
#   desde el estado inicial hasta la meta (BFS garantiza mínimo número de pasos).
# - Se deja de imprimir cada expansión (Depth); solo se muestra la solución encontrada.
# -----------------------------------------------------------------------------

from collections import deque

N = 3
GOAL = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

ROW = [0, 0, -1, 1]
COL = [-1, 1, 0, 0]
MOVE_NAME = ["izquierda", "derecha", "arriba", "abajo"]

class PuzzleState:
    def __init__(self, board, x, y, depth):
        self.board = board
        self.x = x
        self.y = y
        self.depth = depth

def is_goal_state(board):
    return board == GOAL

def is_valid(x, y):
    return 0 <= x < N and 0 <= y < N

def print_board(board):
    for row in board:
        print(" ".join(map(str, row)))
    print()

def solve_puzzle_bfs(start):
    """
    BFS con reconstrucción de ruta:
    - 'parents' guarda: estado_hijo -> (estado_padre, nombre_movimiento)
    - Al encontrar la meta, retrocedemos con 'parents' para armar el camino.
    """
    # localizar 0
    zx, zy = next((i, j) for i in range(N) for j in range(N) if start[i][j] == 0)

    start_key = tuple(map(tuple, start))
    goal_key  = tuple(map(tuple, GOAL))

    q = deque([PuzzleState(start, zx, zy, 0)])
    visited = {start_key}
    parents = {start_key: (None, None)}  # hijo -> (padre, movimiento)

    while q:
        curr = q.popleft()
        curr_key = tuple(map(tuple, curr.board))

        if curr_key == goal_key:
            # reconstruir
            path_states, path_moves = [], []
            k = curr_key
            while k is not None:
                parent, move = parents[k]
                path_states.append([list(r) for r in k])
                path_moves.append(move)
                k = parent
            path_states.reverse()
            path_moves = [m for m in reversed(path_moves)][1:]  # quitar primer None
            return path_states, path_moves

        for i in range(4):
            nx, ny = curr.x + ROW[i], curr.y + COL[i]
            if is_valid(nx, ny):
                new_board = [r[:] for r in curr.board]
                new_board[curr.x][curr.y], new_board[nx][ny] = new_board[nx][ny], new_board[curr.x][curr.y]
                key = tuple(map(tuple, new_board))
                if key not in visited:
                    visited.add(key)
                    parents[key] = (curr_key, MOVE_NAME[i])
                    q.append(PuzzleState(new_board, nx, ny, curr.depth + 1))

    return None, None  # sin solución

if __name__ == "__main__":
    start = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5]
    ]

    camino, movimientos = solve_puzzle_bfs(start)
    if camino is None:
        print("No se encontró solución.")
    else:
        print(f"Pasos (óptimos): {len(movimientos)}")
        print("Movimientos:", " -> ".join(movimientos))
        print("\nSecuencia de tableros:")
        for b in camino:
            print_board(b)
