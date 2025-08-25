# Laboratorio 1 - Introducción a los Espacios de Estados y Búsqueda

## Introducción

El presente laboratorio introduce al estudiante en el uso de algoritmos
de búsqueda y en la representación de problemas mediante espacios de
estados, acciones y metas.\
El laboratorio consta de tres puntos: el problema del 8-puzzle, el
espacio de estados y acciones con ejemplos simples (lámpara, mascota y
tesoro), y el desarrollo de un laberinto.

------------------------------------------------------------------------

## Punto 1: Resolución del 8-Puzzle

En este punto se implementó el **algoritmo de búsqueda en anchura
(BFS)** para resolver el 8-puzzle.\
Se representaron los estados como matrices 3x3 y se aplicaron
movimientos válidos del espacio vacío.

### Código relevante

``` python
def solve_puzzle_bfs(start):
    q = deque([start])
    visited = {tuple(map(tuple, start))}
    # Se expande por niveles hasta alcanzar el estado meta
```

### Ejecución

``` bash
python Primer_punto.py
```

------------------------------------------------------------------------

## Punto 2: Espacio de Estados y Acciones

Se trabajaron tres ejemplos básicos:

1.  **Lámpara:**

``` python
def transicion_lampara(estado, accion):
    if accion == "PRENDER":
        return "ENCENDIDA"
    elif accion == "APAGAR":
        return "APAGADA"
```

2.  **Mascota Virtual:**

``` python
def transicion_mascota(estado, accion):
    if accion == "DAR_COMIDA":
        return "CONTENTA"
    elif accion == "QUITAR_COMIDA":
        return "TRISTE"
```

3.  **Tesoro (BFS en cuadrícula 3x3):**

``` python
def bfs_camino(inicio, meta):
    q = deque([inicio])
    parents = {inicio: (None, None)}
    # Reconstrucción de camino al encontrar la meta
```

### Ejecución

``` bash
python Segundo_punto.py
```

------------------------------------------------------------------------

## Punto 3: Laberinto en 2x2 y 3x3

Se desarrolló un laberinto inicial en un mundo **2x2** y luego en
**3x3**.\
Se incluyó la noción de obstáculos, tabla de transiciones y recompensas
asociadas a las acciones.

### Código relevante

``` python
def mover(estado, accion):
    dx, dy = ACCIONES[accion]
    nx, ny = estado[0] + dx, estado[1] + dy
    return (nx, ny) if dentro(nx, ny) else estado
```

``` python
def bfs(inicio, meta, T):
    q = deque([inicio])
    padres = {inicio: (None, None)}
    # Se expande hasta encontrar el objetivo
```

### Ejecución

``` bash
python Tercer_punto.py
```

------------------------------------------------------------------------

## Conclusiones

-   Los problemas pueden representarse como espacios de estados y
    acciones.\
-   BFS permite encontrar caminos mínimos garantizando solución cuando
    esta existe.\
-   Ejemplos simples como la lámpara o la mascota facilitan comprender
    el concepto antes de abordar problemas más complejos como el
    8-puzzle o el laberinto.
