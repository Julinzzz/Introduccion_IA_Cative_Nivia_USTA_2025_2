
# etl_polars.py
# ETL sencillo con Polars para BD_SENSORES.xlsx
# Ejecuta:  python etl_polars.py --input BD_SENSORES.xlsx --out data/clean.parquet
# Requiere: polars>=0.20, openpyxl

import argparse, os, re
import polars as pl

def read_sheet(path:str, sheet:str) -> pl.DataFrame:
    """
    Lee una hoja usando Polars (con fallback a pandas si es necesario)
    y retorna en formato largo: [usuario, t, voltaje, sensor].
    """
    try:
        df = pl.read_excel(path, sheet_name=sheet)
    except Exception:
        import pandas as pd
        df = pl.from_pandas(pd.read_excel(path, sheet_name=sheet))

    # Elimina filas totalmente vacías
    df = df.drop_nulls(subset=None, how="any").fill_null(None) if "Usuario" in df.columns else df

    # Normaliza nombres de columnas a str
    df = df.rename({c: str(c) for c in df.columns})

    if "Usuario" not in df.columns:
        df = df.with_columns(pl.lit(None).alias("Usuario"))
        # ubica 'Usuario' como primera columna
        cols = ["Usuario"] + [c for c in df.columns if c != "Usuario"]
        df = df.select(cols)

    value_cols = [c for c in df.columns if c != "Usuario"]

    # Limpia caracteres no numéricos (ej: "1.42 V") y castea a float
    clean_exprs = [pl.col(c).cast(pl.Utf8).str.replace_all(r"[^0-9\.\-]", "").cast(pl.Float64).alias(c)
                   for c in value_cols]
    df = df.with_columns(clean_exprs)

    # Pasa a formato largo
    long = df.melt(id_vars="Usuario", variable_name="t", value_name="voltaje").drop_nulls(["t","voltaje"])
    long = long.with_columns([
        pl.col("t").cast(pl.Int64, strict=False),
        pl.lit(sheet).alias("sensor"),
        # si "Usuario" viene vacío, usar índice incremental como id de registro
        pl.arange(0, pl.len()).alias("_row")
    ])
    # Usuario robusto: prioridad a columna, si NA usar _row
    long = long.with_columns(
        pl.when(pl.col("Usuario").is_null())
          .then(pl.col("_row"))
          .otherwise(pl.col("Usuario"))
          .alias("usuario")
    ).drop(["Usuario","_row"])

    return long

def build_dataset(path:str) -> pl.DataFrame:
    xls = pl.read_excel(path, sheet_name=None)  # solo para obtener hojas si es posible
    sheets = list(xls.keys()) if isinstance(xls, dict) else None
    if not sheets:
        # Fallback a pandas para listar hojas
        import pandas as pd
        sheets = pd.ExcelFile(path).sheet_names

    frames = []
    for sh in sheets:
        try:
            frames.append(read_sheet(path, sh))
        except Exception as e:
            print(f"[WARN] Hoja '{sh}' omitida por error: {e}")

    data = pl.concat(frames, how="vertical_relaxed")
    # Derivadas y limpieza adicional
    data = data.with_columns([
        (pl.col("voltaje")*1000).alias("mV"),
        pl.col("voltaje").group_by_dynamic(index_column="t", every="1i").mean().over(["sensor","usuario"]),
    ])

    # Z-score por sensor
    by_sensor = data.group_by("sensor").agg(
        media = pl.col("voltaje").mean(),
        sigma = pl.col("voltaje").std(ddof=1)
    )
    data = data.join(by_sensor, on="sensor", how="left").with_columns(
        ((pl.col("voltaje") - pl.col("media")) / pl.col("sigma")).alias("zscore")
    ).drop(["media","sigma"])

    # Señal suavizada por usuario/sensor (ventana 5)
    data = data.sort(["sensor","usuario","t"]).with_columns(
        pl.col("voltaje").rolling_mean(window_size=5, min_periods=1).over(["sensor","usuario"]).alias("voltaje_suav")
    )

    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="Ruta al Excel BD_SENSORES.xlsx")
    ap.add_argument("--out", "-o", default="data/clean.parquet", help="Salida parquet/csv")
    args = ap.parse_args()

    data = build_dataset(args.input)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    if args.out.endswith(".csv"):
        data.write_csv(args.out)
    else:
        data.write_parquet(args.out)
    print(f"[OK] Dataset limpio -> {args.out} | filas={data.height}, columnas={data.width}")

if __name__ == "__main__":
    main()
