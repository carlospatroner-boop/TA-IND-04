"""analisis_t4.py -- Analisis de Amdahl/Karp-Flatt para T4 (foco individual, Carpio),
replicando el metodo de PE-U4/src/graficas.py (equipo) pero sobre los datos propios de
escalado T4 medidos en medir_t4_escalado.py.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from amdahl import (
    eficiencia,
    fraccion_serial_inversa,
    n_para_fraccion_de_maximo,
    speedup_amdahl,
    speedup_maximo,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(HERE, "..", "datos")
FIGURAS = os.path.join(HERE, "..", "figuras")

with open(os.path.join(DATOS, "t4_escalado_executors.json")) as f:
    t4_por_n = json.load(f)

ns = sorted(int(n) for n in t4_por_n.keys())
tiempos = {n: t4_por_n[str(n)] for n in ns}
t1 = tiempos[1]
speedup_obs = {n: t1 / tiempos[n] for n in ns}

p_por_n = {n: fraccion_serial_inversa(n, speedup_obs[n]) for n in ns if n > 1}
n_max = max(p_por_n.keys())
p_principal = p_por_n[n_max]

ns_arr = np.array(ns, dtype=float)
s_arr = np.array([speedup_obs[n] for n in ns], dtype=float)
popt, _ = curve_fit(speedup_amdahl, ns_arr, s_arr, p0=[0.5], bounds=(0, 0.999))
p_ajustado = float(popt[0])

s_max = speedup_maximo(p_principal)
n_90 = n_para_fraccion_de_maximo(p_principal, 0.9)

s_max_ls = speedup_maximo(p_ajustado)
n_90_ls = n_para_fraccion_de_maximo(p_ajustado, 0.9)

resultado = {
    "N_medidos": ns,
    "tiempos_s": tiempos,
    "speedup_observado": speedup_obs,
    "eficiencia_observada": {n: eficiencia(speedup_obs[n], n) for n in ns},
    "p_por_N_ec4": p_por_n,
    "p_principal_ec4": p_principal,
    "N_usado_para_p_principal": n_max,
    "p_ajustado_minimos_cuadrados": p_ajustado,
    "S_max": s_max,
    "N_para_90pct_S_max": n_90,
    "S_max_ls": s_max_ls,
    "N_para_90pct_S_max_ls": n_90_ls,
}

with open(os.path.join(DATOS, "amdahl_fit_t4.json"), "w") as f:
    json.dump(resultado, f, indent=2)

print("=== Analisis de Amdahl (T4, escalado propio de executors) ===")
for n in ns:
    print(f"  N={n}: T={tiempos[n]:.4f}s  S_obs={speedup_obs[n]:.4f}  E_obs={eficiencia(speedup_obs[n], n):.4f}")
for n, p in p_por_n.items():
    print(f"  e/p Karp-Flatt (Ec. 2/4, N={n}) = {p:.4f}")
print(f"  p principal (N={n_max}) = {p_principal:.4f}")
print(f"  p ajuste minimos cuadrados (todos los N) = {p_ajustado:.4f}")
print(f"  S_max (con p principal) = {s_max:.4f}")
print(f"  N para 90% S_max (con p principal) = {n_90:.2f}")
print(f"  S_max (con p ajustado LS) = {s_max_ls:.4f}")
print(f"  N para 90% S_max (con p ajustado LS) = {n_90_ls:.2f}")

# ---- Figura propia: speedup observado vs curva de Amdahl teorica (para el .tex) ----
n_smooth = np.linspace(1, 16, 300)
s_smooth = speedup_amdahl(n_smooth, p_principal)

plt.figure(figsize=(7, 5))
plt.plot(ns, [speedup_obs[n] for n in ns], "o-", color="#2563eb", linewidth=2, markersize=7,
         label="Speedup observado (T4, columna derivada)")
plt.plot(n_smooth, s_smooth, "--", color="#dc2626", linewidth=1.8,
         label=f"Amdahl teórico (p={p_principal:.3f})")
plt.axhline(s_max, color="gray", linestyle=":", label=f"$S_{{max}}$={s_max:.2f}")
plt.xlabel("Número de executors (N)")
plt.ylabel("Speedup S(N)")
plt.title("T4 (columna derivada): speedup observado vs. curva de Amdahl")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
os.makedirs(FIGURAS, exist_ok=True)
plt.savefig(os.path.join(FIGURAS, "fig_speedup.png"), dpi=300)
plt.close()

# ---- Figura eficiencia ----
e_smooth = [eficiencia(speedup_amdahl(n, p_principal), n) for n in n_smooth]
e_obs = [eficiencia(speedup_obs[n], n) for n in ns]
plt.figure(figsize=(7, 5))
plt.plot(ns, e_obs, "o-", color="#2563eb", linewidth=2, markersize=7, label="Eficiencia observada (T4)")
plt.plot(n_smooth, e_smooth, "--", color="#dc2626", linewidth=1.8, label=f"Eficiencia teórica Amdahl (p={p_principal:.3f})")
plt.xlabel("Número de executors (N)")
plt.ylabel("Eficiencia E(N) = S(N)/N")
plt.title("T4 (columna derivada): eficiencia del paralelismo vs. N")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, "fig_eficiencia_t4.png"), dpi=300)
plt.close()

print("\nFiguras guardadas en", FIGURAS)
