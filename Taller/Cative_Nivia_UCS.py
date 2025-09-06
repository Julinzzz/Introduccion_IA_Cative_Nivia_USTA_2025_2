
import heapq
import matplotlib.pyplot as plt
import networkx as nx

# --------------------- Layout jerárquico (árbol) ---------------------
def hierarchy_pos(G, root, width=1.0, vert_gap=1.2, vert_loc=0, xcenter=0.5):
    """Posición jerárquica para dibujar árboles dirigidos (root arriba)."""
    def _hierarchy_pos(G, root, leftmost, width, vert_gap, vert_loc, xcenter,
                       pos=None, parent=None):
        if pos is None:
            pos = {}
        pos[root] = (xcenter, vert_loc)
        children = list(G.successors(root))
        if parent is not None and root in children:
            children.remove(parent)
        if children:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, leftmost, dx, vert_gap,
                                     vert_loc - vert_gap, nextx, pos, root)
        return pos
    return _hierarchy_pos(G, root, 0, width, vert_gap, vert_loc, xcenter)

# --------------------- UCS con animación ---------------------
def ucs_visual(graph_w, start, goal, pause=0.9):
    """
    graph_w: dict[str, list[tuple[str, cost]]], costos >= 0
    start, goal: nodos
    pause: segundos entre cuadros
    """
    G = nx.DiGraph()
    for u, lst in graph_w.items():
        for v, w in lst:
            G.add_edge(u, v, weight=w)

    pos = hierarchy_pos(G, start)
    edge_labels = nx.get_edge_attributes(G, 'weight')

  
    pq = [(0, start, [start])]
    best_cost = {start: 0}
    visited_order = []  

    plt.ion()
    while pq:
        cost, node, path = heapq.heappop(pq)

        if cost > best_cost.get(node, float('inf')):
            continue

        plt.clf()
        nx.draw(G, pos, with_labels=True, node_size=1100, node_color="#DDEEFF",
                font_size=10, arrows=True, arrowsize=12)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

        if visited_order:
            nx.draw_networkx_nodes(G, pos, nodelist=visited_order,
                                   node_color="#FFE08A", node_size=1100)

        nx.draw_networkx_nodes(G, pos, nodelist=path,
                               node_color="#FFB074", node_size=1100)

        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3)

        plt.title(f"UCS: extraído '{node}'  |  costo={cost}")
        plt.pause(pause)

        if node == goal:
            plt.clf()
            nx.draw(G, pos, with_labels=True, node_size=1100, node_color="#DDEEFF",
                    font_size=10, arrows=True, arrowsize=12)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
            nx.draw_networkx_nodes(G, pos, nodelist=visited_order, node_color="#FFE08A", node_size=1100)
            nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="#8CE99A", node_size=1100)
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=4)
            plt.title(f"Camino óptimo (UCS): {' → '.join(path)}  |  Costo={cost}")
            plt.pause(2.5)
            plt.ioff()
            plt.show()
            return path, cost

        if node not in visited_order:
            visited_order.append(node)
            for nbr, w in graph_w.get(node, []):
                new_cost = cost + w
                if new_cost < best_cost.get(nbr, float('inf')):
                    best_cost[nbr] = new_cost
                    heapq.heappush(pq, (new_cost, nbr, path + [nbr]))

    plt.ioff()
    plt.show()
    return None, None

# --------------------- Árbol del enunciado ---------------------
# Orden de hijos: estrictamente izquierda→derecha
GRAPH_W = {
    'S': [('A',1),('B',1),('D',1),('E',1)],
    'A': [('F',1),('G',1)],
    'F': [('M',1)], 'M': [('N',1)],
    'B': [('H',1),('R',1)],
    'H': [('O',1),('Q',1)], 'O': [('P',1)],
    'Q': [('U',1)], 'U': [('V',1),('W',1)],
    'R': [('X',1),('T',1)], 'T': [('GG',1)],
    'D': [('J',1)], 'J': [('Y',1)], 'Y': [('Z',1)], 'Z': [('AA',1),('BB',1)],
    'E': [('K',1),('L',1)], 'K': [('I',1)], 'L': [('CC',1)],
    'CC': [('DD',1),('EE',1)], 'EE': [('FF',1)]
}

if __name__ == "__main__":
    path, cost = ucs_visual(GRAPH_W, start='S', goal='W', pause=0.8)
    print("Resultado UCS ->", path, "| costo:", cost)

