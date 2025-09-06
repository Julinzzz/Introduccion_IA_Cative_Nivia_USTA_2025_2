
# app_streamlit_plotly_v3.py
# Versión enfocada en UN usuario a la vez.
# - ETL: columnas = usuarios (1..60), filas = t
# - Selector único de usuario (sin rango)
# - Orden de usuarios 1→60
# - Gráficas centradas en el usuario seleccionado

import os, io
import polars as pl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Sensores – Túnel Carpiano (Plotly, un usuario)", layout="wide")

# ------------------------- Utilidades ETL -------------------------
@st.cache_data(show_spinner=False)
def read_excel_polars(file_bytes:bytes, sheet:str) -> pl.DataFrame:
    try:
        return pl.read_excel(io.BytesIO(file_bytes), sheet_name=sheet)
    except Exception:
        pdf = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet)
        return pl.from_pandas(pdf)

def clean_long(df:pl.DataFrame, sheet:str) -> pl.DataFrame:
    df = df.rename({c: str(c) for c in df.columns})
    value_cols = [c for c in df.columns if c != "Usuario"]
    df = df.select(value_cols).with_columns(pl.arange(1, pl.len()+1).alias("t"))
    clean_exprs = [
        pl.col(c).cast(pl.Utf8).str.replace_all(r"[^0-9\.\-]","").cast(pl.Float64).alias(c)
        for c in value_cols
    ]
    df = df.with_columns(clean_exprs)
    long = (df.melt(id_vars="t", variable_name="usuario", value_name="voltaje")
              .drop_nulls(["usuario","voltaje"])
              .with_columns(pl.lit(sheet).alias("sensor"))
              .with_columns([pl.col("t").cast(pl.Int64, strict=False),
                             pl.col("usuario").cast(pl.Utf8)]))
    return long

@st.cache_data(show_spinner=False)
def build_dataset(file_bytes:bytes, sheets:list[str], win:int=5) -> pl.DataFrame:
    if not sheets:
        return pl.DataFrame({"t": [], "usuario": [], "voltaje": [], "sensor": []})
    frames = []
    for sh in sheets:
        try:
            frames.append(clean_long(read_excel_polars(file_bytes, sh), sh))
        except Exception as e:
            st.warning(f"Hoja '{sh}' omitida: {e}")
    if not frames:
        return pl.DataFrame({"t": [], "usuario": [], "voltaje": [], "sensor": []})
    data = pl.concat(frames, how="vertical_relaxed").sort(["sensor","usuario","t"])
    data = data.with_columns([
        (pl.col("voltaje")*1000).alias("mV"),
        pl.col("voltaje").rolling_mean(window_size=win, min_periods=1).over(["sensor","usuario"]).alias("voltaje_suav")
    ])
    stats = data.group_by("sensor").agg(
        media = pl.col("voltaje").mean(),
        sigma = pl.col("voltaje").std(ddof=1)
    )
    data = data.join(stats, on="sensor", how="left").with_columns(
        ((pl.col("voltaje")-pl.col("media"))/pl.col("sigma")).alias("zscore")
    ).drop(["media","sigma"])
    return data

# ------------------------- Sidebar -------------------------
st.sidebar.header("Carga de datos")
default_path = "BD_SENSORES.xlsx"
uploaded = st.sidebar.file_uploader("Sube BD_SENSORES.xlsx", type=["xlsx"])

sheets = None
file_bytes = None
if uploaded is not None:
    file_bytes = uploaded.read()
    sheets = pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names
    st.sidebar.success("Archivo cargado desde la interfaz.")
elif os.path.exists(default_path):
    file_bytes = open(default_path,"rb").read()
    sheets = pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names
    st.sidebar.info("Usando BD_SENSORES.xlsx de la carpeta actual.")

if file_bytes is None or sheets is None or len(sheets)==0:
    st.warning("Sube **BD_SENSORES.xlsx** o deja el archivo junto a este script.")
    st.stop()

sel_sheets = st.sidebar.multiselect("Selecciona sensores (hojas)", sheets, default=sheets[:1])
if not sel_sheets:
    st.warning("Selecciona al menos **una** hoja.")
    st.stop()

win = st.sidebar.slider("Suavizado (ventana)", 1, 15, 5)

# Dataset completo filtrado por hojas
data = build_dataset(file_bytes, sel_sheets, win=win)
if data.is_empty():
    st.warning("No se pudo construir el dataset con las hojas seleccionadas.")
    st.stop()

# Orden 1→60 para usuarios
usuarios_ordenados = (
    data.select("usuario").unique()
        .with_columns(pl.col("usuario").cast(pl.Int64, strict=False))
        .drop_nulls()
        .sort("usuario")
        .with_columns(pl.col("usuario").cast(pl.Utf8))
        .to_series()
        .to_list()
)

