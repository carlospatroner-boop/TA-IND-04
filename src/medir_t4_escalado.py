"""medir_t4_escalado.py -- Medicion individual (TA-IND-04, Carpio Mendoza Carlos Jose).

Replica EXACTAMENTE el protocolo de medicion.py y transformaciones_spark.py del equipo PE-U4
(commit 1d643b0c1f71a1cfd951c3e8e7169744010d1420 de
https://github.com/carlospatroner-boop/pe-u4-spark-Soporte-Tecnico-ISP), pero para T4
(columna derivada / UDF de prioridad) en local[1], local[2] y local[4] -- escalado que el
equipo NO midio para T4 (solo lo hizo para T3). Esta corrida llena ese vacio para el informe
individual TA-IND-04, cuyo foco declarado es T4.

Mismo dataset (fcc_consumer_complaints.csv, 600000 filas), misma UDF de referencia.py, mismo
protocolo de medicion.py (1 warmup + 5 repeticiones cronometradas, materializacion con count(),
mediana). Se ejecuta en esta maquina local (no Docker, no Colab/Databricks) -- se declara la
plataforma real y las versiones efectivas en la salida.
"""

import argparse
import csv
import json
import os
import platform
import sys

# Reutiliza el codigo del equipo tal cual, sin modificarlo: medicion.py y referencia.py son
# copias sin modificar del commit 1d643b0c1f71a1cfd951c3e8e7169744010d1420 del repositorio de
# origen (ver README.md), vendorizadas en este mismo directorio para que la medicion sea
# reproducible clonando unicamente este repositorio.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyspark.sql import SparkSession, functions as F  # noqa: E402
from pyspark.sql.types import StringType  # noqa: E402

import referencia  # noqa: E402
from medicion import medir  # noqa: E402

_prioridad_udf = F.udf(referencia.clasificar_prioridad, StringType())


def crear_sesion(master: str, app_name: str, executor_instances: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master(master)
        .config("spark.executor.instances", executor_instances)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def cargar_dataset(spark: SparkSession, path: str):
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    df = df.replace("None", None)
    df = df.withColumn(
        "ticket_created", F.to_timestamp("ticket_created", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
    )
    return df


def t4_columna_derivada(df):
    return df.withColumn("prioridad", _prioridad_udf(F.col("issue_type"), F.col("issue")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="../data/raw/fcc_consumer_complaints.csv",
                         help="Ruta al CSV crudo (no versionado, ver data/README_dataset.md "
                              "del repositorio de origen para regenerarlo).")
    parser.add_argument("--out-dir", default="../datos")
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    resumen_por_n = {}
    filas_crudas = []
    config_por_n = {}
    conteo_filas = None

    for n in (1, 2, 4):
        print(f"\n>>> T4_columna_derivada con local[{n}] ...")
        spark = crear_sesion(master=f"local[{n}]", app_name=f"ta-ind-04-carpio-t4-n{n}", executor_instances=str(n))
        try:
            config_efectiva = dict(spark.sparkContext.getConf().getAll())
            config_por_n[n] = config_efectiva
            with open(os.path.join(args.out_dir, f"spark_config_efectiva_t4_n{n}.json"), "w") as f:
                json.dump(config_efectiva, f, indent=2)

            df = cargar_dataset(spark, args.data)
            if conteo_filas is None:
                conteo_filas = df.count()
                print(f"Filas cargadas: {conteo_filas}")

            r = medir("T4_columna_derivada", lambda: t4_columna_derivada(df), reps=5, warmup=1,
                       materialize=lambda d: d.count())
            for i, t in enumerate(r.tiempos_s, start=1):
                filas_crudas.append(["pyspark", f"T4_columna_derivada_N{n}", i, round(t, 6)])
            resumen_por_n[n] = r.mediana_s
            print(f"  N={n}  mediana = {r.mediana_s:.4f} s  (tiempos: {[round(t,4) for t in r.tiempos_s]})")
        finally:
            spark.stop()

    with open(os.path.join(args.out_dir, "t4_escalado_executors.json"), "w") as f:
        json.dump(resumen_por_n, f, indent=2)

    path_crudos = os.path.join(args.out_dir, "tiempos_crudos_t4_escalado.csv")
    with open(path_crudos, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["motor", "transformacion", "repeticion", "tiempo_s"])
        w.writerows(filas_crudas)

    plataforma = {
        "descripcion": "Ejecucion local (no Docker, no Colab, no Databricks) para completar el "
                        "escalado de la transformacion foco T4, no medido por el equipo en PE-U4.",
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count_logico": os.cpu_count(),
        "filas_dataset": conteo_filas,
        "dataset": os.path.basename(args.data),
    }
    import pyspark
    plataforma["pyspark_version"] = pyspark.__version__
    with open(os.path.join(args.out_dir, "plataforma_medicion_individual.json"), "w") as f:
        json.dump(plataforma, f, indent=2)

    print("\nResumen T4_columna_derivada por numero de executors (local[N]):")
    for n, v in resumen_por_n.items():
        print(f"  N={n}: {v:.4f} s")
    print("\nPlataforma:", json.dumps(plataforma, indent=2))


if __name__ == "__main__":
    main()
