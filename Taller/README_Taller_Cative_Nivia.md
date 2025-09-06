# Taller – Introducción a IA (Cative & Nivia)

Este documento resume **qué hicimos** y **cómo ejecutar todo**. Está escrito paso a paso para que se entienda fácil, incluso con conocimientos básicos.

---

## 📁 Estructura de archivos

```
BD_SENSORES.xlsx             # Base original sin procesar (varias hojas/sensores)
etl_polars.py                # ETL sencillo (extraer/limpiar/transformar)
app_streamlit_plotly.py      # Dashboard interactivo (Streamlit + Plotly)
Cative_Nivia_BFS.py          # Árbol: Búsqueda en Amplitud (BFS)
Cative_Nivia_DFS.py          # Árbol: Búsqueda en Profundidad (DFS)
Cative_Nivia_UCS.py          # Árbol: Búsqueda de Costo Uniforme (UCS) con animación
Punto_3.py                   # Agente que resuelve el circuito (A* + movimiento seguro)
```

---

## 🔧 Requisitos (una sola vez)

1. **Python 3.10+** instalado.
2. (Opcional) crear entorno virtual y activarlo.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar librerías:
```bash
pip install streamlit polars pandas openpyxl plotly networkx matplotlib
```

> Si falla alguna, instala al menos: `polars`, `pandas`, `openpyxl`, `plotly`, `streamlit`, `matplotlib`, `networkx`.

---

## 1) Árboles de búsqueda (BFS / DFS / UCS)

**Meta:** ir del nodo `S` al objetivo (p. ej., `W`) en el árbol del enunciado.

- **BFS** (Breadth-First Search): explora por niveles; da el **menor número de pasos** si los costos son iguales.
- **DFS** (Depth-First Search): se mete por un camino hasta el fondo; no garantiza el más corto.
- **UCS** (Uniform Cost Search): siempre expande el nodo con **menor costo acumulado**; encuentra el camino de menor costo (costos ≥ 0).

### Ejecutar
```bash
python Cative_Nivia_BFS.py
python Cative_Nivia_DFS.py
python Cative_Nivia_UCS.py   # muestra animación del orden de expansión
```

---

## 2) Dashboard de sensores (Streamlit + Plotly)

**Objetivo:** leer `BD_SENSORES.xlsx`, limpiar datos y visualizar 5 gráficas clave.

### 2.1 Ejecutar Streamlit
Coloca `BD_SENSORES.xlsx` en la misma carpeta o súbelo desde la barra lateral.

**Opción A (normal):**
```bash
streamlit run app_streamlit_plotly.py
```

**Opción B (si en Windows dice “streamlit no se reconoce”):**
```powershell
python -m streamlit run app_streamlit_plotly.py
```

Se abrirá el navegador con la app. En la **barra lateral**:

- **Selecciona sensores (hojas):** elige una o varias hojas del Excel.
- **Suavizado (ventana):** tamaño del promedio móvil (más grande = más suave).
- **Sensor principal:** cuál analizar en detalle.
- **Usuario (único):** selecciona **un usuario** (evita el “spaghetti” de líneas).

### 2.2 ¿Qué gráficos verás?
1. **Serie temporal (V) + Suavizado** – evolución de la señal cruda y suavizada.
2. **Serie en mV (usuario único)** – misma señal convertida a milivoltios.
3. **Boxplot por usuario (sensor elegido)** – compara distribuciones y outliers.
4. **Heatmap (t × usuario)** – patrón por tiempo y usuario.
5. **z‑score** – puntos con |z|>3 son outliers estadísticos.

> El dashboard **ordena los usuarios 1→60** y evita fallos cuando no seleccionas hojas.

### 2.3 ETL con Polars (opcional)
Si quieres generar un archivo limpio:

```bash
# Parquet
python etl_polars.py --input BD_SENSORES.xlsx --out data/clean.parquet

# CSV
python etl_polars.py -i BD_SENSORES.xlsx -o data/clean.csv
```

---

## 3) Agente en el circuito (A* + movimiento seguro)

**Qué hace:** planifica con **A\*** una ruta de `S` (abajo-izq) a `G` (arriba-der) evitando `X`. Luego **sigue** esa ruta con pasos seguros; si queda cerca de una esquina, prueba micro‑pasos para destrabarse.

### Ejecutar
```bash
python Punto_3.py
```
Verás el circuito, la ruta punteada y el agente avanzando. Parámetros útiles si quieres afinar:
- `STEP_SIZE`: tamaño del paso (0.30–0.45 va bien).
- `CLEARANCE`: margen al dilatar obstáculos para planear.
- Umbral de llegada al waypoint (0.35–0.45).

---

## 🧪 Problemas comunes

- **“streamlit no se reconoce”** → usa `python -m streamlit run app_streamlit_plotly.py`  
- **“No module named …”** → `pip install` del paquete que falta  
- **Gráficas vacías** → selecciona al menos **una hoja** y un **usuario** válido  
- **Circuito no encuentra ruta** → baja `CLEARANCE` o permite cortar esquinas en el planificador

---

## ✅ Checklist rápido

- [ ] `python --version` → 3.10+  
- [ ] `pip install …` sin errores  
- [ ] BFS/DFS/UCS ejecutan y muestran resultados  
- [ ] Streamlit abre y veo las 5 gráficas  
- [ ] El agente en `Punto_3.py` llega a `G`

---

**Autores:** Cative & Nivia — *Introducción a IA*  
**Tecnologías:** Python, Polars, Pandas, Plotly, Streamlit, NetworkX, Matplotlib