# Filtros de detalle
sensors = data.select("sensor").unique().to_series().to_list()
sel_sensor = st.sidebar.selectbox("Sensor principal", sensors, index=0)

# Recalcula lista de usuarios disponibles SOLO para ese sensor
usuarios_sensor = (data.filter(pl.col("sensor")==sel_sensor)
                      .select("usuario").unique()
                      .with_columns(pl.col("usuario").cast(pl.Int64, strict=False))
                      .drop_nulls().sort("usuario")
                      .with_columns(pl.col("usuario").cast(pl.Utf8))
                      .to_series().to_list())
default_user_idx = 0
sel_user = st.sidebar.selectbox("Usuario (único)", usuarios_sensor, index=default_user_idx)

# Subconjunto final
df = data.filter((pl.col("sensor")==sel_sensor) & (pl.col("usuario")==sel_user))
pdf = df.to_pandas()

# ------------------------- Título y KPIs -------------------------
st.title("Cative y Nivia - Dashboard de Sensores")
st.caption(f"Sensor: {sel_sensor}  |  Usuario: {sel_user}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Filas", len(pdf))
col2.metric("t distintos", pdf["t"].nunique() if not pdf.empty else 0)
col3.metric("Voltaje prom. [mV]", f"{pdf['mV'].mean():.1f}" if not pdf.empty else "—")
col4.metric("Outliers (|z|>3)", int((pdf['zscore'].abs()>3).sum()) if not pdf.empty else 0)

# ------------------------- 1) Serie temporal (voltaje y suavizado) -------------------------
st.subheader("1) Serie temporal (voltaje y suavizado)")
if pdf.empty:
    st.info("No hay datos para graficar con la selección actual.")
else:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=pdf["t"], y=pdf["voltaje"], mode="lines+markers",
                              name="Voltaje [V]"))
    fig1.add_trace(go.Scatter(x=pdf["t"], y=pdf["voltaje_suav"], mode="lines",
                              name=f"Suavizado (win={win})"))
    fig1.update_layout(xaxis_title="t (muestra)", yaxis_title="Voltaje [V]", height=360)
    st.plotly_chart(fig1, use_container_width=True)

# ------------------------- 2) Serie en mV (usuario único) -------------------------
st.subheader("2) Serie en mV (usuario único)")
if pdf.empty:
    st.info("Sin datos para la serie en mV.")
else:
    fig2 = px.line(pdf.sort_values("t"), x="t", y="mV", markers=True, height=320)
    fig2.update_layout(xaxis_title="t (muestra)", yaxis_title="mV", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------- 3) Boxplot (sensor, todos los usuarios) -------------------------
st.subheader("3) Boxplot por usuario del sensor seleccionado")
box_df = (data.filter(pl.col("sensor")==sel_sensor)
              .select(["usuario","voltaje"]).to_pandas())
if box_df.empty:
    st.info("Sin datos para el boxplot.")
else:
    # Ordena usuarios en el boxplot
    cat_order = (pd.Series(box_df["usuario"]).astype(int).sort_values().astype(str).unique().tolist())
    st.plotly_chart(px.box(box_df, x="usuario", y="voltaje", points="outliers",
                           category_orders={"usuario": cat_order},
                           height=380),
                    use_container_width=True)

# ------------------------- 4) Heatmap t × usuario (sensor seleccionado) -------------------------
st.subheader("4) Heatmap — Media por t × usuario (sensor seleccionado)")
heat = (data.filter(pl.col("sensor")==sel_sensor)
            .group_by(["usuario","t"]).agg(val=pl.col("voltaje").mean())
            .to_pandas()
            .pivot(index="t", columns="usuario", values="val"))
if heat.empty:
    st.info("Sin datos para el heatmap.")
else:
    # Ordena columnas 1→60
    heat = heat.reindex(sorted(heat.columns, key=lambda x: int(x)), axis=1)
    st.plotly_chart(px.imshow(heat, aspect="auto", origin="lower", height=500,
                              color_continuous_scale="Viridis"),
                    use_container_width=True)

# ------------------------- 5) z-score (usuario único) -------------------------
st.subheader("5) z-score del usuario")
if pdf.empty:
    st.info("Sin datos para z-score.")
else:
    st.plotly_chart(px.scatter(pdf, x="t", y="zscore", height=320,
                               labels={"zscore":"z-score"}),
                    use_container_width=True)

# ------------------------- Tabla -------------------------
st.subheader("Vista tabular (usuario seleccionado)")
st.dataframe(pdf.sort_values("t").reset_index(drop=True))
