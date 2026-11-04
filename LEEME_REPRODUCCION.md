# Ejecución reproducible

1. Colocar `MonteCarlo_1000corridas_17tramos.xlsx` en `/mnt/data/` o adaptar su ruta en los scripts.
2. Ejecutar `python reproducir_montecarlo.py` para M2–M5 y métricas.
3. Ejecutar `python agregar_M1.py` para la clasificación AHP global M1 y agregar sus fronteras.
4. Ejecutar `python completar_reporte.py` para tablas de comparación pareada, intervalos bootstrap, figura y reporte.

Se requiere Python, numpy, pandas, scipy, matplotlib, openpyxl y PyWavelets. El archivo `Codigo_original/Experimento Inglés.ipynb` es el original y `motor_original.py` extrae sus funciones sin modificar las reglas. Los scripts son auditoría externa.

Los porcentajes de cobertura y de reporte Poor **no se calculan para M1** porque su clasificación es global, no específica de cada dimensión. Los intervalos bootstrap son descriptivos y condicionales a las corridas suministradas.
