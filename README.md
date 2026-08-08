# TA-IND-04 — Análisis de Rendimiento Paralelo aplicado al PFC (individual)

**Asignatura:** Aplicaciones Distribuidas (ISR-701) · Unidad 4 · Universidad Técnica Estatal de
Quevedo · Facultad de Ciencias de la Computación · Carrera de Ingeniería de Software
**Docente responsable:** Gleiston C. Guerrero-Ulloa, M.Sc. · **Período:** 2026–2027 PPA

## Identificación

| Campo | Valor |
|---|---|
| Estudiante | Carpio Mendoza Carlos Jose |
| Correo | carlospatroner@gmail.com |
| Equipo PE-U4 / GA-SUM-05 | ACC — Soporte Técnico ISP (Alvarez Parraga Jeremy Alexis, Aucatoma Celorio Jhinson Stalyn, Carpio Mendoza Carlos Jose) |
| PFC de referencia | ACC — Soporte Técnico ISP (sistema de gestión de tickets de soporte técnico, microservicios) |
| Transformación declarada como foco individual | **T4 — Columna derivada compleja** (clasificación de prioridad) |

## Trazabilidad de los datos base

- **Repositorio de origen (equipo PE-U4):** https://github.com/carlospatroner-boop/pe-u4-spark-Soporte-Tecnico-ISP
- **Commit exacto:** `1d643b0c1f71a1cfd951c3e8e7169744010d1420`
- Verificado con:
  ```bash
  GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/carlospatroner-boop/pe-u4-spark-Soporte-Tecnico-ISP.git HEAD
  ```
- Tabla de tiempos base de las 5 transformaciones tomada de `resultados/tiempos_resumen.csv`
  de ese commit, copiada sin alterar a [`datos/tiempos_base.csv`](datos/tiempos_base.csv)
  (filas `tabla_base`).

## Dato añadido para este informe individual

El equipo **no midió el escalado N=1,2,4 executors para T4** (solo lo hizo para T3, ver
`resultados/t3_escalado_executors.json` del repo de origen). Como T4 es la transformación
declarada como foco de este informe, esa medición era obligatoria (Anexo A de la guía). Se
ejecutó de forma individual, reutilizando sin modificar el código del equipo
(`medicion.py`, `transformaciones_spark.py`, `referencia.py`), en una máquina local (no el
contenedor Docker del equipo, no Colab, no Databricks). Detalle de plataforma, script y
resultados crudos en [`datos/`](datos/) (filas `escalado_foco_T4` de `tiempos_base.csv`,
`tiempos_crudos_t4_escalado.csv`, `amdahl_fit_t4.json`, `umbral_rentabilidad_t4.json`,
`plataforma_medicion_individual.json`).

## Estructura del repositorio

```
ta-ind-04-carpio/
├── README.md                    (este archivo)
├── LICENSE
├── docs/
│   ├── TA_IND_04_Informe.tex
│   ├── TA_IND_04_Informe.pdf
│   └── references.bib
├── src/
│   ├── medicion.py           (copia sin modificar, commit 1d643b0c... del equipo)
│   ├── referencia.py         (copia sin modificar, commit 1d643b0c... del equipo)
│   ├── amdahl.py             (copia sin modificar, commit 1d643b0c... del equipo)
│   ├── medir_t4_escalado.py  (medición propia: T4 en local[1,2,4])
│   ├── analisis_t4.py        (ajuste de Amdahl/Karp-Flatt + figuras propias)
│   └── umbral_t4.py          (alpha, beta, gamma y n* — Ec. 4)
├── datos/
│   ├── tiempos_base.csv                    (tabla Anexo A: 5 transf. + escalado propio T4)
│   ├── tiempos_crudos_t4_escalado.csv      (15 mediciones crudas: T4 x N=1,2,4 x 5 repeticiones)
│   ├── amdahl_fit_t4.json                  (ajuste de p, S_max, N para 90% S_max)
│   ├── umbral_rentabilidad_t4.json         (alpha, beta, gamma, n* para N=2 y N=4)
│   ├── plataforma_medicion_individual.json (entorno exacto de la medición propia)
│   └── spark_config_efectiva_t4_n{1,2,4}.json (configuración efectiva de cada sesión Spark)
└── figuras/
    ├── fig_speedup.png       (figura propia, 300 DPI — speedup T4 vs. curva de Amdahl)
    └── fig_eficiencia_t4.png (figura propia, 300 DPI — eficiencia T4 vs. N)
```

## Compilación del informe

Requiere una distribución LaTeX con `biblatex` + estilo `biblatex-ieee` + `biber` (Overleaf ya
los trae preinstalados; en TeX Live/MiKTeX completos también están disponibles).

```bash
cd docs
pdflatex TA_IND_04_Informe.tex
biber TA_IND_04_Informe
pdflatex TA_IND_04_Informe.tex
pdflatex TA_IND_04_Informe.tex
```

Secuencia exacta: **pdflatex → biber → pdflatex → pdflatex** (dos pasadas finales para resolver
referencias cruzadas y la bibliografía). El PDF resultante se committea en
`docs/TA_IND_04_Informe.pdf`.

## Reproducir la medición propia de T4 (N=1,2,4)

Requiere el CSV crudo del dataset (`fcc_consumer_complaints.csv`, 600 000 filas, ver
`data/README_dataset.md` del repositorio de origen para el comando de descarga) y PySpark 4.1.2
+ Java 21.

```bash
python src/medir_t4_escalado.py --data <ruta al csv crudo> --out-dir datos/
python src/analisis_t4.py
python src/umbral_t4.py
```

## Declaración de uso de inteligencia artificial generativa

Se utilizó Claude (Anthropic) como asistente para: verificar la trazabilidad del commit de
origen, redactar el script de la medición propia de escalado de T4 (reutilizando sin modificar
el código de medición del equipo), apoyar la redacción y composición en LaTeX del informe, y
buscar/verificar las referencias bibliográficas propias. El análisis, la interpretación de los
resultados y las conclusiones son responsabilidad del autor. Declaración completa en la última
sección de `docs/TA_IND_04_Informe.tex`.
