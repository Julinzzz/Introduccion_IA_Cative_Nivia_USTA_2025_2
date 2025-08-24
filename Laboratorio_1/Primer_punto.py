# Primer_punto.py — Commit 3 (BFS final)
# -----------------------------------------------------------------------------
# Mejoras finales:
# 1) Verificación de RESOLUBILIDAD respecto al estado final (GOAL).
#    Evita ejecutar BFS si el problema es imposible (paridad de inversiones).
# 2) Métricas básicas: nodos expandidos y profundidad de solución.
# 3) Comentarios detallados y salida formateada para el informe.
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

# ---------- Chequeo de resolubilidad (3x3) ----------
def is_solvable(initial, goal):
    """
    8‑puzzle 3x3: el estado inicial es resoluble hacia 'goal' si la paridad
    de inversiones del inicial **relativa al orden del goal** es PAR.
    - Ignoramos el 0.
    - Reescribimos el inicial en el orden en que las fichas aparecen en 'goal'.
    """
    def flat_wo_zero(m):
        return [x for r in m for x in r if x != 0]

    goal_order = {v: i for i, v in enumerate(flat_wo_zero(goal))}
    seq = [goal_order[v] for v in flat_wo_zero(initial)]
    inv = sum(1 for i in range(len(seq)) for j in range(i+1, len(seq)) if seq[i] > seq[j])
    return inv % 2 == 0
# ----------------------------------------------------

def solve_puzzle_bfs(start):
    """BFS con reconstrucción de ruta; retorna (lista_tableros, lista_movimientos)."""
    # Comprobación previa: ¿vale la pena buscar?
    if not is_solvable(start, GOAL):
        return None, None, {"expandidos": 0, "profundidad": None}

    zx, zy = next((i, j) for i in range(N) for j in range(N) if start[i][j] == 0)

    start_key = tuple(map(tuple, start))
    goal_key  = tuple(map(tuple, GOAL))

    q = deque([PuzzleState(start, zx, zy, 0)])
    visited = {start_key}
    parents = {start_key: (None, None)}  # hijo -> (padre, movimiento)

    expanded = 0  # métrica: cuántos nodos sacamos de la cola (expandidos)

    while q:
        curr = q.popleft()
        expanded += 1
        curr_key = tuple(map(tuple, curr.board))

        if curr_key == goal_key:
            # reconstrucción
            path_states, path_moves = [], []
            k = curr_key
            while k is not None:
                parent, move = parents[k]
                path_states.append([list(r) for r in k])
                path_moves.append(move)
                k = parent
            path_states.reverse()
            path_moves = [m for m in reversed(path_moves)][1:]

            stats = {"expandidos": expanded, "profundidad": len(path_moves)}
            return path_states, path_moves, stats

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

    return None, None, {"expandidos": expanded, "profundidad": None}

if __name__ == "__main__":
    # Puedes pegar aquí el estado inicial del enunciado
    start = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5]
    ]

    camino, movimientos, stats = solve_puzzle_bfs(start)
    if camino is None:
        print("El estado inicial NO es resoluble hacia el estado final dado (GOAL).")
    else:
        print(f"Pasos (óptimos): {len(movimientos)}")
        print("Movimientos:", " -> ".join(movimientos))
        print(f"Nodos expandidos (BFS): {stats['expandidos']}")
        print("\nSecuencia de tableros:")
        for b in camino:
            print_board(b)
