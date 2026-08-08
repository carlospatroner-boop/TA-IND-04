"""umbral_t4.py -- Ajuste de alpha, beta, gamma y calculo del umbral de rentabilidad n*
(Ec. 4 de la guia TA-IND-04) para T4, usando:
  - T_pandas(n=600000) del commit 1d643b0c... del repo del equipo (T_sec(n)=alpha*n)
  - Las 3 mediciones propias de escalado T4 en N=1,2,4 (T_dist(n,N)=beta+gamma*n/N)
"""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(HERE, "..", "datos")

n_filas = 600000
t_pandas_t4 = 0.355890  # mediana pandas T4, commit 1d643b0c..., tiempos_crudos.csv

with open(os.path.join(DATOS, "t4_escalado_executors.json")) as f:
    t4_por_n = json.load(f)

alpha = t_pandas_t4 / n_filas

xs = np.array([n_filas / int(N) for N in t4_por_n.keys()])
ys = np.array([t4_por_n[N] for N in t4_por_n.keys()])

# Regresion lineal T = beta + gamma * (n/N)
A = np.vstack([np.ones_like(xs), xs]).T
(beta, gamma), residuals, rank, sv = np.linalg.lstsq(A, ys, rcond=None)

resultado = {"alpha_s_por_fila": alpha, "beta_s": float(beta), "gamma_s": float(gamma),
             "n_filas_dataset": n_filas, "t_pandas_t4_s": t_pandas_t4}

for N in (2, 4):
    gamma_sobre_N = gamma / N
    valido = alpha > gamma_sobre_N
    n_star = beta / (alpha - gamma_sobre_N) if valido else None
    resultado[f"N={N}"] = {
        "gamma_sobre_N": gamma_sobre_N,
        "alpha_mayor_gamma_sobre_N": bool(valido),
        "n_estrella": n_star,
    }
    print(f"N={N}: gamma/N={gamma_sobre_N:.6e}  alpha={alpha:.6e}  valido={valido}  n*={n_star:,.0f}" if valido else f"N={N}: no valido")

print(json.dumps(resultado, indent=2))
with open(os.path.join(DATOS, "umbral_rentabilidad_t4.json"), "w") as f:
    json.dump(resultado, f, indent=2)
