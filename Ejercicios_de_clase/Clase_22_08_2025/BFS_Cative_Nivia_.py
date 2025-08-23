from collections import deque

def bfs(graph, start, goal):
    visited = set()  # Set to keep track of visited nodes
    queue = deque([[start]])  # Queue for BFS, starting with the initial node

    if start == goal:
        return "Start and goal nodes are the same"

    while queue:
        path = queue.popleft()  # Get the first path from the queue
        node = path[-1]         # Get the last node from the path

        if node not in visited:
            neighbors = graph.get(node, [])  # Get neighbors of the current node

            for neighbor in neighbors:
                new_path = list(path)       # Copy the current path
                new_path.append(neighbor)   # Add the neighbor to the path
                queue.append(new_path)      # Add new path to the queue

                if neighbor == goal:
                    return new_path  # If neighbor is the goal, return the path

            visited.add(node)  # Mark the node as explored

    return "No path found between start and goal"

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

start_node = 'A'
end_node = 'G'
print("BFS Path:", bfs(graph, start_node, end_node))