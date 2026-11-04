from pathlib import Path
import pandas as pd,numpy as np,contextlib,io,sys,zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'01_Algoritmos_originales'))
with contextlib.redirect_stdout(io.StringIO()):import motor_original as mo
ns=mo.ns
raw=pd.read_excel('/mnt/data/MonteCarlo_1000corridas_17tramos.xlsx',sheet_name='Base_Ancha')
rows=[];zones=[];bounds=[]
for runid,g in raw.groupby('Corrida'):
 for i,(_,r) in enumerate(g.sort_values('Tramo').iterrows()):
  score,lab,cls=ns['evaluar_tramo']({k:float(r[k]) for k in ['CF','TX','IRI','JF','LTE','DEF']},ns['pesos_globales'],ns['pesos_alt_vec'],ns['umbrales'])
  zones.append((int(runid),'M1',i+1,round(i*.3,10),round((i+1)*.3,10),lab))
 for k in range(1,17):bounds.append((int(runid),'M1',k,np.nan,1))
 rows.append(dict(Corrida=int(runid),Metodo='M1',Fronteras_unicas=16,Reduccion_pct=0,Cobertura_pares=np.nan,Cobertura_pct=np.nan,Pares_criticos=np.nan,Criticos_reportados_poor=np.nan,Reporte_criticos_pct=np.nan,Ambiguedades_etapa=np.nan,Contraste_retenidas=np.nan,Contraste_omitidas=np.nan,Diferencia_contraste=np.nan,AUC=np.nan,Registros_zona_original=17))
M=pd.read_csv(P/'metricas_por_corrida.csv')
S=pd.read_csv(P/'resumen_montecarlo.csv')
# Distribution figures
fig,axs=plt.subplots(1,3,figsize=(14,4.2))
for ax,col,title in zip(axs,['Reduccion_pct','Cobertura_pct','Reporte_criticos_pct'],['Internal-boundary reduction','Documented hierarchical coverage','Critical conditions reported Poor']):
 vals=[M[M.Metodo==f'M{k}'][col].dropna().to_numpy() for k in [1,2,3,4,5]]
 vals=[v for v in vals if len(v)]
 ax.boxplot(vals,positions=[k for k,v in enumerate(vals,1) if len(v)],tick_labels=[f'M{k}' for k,v in enumerate(vals,1) if len(v)],showfliers=False)
 ax.set_title(title);ax.set_ylabel('Percent (%)');ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(P/'distribuciones_montecarlo.png',dpi=170);plt.close(fig)
C=pd.read_csv(P/'comparaciones_pareadas_montecarlo.csv')
# quantiles and bootstrap CI on paired differences for publication-ready robustness
wide=M.pivot(index='Corrida',columns='Metodo')
rows=[]
for a,b in [('M2','M4'),('M3','M5'),('M4','M5'),('M2','M3')]:
 for field in ['Reduccion_pct','Cobertura_pct','Reporte_criticos_pct']:
  delta=(wide[field][b]-wide[field][a]).dropna().to_numpy()
  rng=np.random.default_rng(1729)
  # percentile bootstrap of run-level paired differences, 3000 resamples
  means=np.array([rng.choice(delta,size=len(delta),replace=True).mean() for _ in range(3000)])
  rows.append(dict(Comparacion=f'{b}-{a}',Metrica=field,N=len(delta),Diferencia_media=delta.mean(),Mediana=np.median(delta),Q025=np.quantile(delta,.025),Q975=np.quantile(delta,.975),IC95_bootstrap_media_inferior=np.quantile(means,.025),IC95_bootstrap_media_superior=np.quantile(means,.975),Proporcion_positiva=np.mean(delta>0),Proporcion_cero=np.mean(delta==0)))
Q=pd.DataFrame(rows);Q.to_csv(P/'comparaciones_pareadas_bootstrap.csv',index=False)
report='''# Monte Carlo robustness assessment: 1,000 runs × 17 pavement sections

## Design and traceability

The supplied workbook contains 1,000 simulated runs with 17 consecutive 300-m sections per run and six original indicators (CF, TX, IRI, JF, LTE, DEF). The original notebook functions were applied without changing the AHP weights, normative thresholds, strict/tolerant progression rules, DWT/CDA parameters, or original zone records and overlaps. The analyses below are post-processing only. M1 is a global AHP classification and therefore has no comparable dimension-specific hierarchical coverage or Poor-reporting rate; these are intentionally shown as missing, not zero.

**Important limitation:** the workbook alone does not establish the Monte Carlo generation mechanism or independence between runs. Confidence intervals describe variation across the supplied runs under a conditional run-level resampling assumption, not field-validated uncertainty.

## Results

'''+S.round(3).to_markdown(index=False)+'''\n\n## Paired method comparisons\n\n'''+Q.round(3).to_markdown(index=False)+'''\n\n## Metric definitions\n\n- Boundary count: distinct original internal endpoints, deduplicated only for counting, among 16 possible positions; reduction = (16−count)/16 × 100.\n- Coverage: number of unique (section, dimension) pairs having an original stage label (Bueno/Regular/Malo), divided by 51. Multiple overlapping original records are preserved, but a pair is counted once.\n- Conservative critical reporting: for each dimension, at least one constituent original indicator is Malo; numerator counts those pairs with a dimension-specific final output label Malo. This is not validated sensitivity or a false-negative rate.\n- Boundary contrast: Euclidean distance of adjacent six-indicator profiles after pooled min-max normalization over all 1,000 runs, divided by sqrt(6); AUC compares retained and omitted boundary positions within each run. Undefined when there are no omitted positions.\n- Bootstrap intervals are percentile intervals for the paired run-level mean difference (3,000 resamples, fixed seed 1729).\n\n## Interpretation restrictions\n\nBoundary reduction is not demonstrated improved homogeneity, economic optimization, or diagnostic accuracy. Higher hierarchical coverage is not automatically better classification quality. Overlapping M4/M5 outputs are not reconciled. The original two scenarios remain separate from these Monte Carlo simulations.\n'''
(P/'INFORME_MONTECARLO.md').write_text(report,encoding='utf-8')
with zipfile.ZipFile('/mnt/data/MonteCarlo_Robustez_M1_M5_1000corridas.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in P.iterdir():
  if p.is_file() and p.name!='ejecucion.log':z.write(p,arcname=p.name)
 for p in (P/'01_Algoritmos_originales').iterdir():
  if p.is_file():z.write(p,arcname='Codigo_original/'+p.name)
print(S.to_string(index=False));print('PAIRED\n',Q.to_string(index=False));print('ZIP READY')
