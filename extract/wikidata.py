import json
from datetime import datetime, timezone
from pathlib import Path
import requests

RAIZ = Path(__file__).resolve().parent.parent
ENDPOINT = "https://query.wikidata.org/sparql"

# Modelos de auto lanzados antes de 1990, con su marca y país
CONSULTA = """
SELECT ?modelo ?modeloLabel ?marcaLabel ?paisLabel ?paisMarcaLabel ?inicio WHERE {
  ?modelo wdt:P31 wd:Q3231690 ;
          wdt:P571 ?inicio .
  FILTER(YEAR(?inicio) < 1990)
  OPTIONAL { ?modelo wdt:P176 ?marca .
             OPTIONAL { ?marca wdt:P17 ?paisMarca . } }
  OPTIONAL { ?modelo wdt:P495 ?pais . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
}
"""

def extraer():
    respuesta = requests.get(
        ENDPOINT,
        params={"query": CONSULTA, "format": "json"},
        headers={"User-Agent": "autos-antiguos-pipeline/0.1 (proyecto educativo)"},
        timeout=120,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()

    carpeta = RAIZ / "data" / "raw" / "wikidata"
    carpeta.mkdir(parents=True, exist_ok=True)
    marca_tiempo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    ruta = carpeta / f"modelos_{marca_tiempo}.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")

    print(f"{len(datos['results']['bindings'])} modelos guardados en {ruta}")

if __name__ == "__main__":
    extraer()