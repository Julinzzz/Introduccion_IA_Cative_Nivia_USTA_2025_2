
# Primer Punto — Ecosistema de Visualización Interactiva en Python (hvPlot · HoloViews · Datashader · Bokeh/Matplotlib/Plotly · Streamlit)

> **Objetivo.** Presentar, de manera práctica y académica, cómo se articula el ecosistema de visualización basado en **hvPlot** y **HoloViews**, cómo **Datashader** permite escalar a millones de puntos, qué salidas de *rendering* soportan (**Bokeh**, **Matplotlib**, **Plotly**) y cómo **Streamlit** sirve para desplegar prototipos o aplicaciones de *data apps*. Se incluyen descripciones, casos de uso y fragmentos de código mínimos.

---

## Tabla de contenidos
1. [Arquitectura general](#arquitectura-general)
2. [Datos de entrada (pandas, GeoPandas, Dask, xarray, Polars)](#datos-de-entrada)
3. [hvPlot: API rápida tipo `.plot()`](#hvplot)
4. [HoloViews: representación declarativa](#holoviews)
5. [Datashader: visualización a gran escala](#datashader)
6. [Motores de renderizado: Bokeh / Matplotlib / Plotly](#motores-de-renderizado)
7. [Streamlit: despliegue en apps](#streamlit)
8. [Guías de elección](#guias-de-eleccion)
9. [Reproducibilidad (entorno sugerido)](#reproducibilidad)
10. [Referencias básicas](#referencias)

---

## Arquitectura general

![Pipeline de librerías](pipeline_hvplot_holoviews_datashader.png)

**Flujo conceptual:**

- **Data libraries:** `pandas`, `GeoPandas`, `xarray`, `polars`, `Dask` (y afines) → estructuras tabulares o matriciales.
- **hvPlot** expone un **API tipo `.plot()`** unificado para esas estructuras.
- **HoloViews** provee una **representación intermedia declarativa** (objetos `Curve`, `Points`, `Image`, `Polygons`…), conmutando **backends** de salida.
- **Datashader** rasteriza datos masivos y se integra con HoloViews/hvPlot.
- **Backends de salida:** **Bokeh** (interactivo web por defecto), **Matplotlib** (estático/impresión), **Plotly** (interactividad JS).
- **Streamlit** orquesta una interfaz de usuario simple para empaquetar visualizaciones como aplicación web.

---

## Datos de entrada
Las siguientes bibliotecas suministran estructuras de datos con soporte nativo en hvPlot/HoloViews:

- **pandas / GeoPandas:** tablas; *geometrías* (`Point`, `LineString`, `Polygon`) en columnas `geometry` (CRS).
- **xarray:** *N-D labeled arrays*; ideal para series temporales, rejillas y datos científicos.
- **Dask:** *out-of-core* y paralelismo; permite trabajar con datos más grandes que la memoria.
- **polars:** *DataFrames* rápidos basados en Apache Arrow (soporte vía conversión o extensiones).
- (Otros: DuckDB, Ibis, NetworkX, RAPIDS, Intake, etc., integrables vía exportación a DataFrame).

> **Instalación mínima (conda):**
> ```bash
> conda install -c conda-forge pandas geopandas xarray dask hvplot holoviews datashader bokeh matplotlib plotly streamlit
> ```

---

## hvPlot
**¿Qué es?** Una capa muy ligera que añade un método `.hvplot` a DataFrames/Series (y estructuras compatibles) para obtener gráficos interactivos **sin cambiar** de paradigma respecto a `pandas.plot()`.

**Para qué sirve / campos:** *Exploración rápida* de datos tabulares/espaciales; *prototipado*; docencia; *dashboards* simples.

**Cómo funciona (idea):** mapea columnas a **canales visuales** (x, y, color, tamaño, agregación) y delega la construcción del objeto declarativo a **HoloViews**, que a su vez lo renderiza con el *backend* por defecto (usualmente **Bokeh**).

**Ejemplo mínimo** (tabla temporal):

```python
import pandas as pd, numpy as np
import hvplot.pandas  # habilita df.hvplot

t = pd.date_range("2025-01-01", periods=200, freq="D")
df = pd.DataFrame({"fecha": t, "y": np.sin(np.linspace(0, 8, t.size))})
plot = df.hvplot(x="fecha", y="y", kind="line", title="Serie temporal (hvPlot)")
plot
```

**Geo** con `GeoPandas`:

```python
import geopandas as gpd, hvplot.pandas  # noqa: F401
gdf = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
gdf.hvplot(geo=True, tiles="OSM", hover_cols=["name"], color="continent")
```

---

## HoloViews
**¿Qué es?** Un marco **declarativo**: el usuario describe **lo que** quiere representar, no **cómo** dibujarlo. Produce objetos componibles (`+`, `*`, `layout`, `overlay`) y *responsive* a widgets.

**Para qué sirve / campos:** análisis exploratorio, ciencia de datos, visualización científica, interfaces interactivas con *sliders*, *selectors*, *linked brushing*.

**Cómo funciona (idea):** crea objetos de alto nivel (`hv.Curve`, `hv.Points`, `hv.Image`, `hv.Polygons`) y los convierte a la sintaxis del *backend* elegido (**Bokeh**, **Matplotlib** o **Plotly**).

**Ejemplo mínimo:**

```python
import numpy as np, holoviews as hv
hv.extension("bokeh")  # o "matplotlib"/"plotly"

x = np.linspace(0, 10, 200)
curve = hv.Curve((x, np.sin(x)), label="Seno")
scatter = hv.Scatter((x, np.cos(x)), label="Coseno")
(curve * scatter).opts(width=600, height=300, title="Composición en HoloViews")
```

---

## Datashader
**¿Qué es?** Librería para **rasterizar** millones (o miles de millones) de puntos/polígonos en **imágenes** agregadas, evitando sobrecarga del navegador.

**Para qué sirve / campos:** *big data* geoespacial, *time series* densas, nubes de puntos, trayectorias, mapas de calor.

**Cómo funciona (idea):** en lugar de enviar cada marca al navegador, computa **agregaciones por píxel** (conteo, suma, media…) en el servidor/local y genera una **imagen** que luego se superpone en el lienzo interactivo (vía HoloViews/hvPlot).

**Ejemplo mínimo con hvPlot (activación automática):**

```python
import pandas as pd, numpy as np, hvplot.pandas  # noqa: F401

n = 2_000_000
df = pd.DataFrame({"x": np.random.randn(n), "y": np.random.randn(n)})
# rasterize=True delega a Datashader
df.hvplot.points("x", "y", rasterize=True, aggregator="count", cnorm="eq_hist")
```

---

## Motores de renderizado
### Bokeh
- **Foco:** interactividad Web (zoom, hover, selección, *linked brushing*, *Bokeh Server*).
- **Uso típico:** *dashboards* y notebooks.
- **Ejemplo:**

```python
from bokeh.plotting import figure, show
p = figure(title="Bokeh básico")
p.line([1,2,3], [3,2,1], line_width=2)
show(p)
```

### Matplotlib
- **Foco:** publicación académica, control fino, formatos estáticos (PNG/SVG/PDF).
- **Ejemplo:**

```python
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1,2,3], [3,2,1])
plt.title("Matplotlib básico")
plt.show()
```

### Plotly
- **Foco:** interactividad **JavaScript** con *tooltips*, exportación HTML, soporte 3D.
- **Ejemplo:**

```python
import plotly.express as px
df = px.data.iris()
px.scatter(df, x="sepal_width", y="sepal_length", color="species",
           title="Iris con Plotly")
```

---

## Streamlit
**¿Qué es?** *Framework* para construir **aplicaciones de datos** en Python con muy poco código.

**Para qué sirve / campos:** demostraciones, prototipos de analítica, *dashboards* livianos, formularios y carga de datos.

**Cómo funciona (idea):** cada ejecución del script genera una **página reactiva**; los *widgets* (selectbox, slider, file_uploader) invalidan el estado y recomputan.

**Ejemplo mínimo integrando hvPlot:**

```python
# streamlit_app.py
import streamlit as st, pandas as pd, numpy as np
import hvplot.pandas  # habilita hvPlot
from holoviews import opts

st.title("Demo hvPlot + Streamlit")
n = st.slider("n puntos", 100, 5000, 1000, step=100)
df = pd.DataFrame({"x": np.random.randn(n), "y": np.random.randn(n)})
plot = df.hvplot.scatter("x", "y").opts(opts.Scatter(width=600, height=400))
st.bokeh_chart(hv.render(plot, backend="bokeh"))
```

> Ejecutar: `streamlit run streamlit_app.py`.

---

## Guías de elección
- **Exploración rápida:** `hvPlot` sobre `pandas/GeoPandas/xarray`.
- **Composición avanzada/Widgets:** `HoloViews` (+ `panel` si requiere UI compleja).
- **Datos masivos:** activar `rasterize=True` (hvPlot/HoloViews) → **Datashader**.
- **Salida estática de alta calidad:** **Matplotlib**.
- **Web JS embebible o 3D:** **Plotly**.
- **App ligera para compartir:** **Streamlit**.

---

## Reproducibilidad
**`environment.yml` sugerido:**

```yaml
name: vis-ecosystem
channels: [conda-forge]
dependencies:
  - python=3.11
  - pandas
  - geopandas
  - xarray
  - dask
  - hvplot
  - holoviews
  - datashader
  - bokeh
  - matplotlib
  - plotly
  - streamlit
```

---

## Referencias
- Documentación oficial: hvPlot · HoloViews · Datashader · Bokeh · Matplotlib · Plotly · Streamlit.
- Guías introductorias y galerías de ejemplos en los sitios oficiales de cada proyecto.
