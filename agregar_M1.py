"""Run original global AHP (M1) on 1000 Monte Carlo profiles, after reproducir_montecarlo.py."""
from pathlib import Path
import pandas as pd,numpy as np,contextlib,io,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'01_Algoritmos_originales'))
with contextlib.redirect_stdout(io.StringIO()):import motor_original as mo
ns=mo.ns
raw=pd.read_excel('/mnt/data/MonteCarlo_1000corridas_17tramos.xlsx',sheet_name='Base_Ancha')
rows=[];zones=[]
for runid,g in raw.groupby('Corrida'):
 for i,(_,r) in enumerate(g.sort_values('Tramo').iterrows()):
  score,lab,cls=ns['evaluar_tramo']({k:float(r[k]) for k in ['CF','TX','IRI','JF','LTE','DEF']},ns['pesos_globales'],ns['pesos_alt_vec'],ns['umbrales'])
  zones.append((int(runid),'M1',i+1,round(i*.3,10),round((i+1)*.3,10),lab))
 rows.append(dict(Corrida=int(runid),Metodo='M1',Fronteras_unicas=16,Reduccion_pct=0,Cobertura_pares=np.nan,Cobertura_pct=np.nan,Pares_criticos=np.nan,Criticos_reportados_poor=np.nan,Reporte_criticos_pct=np.nan,Ambiguedades_etapa=np.nan,Contraste_retenidas=np.nan,Contraste_omitidas=np.nan,Diferencia_contraste=np.nan,AUC=np.nan,Registros_zona_original=17))
M=pd.read_csv(P/'metricas_por_corrida.csv');M=M[M.Metodo!='M1'];M=pd.concat([M,pd.DataFrame(rows)],ignore_index=True).sort_values(['Corrida','Metodo']);M.to_csv(P/'metricas_por_corrida.csv',index=False)
Z=pd.read_csv(P/'zonas_originales_montecarlo.csv');Z=Z[Z.Metodo!='M1'];Z=pd.concat([Z,pd.DataFrame(zones,columns=Z.columns)],ignore_index=True).sort_values(['Corrida','Metodo','Registro_original']);Z.to_csv(P/'zonas_originales_montecarlo.csv',index=False)
B=pd.read_csv(P/'auditoria_fronteras.csv');B=B[B.Metodo!='M1'];base=B[B.Metodo=='M2'].copy();base['Metodo']='M1';B=pd.concat([B,base],ignore_index=True).sort_values(['Corrida','Metodo','Posicion']);B.to_csv(P/'auditoria_fronteras.csv',index=False)
S=M.groupby('Metodo').agg(Corridas=('Corrida','size'),Fronteras_media=('Fronteras_unicas','mean'),Fronteras_sd=('Fronteras_unicas','std'),Reduccion_media_pct=('Reduccion_pct','mean'),Reduccion_sd_pct=('Reduccion_pct','std'),Cobertura_media_pct=('Cobertura_pct','mean'),Cobertura_sd_pct=('Cobertura_pct','std'),Reporte_criticos_media_pct=('Reporte_criticos_pct','mean'),Reporte_criticos_sd_pct=('Reporte_criticos_pct','std'),Ambiguedades_media=('Ambiguedades_etapa','mean'),AUC_media=('AUC','mean'),Contraste_diferencia_media=('Diferencia_contraste','mean')).reset_index();S.to_csv(P/'resumen_montecarlo.csv',index=False)
