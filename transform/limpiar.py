import json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PATRON_CODIGO = r"^Q\d+$"   # detecta códigos tipo "Q12345"

def ultimo_archivo_crudo():
    archivos = sorted((RAIZ / "data" / "raw" / "wikidata").glob("modelos_*.json"))
    if not archivos:
        raise FileNotFoundError("No hay datos crudos. Ejecuta primero extract/wikidata.py")
    return archivos[-1]   # el más reciente (por la fecha en el nombre)

def aplanar(datos):
    filas = []
    for registro in datos["results"]["bindings"]:
        filas.append({campo: v["value"] for campo, v in registro.items()})
    return pd.DataFrame(filas)

def transformar():
    ruta = ultimo_archivo_crudo()
    df = aplanar(json.loads(ruta.read_text(encoding="utf-8")))
    print(f"Leído: {ruta.name} -> {len(df)} filas crudas")

    # 1. Nombres de columnas claros
    df = df.rename(columns={"modeloLabel": "modelo_nombre",
                            "marcaLabel": "marca", "paisLabel": "pais",
                            "paisMarcaLabel": "pais_marca"})          # CAMBIO 1
    for col in ["marca", "pais", "pais_marca"]:                       # CAMBIO 1
        if col not in df:
            df[col] = pd.NA

    # 2. ID corto del modelo (de la URL nos quedamos con "Q...")
    df["modelo_id"] = df["modelo"].str.split("/").str[-1]

    # 3. Año y década
    df["anio_inicio"] = pd.to_numeric(df["inicio"].str[:4], errors="coerce").astype("Int64")
    df["decada"] = (df["anio_inicio"] // 10) * 10

    # 4. Nulos disfrazados: un código "Q123" no es un nombre real
    for col in ["modelo_nombre", "marca", "pais", "pais_marca"]:     # CAMBIO 2
        df.loc[df[col].str.match(PATRON_CODIGO, na=False), col] = pd.NA

    # 4b. Si el modelo no tiene país, usamos el país de su fabricante  # CAMBIO 3
    df["pais"] = df["pais"].fillna(df["pais_marca"])

    # 5. Fechas imposibles (el automóvil se inventó en 1885-1886)
    df = df[df["anio_inicio"].between(1885, 1989)]

    # 6. Una fila por modelo: si hay duplicados, nos quedamos con el año más antiguo
    antes = len(df)
    df = df.sort_values("anio_inicio").drop_duplicates(subset="modelo_id", keep="first")
    print(f"Duplicados eliminados: {antes - len(df)}")

    # 7. Sin nombre no sirve para el análisis
    df = df.dropna(subset=["modelo_nombre"])

    df = df[["modelo_id", "modelo_nombre", "marca", "pais", "anio_inicio", "decada"]]

    carpeta = RAIZ / "data" / "clean"
    carpeta.mkdir(parents=True, exist_ok=True)
    df.to_csv(carpeta / "modelos.csv", index=False, encoding="utf-8")

    print(f"Filas limpias: {len(df)}")
    print("\nDatos faltantes por columna:")
    print(df.isna().sum())
    print("\nModelos por década:")
    print(df["decada"].value_counts().sort_index())

if __name__ == "__main__":
    transformar()