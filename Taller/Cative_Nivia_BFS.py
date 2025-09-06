from collections import deque

def bfs(graph, start, goal):
    if start == goal:
        return [start]
    visited = set()
    q = deque([[start]])  # cola de caminos

    while q:
        path = q.popleft()
        node = path[-1]
        if node in visited:
            continue
        visited.add(node)

        for nbr in graph.get(node, []): 
            new_path = path + [nbr]
            if nbr == goal:
                return new_path
            q.append(new_path)
    return None

# Grafo (no ponderado)
GRAPH = {
    'S': ['A','B','D','E'],
    'A': ['F','G'],
    'F': ['M'], 'M': ['N'],
    'B': ['H','R'],
    'H': ['O','Q'], 'O': ['P'],
    'Q': ['U'], 'U': ['V','W'],
    'R': ['X','T'], 'T': ['GG'],
    'D': ['J'], 'J': ['Y'], 'Y': ['Z'], 'Z': ['AA','BB'],
    'E': ['K','L'], 'K': ['I'], 'L': ['CC'], 'CC': ['DD','EE'], 'EE': ['FF']
}

if __name__ == "__main__":
    path = bfs(GRAPH, 'S', 'W')
    print("BFS -> camino:", path)
