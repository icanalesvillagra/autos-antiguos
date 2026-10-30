from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
con = duckdb.connect(str(RAIZ / "warehouse" / "autos.duckdb"), read_only=True)

print("Top 10 países con más modelos:")
print(con.sql("""
    SELECT pais, COUNT(*) AS modelos
    FROM modelos
    WHERE pais IS NOT NULL
    GROUP BY pais
    ORDER BY modelos DESC
    LIMIT 10
""").df())

print("\nPaís líder de cada década:")
print(con.sql("""
    SELECT decada, pais, COUNT(*) AS modelos
    FROM modelos
    WHERE pais IS NOT NULL
    GROUP BY decada, pais
    QUALIFY ROW_NUMBER() OVER (PARTITION BY decada ORDER BY COUNT(*) DESC) = 1
    ORDER BY decada
""").df())