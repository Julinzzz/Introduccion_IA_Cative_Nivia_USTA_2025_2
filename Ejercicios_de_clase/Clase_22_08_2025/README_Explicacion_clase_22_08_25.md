# Algoritmos de Búsqueda: BFS, DFS y UCS

En este documento se explican tres algoritmos de búsqueda vistos en clase y aplicados en grafos: **Búsqueda en Anchura (BFS)**, **Búsqueda en Profundidad (DFS)** y **Búsqueda de Costo Uniforme (UCS)**.  
El objetivo es comprender cómo funcionan a partir de los códigos implementados en Python.

---

## 1. Búsqueda en Anchura (BFS)

En el código implementado, la búsqueda en anchura utiliza una **cola (queue)** para almacenar los caminos posibles.  
El algoritmo comienza en el nodo inicial y explora primero todos sus vecinos, antes de pasar al siguiente nivel.  

- Asegura encontrar la ruta más corta en **número de pasos**, siempre que todos los costos sean iguales.  
- Evita ciclos marcando nodos visitados.  

**Ejemplo de código (fragmento):**
```python
queue = deque([[start]])
...
path = queue.popleft()
node = path[-1]
```

En el ejemplo de grafo dado, BFS encuentra un camino desde el nodo `A` hasta `G`, expandiendo primero los nodos más cercanos a la raíz.

---

## 2. Búsqueda en Profundidad (DFS)

La búsqueda en profundidad se implementa de manera **recursiva**.  
Se expande un camino hasta llegar al objetivo o hasta que ya no haya más nodos disponibles, retrocediendo en caso de ser necesario.  

- Utiliza una **pila implícita en la recursión**.  
- Puede caer en caminos largos sin salida si no se controla.  
- No garantiza la solución más corta, pero puede ser más rápida en ciertos escenarios.  

**Ejemplo de código (fragmento):**
```python
def dfs(graph, start, goal, path=None):
    if path is None:
        path = [start]
    ...
    for node in graph[start]:
        if node not in path:
            result = dfs(graph, node, goal, path + [node])
```

En el ejemplo trabajado, DFS recorre los nodos desde `A` hasta `G` explorando en profundidad cada opción antes de retroceder.

---

## 3. Búsqueda de Costo Uniforme (UCS)

En el código de clase, la búsqueda de costo uniforme se apoya en una **cola de prioridad (heapq)**.  
A diferencia de BFS, aquí se prioriza siempre el camino de **menor costo acumulado**.  

- Garantiza encontrar la **ruta óptima en términos de costo**, siempre que los valores sean positivos.  
- Es más general que BFS porque funciona con grafos ponderados.  

**Ejemplo de código (fragmento):**
```python
pq = [(0, [start])]
...
cost, path = heapq.heappop(pq)
...
heapq.heappush(pq, (cost + step_cost, new_path))
```

El código además incluye una visualización con **NetworkX** y **Matplotlib**, mostrando paso a paso cómo se van expandiendo los nodos y el costo acumulado.

---

## Conclusiones

- **BFS** encuentra la ruta más corta en pasos.  
- **DFS** explora en profundidad, aunque no siempre es la ruta más corta.  
- **UCS** encuentra la ruta de menor costo, siendo más flexible que BFS.  

Estos tres algoritmos representan diferentes estrategias de búsqueda en grafos y son la base para algoritmos más avanzados como A*.
