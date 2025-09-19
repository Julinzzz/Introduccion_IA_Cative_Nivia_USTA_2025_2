def dfs(graph, start, goal, path=None):
    if path is None:
        path = [start]   # Inicializa el camino con el nodo inicial

    if start == goal:
        return path  # Si el inicio es la meta, retorna el camino

    if start not in graph:
        return None  # Si el nodo no está en el grafo, retorna None

    for node in graph[start]:
        if node not in path:  # Evitar ciclos
            new_path = path + [node]  # Crear un nuevo camino
            result = dfs(graph, node, goal, new_path)  # Llamada recursiva
            if result is not None:
                return result  # Si encontró un camino válido, lo devuelve

    return None  # Si no encontró camino, retorna None

# Grafo basado en tu diagrama del tablero
graph = {
    'A' : ['B','L'],
    'B' : ['C','X'],
    'C' : ['E'],
    'E' : ['Z'],
    'L' : ['O','Q'],
    'X' : ['Y'],
    'Y' : ['J'],
    'J' : ['M','N'],
    'M' : ['G']
}

# Nodo inicial y final
start_node = 'A'
end_node = 'G'

# Probar DFS con retroceso
print("DFS Path:", dfs(graph, start_node, end_node))