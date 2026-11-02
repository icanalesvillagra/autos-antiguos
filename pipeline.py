import time
from extract.wikidata import extraer
from transform.limpiar import transformar
from load.cargar import cargar
from quality.validar import validar
from analisis.graficos import graficar

PASOS = [
    ("Extraer", extraer),
    ("Transformar", transformar),
    ("Validar", validar),
    ("Cargar", cargar),
    ("Graficar", graficar),
]

def main():
    inicio_total = time.perf_counter()
    for nombre, paso in PASOS:
        print(f"\n=== {nombre} ===")
        inicio = time.perf_counter()
        paso()
        print(f"✔ {nombre} terminado en {time.perf_counter() - inicio:.1f} s")
    print(f"\nPipeline completo en {time.perf_counter() - inicio_total:.1f} s")

if __name__ == "__main__":
    main()