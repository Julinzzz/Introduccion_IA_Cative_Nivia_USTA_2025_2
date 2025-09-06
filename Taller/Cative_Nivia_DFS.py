def dfs(graph, start, goal, path=None):
    if path is None:
        path = [start]
    if start == goal:
        return path
    for nbr in graph.get(start, []):  
        if nbr not in path:
            res = dfs(graph, nbr, goal, path + [nbr]) #RECURSIVO
            if res is not None:
                return res
    return None

# Grafo
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
    path = dfs(GRAPH, 'S', 'W')
    print("DFS -> camino:", path)
