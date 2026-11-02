from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")   # genera imágenes sin abrir ventanas
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent

def graficar():
    carpeta = RAIZ / "docs" / "img"
    carpeta.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(RAIZ / "warehouse" / "autos.duckdb"), read_only=True)
    decadas = con.sql("""
        SELECT decada, COUNT(*) AS modelos
        FROM modelos GROUP BY decada ORDER BY decada
    """).df()
    paises = con.sql("""
        SELECT pais, COUNT(*) AS modelos
        FROM modelos WHERE pais IS NOT NULL
        GROUP BY pais ORDER BY modelos DESC LIMIT 10
    """).df()
    con.close()

    # Gráfico 1: modelos por década
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(decadas["decada"].astype(str), decadas["modelos"], color="#8B4513")
    ax.set_title("Modelos de autos lanzados por década (fuente: Wikidata)")
    ax.set_xlabel("Década")
    ax.set_ylabel("Cantidad de modelos")
    fig.tight_layout()
    fig.savefig(carpeta / "modelos_por_decada.png", dpi=150)
    plt.close(fig)

    # Gráfico 2: top 10 países (barras horizontales, el mayor arriba)
    paises = paises.sort_values("modelos")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(paises["pais"], paises["modelos"], color="#2F4F4F")
    ax.set_title("Top 10 países por cantidad de modelos (fuente: Wikidata)")
    ax.set_xlabel("Cantidad de modelos")
    fig.tight_layout()
    fig.savefig(carpeta / "top_paises.png", dpi=150)
    plt.close(fig)

    print(f"Gráficos guardados en {carpeta}")

if __name__ == "__main__":
    graficar()