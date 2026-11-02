from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "clean" / "modelos.csv"

# Cada regla es una consulta SQL que devuelve True (pasa) o False (falla)
REGLAS = [
    ("Hay al menos 100 modelos",
     "SELECT COUNT(*) >= 100 FROM datos"),
    ("modelo_id es único",
     "SELECT COUNT(*) = COUNT(DISTINCT modelo_id) FROM datos"),
    ("Ningún modelo sin nombre",
     "SELECT COUNT(*) FILTER (WHERE modelo_nombre IS NULL) = 0 FROM datos"),
    ("Años entre 1885 y 1989",
     "SELECT COUNT(*) FILTER (WHERE anio_inicio NOT BETWEEN 1885 AND 1989) = 0 FROM datos"),
    ("Máximo 25% de países faltantes",
     "SELECT AVG(CASE WHEN pais IS NULL THEN 1 ELSE 0 END) <= 0.25 FROM datos"),
]

def validar():
    con = duckdb.connect()   # sin archivo: base de datos temporal en memoria
    con.execute(f"CREATE VIEW datos AS SELECT * FROM read_csv_auto('{CSV.as_posix()}')")

    fallas = []
    for descripcion, sql in REGLAS:
        pasa = con.execute(sql).fetchone()[0]
        print(f"{'✔' if pasa else '✘'} {descripcion}")
        if not pasa:
            fallas.append(descripcion)
    con.close()

    if fallas:
        raise ValueError(f"Validación fallida, no se cargará el warehouse: {fallas}")

if __name__ == "__main__":
    validar()