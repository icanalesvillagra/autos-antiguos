from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent

def cargar():
    csv = RAIZ / "data" / "clean" / "modelos.csv"
    if not csv.exists():
        raise FileNotFoundError("No hay datos limpios. Ejecuta primero transform/limpiar.py")

    carpeta = RAIZ / "warehouse"
    carpeta.mkdir(exist_ok=True)

    con = duckdb.connect(str(carpeta / "autos.duckdb"))
    con.execute(f"""
        CREATE OR REPLACE TABLE modelos AS
        SELECT * FROM read_csv_auto('{csv.as_posix()}')
    """)
    filas = con.execute("SELECT COUNT(*) FROM modelos").fetchone()[0]
    print(f"Tabla 'modelos' cargada con {filas} filas")
    con.close()

if __name__ == "__main__":
    cargar()