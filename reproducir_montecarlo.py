"""Monte Carlo post-processing preserving original M1–M5 notebook functions."""
from pathlib import Path
import sys, contextlib, io, time
import numpy as np, pandas as pd
from scipy.stats import bootstrap
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'01_Algoritmos_originales'))
with contextlib.redirect_stdout(io.StringIO()):import motor_original as mo
ns=mo.ns
IND=['CF','TX','IRI','JF','LTE','DEF']
AXES={'Safety':['CF','TX'],'Serviceability':['IRI','JF'],'Structural integrity':['LTE','DEF']}
MAP={'BUENO':'BUENO','REGULAR':'REGULAR','MALO':'MALO'}
def decode(x):
 s=str(x).lower();ax=('Safety' if 'seguridad' in s else 'Serviceability' if 'operatividad' in s else 'Structural integrity' if 'integridad' in s else None)
 cl=('MALO' if 'malo' in s else 'REGULAR' if 'regular' in s else 'BUENO' if 'bueno' in s else None)
 return ax,cl

def getzones(m,r):
 if m in (2,3):
  out=[]
  for _,z in r.iterrows():
   lab=z.get('Clasif_Final_Homogenea','');out.append((float(z.KM_Inicio),float(z.KM_Fin),str(lab),z))
  return out
 return [(float(z.KM_Inicio),float(z.KM_Fin),str(z.get('Origen_Final',''))+' '+str(z.get('Clasificacion_Final','')),z) for _,z in r.iterrows()]

def run(max_runs=None):
 t0=time.time()
 raw=pd.read_excel('/mnt/data/MonteCarlo_1000corridas_17tramos.xlsx',sheet_name='Base_Ancha')
 runs=sorted(raw.Corrida.unique());runs=runs[:max_runs] if max_runs else runs
 # pooled normalization across all simulations (constant across runs)
 mini=raw[IND].min().to_numpy(float);maxi=raw[IND].max().to_numpy(float);rg=np.where(maxi>mini,maxi-mini,1)
 metrics=[];boundary=[];detail=[];saved=[]
 for runid in runs:
  d=raw.loc[raw.Corrida==runid].sort_values('Tramo').reset_index(drop=True)
  if len(d)!=17 or not np.array_equal(d.Tramo.to_numpy(),np.arange(1,18)):raise ValueError(f'Invalid run {runid}')
  X=d[IND].to_numpy(float);z=(X-mini)/rg;dist=np.linalg.norm(np.diff(z,axis=0),axis=1)/np.sqrt(6)
  frame=d[['Tramo']+IND].rename(columns={'Tramo':'ID_Tramo'}).copy()
  frame.insert(1,'KM_Inicio',np.round(np.arange(17)*.3,10));frame.insert(2,'KM_Fin',np.round(np.arange(1,18)*.3,10))
  ref={(i,ax):any(ns['clasificar_indicador'](p,float(d.loc[i,p]))=='MALO' for p in ps) for i in range(17) for ax,ps in AXES.items()}
  ncrit=sum(ref.values())
  for m in [2,3,4,5]:
   with contextlib.redirect_stdout(io.StringIO()):
    r=ns[f'aplicar_metodologia{m}'](frame) if m in [2,3] else ns[f'analizar_tramo_jerarquico_rigido_met{m}'](frame,ns['umbrales'])
   zones=getzones(m,r)
   ends=set(round(v/.3) for a,b,lab,_ in zones for v in (a,b) if .000001<v<5.1-.000001)
   if not all(1<=k<=16 for k in ends):raise ValueError(f'Invalid boundary in {runid}/{m}: {ends}')
   flags=np.array([k in ends for k in range(1,17)],bool)
   kept=dist[flags];omitted=dist[~flags]
   auc=np.nan if not len(omitted) or not len(kept) else np.mean([(x>y)+.5*(x==y) for x in kept for y in omitted])
   contrast=np.nan if not len(omitted) or not len(kept) else kept.mean()-omitted.mean()
   covered=0;poor=0;ambig=0
   for i in range(17):
    start=i*.3;stop=(i+1)*.3
    covering=[(lab,row) for a,b,lab,row in zones if a<=start+1e-8 and b>=stop-1e-8]
    for stage,ax in enumerate(AXES,1):
     stage_labels=[];final_labels=[]
     for lab,row in covering:
      v=row.get(['Clasif_Nivel1_Seguridad','Clasif_Nivel2_Operatividad','Clasif_Nivel3_Integridad'][stage-1] if m in [2,3] else f'Clasificacion_Etapa_{stage}',np.nan)
      if pd.notna(v) and str(v).upper() in MAP:stage_labels.append(str(v).upper())
      a,c=decode(lab)
      if a==ax and c:final_labels.append(c)
     covered+=bool(stage_labels)
     ambig+=len(set(stage_labels))>1
     if ref[(i,ax)] and 'MALO' in final_labels:poor+=1
   metrics.append(dict(Corrida=int(runid),Metodo=f'M{m}',Fronteras_unicas=len(ends),Reduccion_pct=100*(16-len(ends))/16,Cobertura_pares=covered,Cobertura_pct=100*covered/51,Pares_criticos=ncrit,Criticos_reportados_poor=poor,Reporte_criticos_pct=100*poor/ncrit if ncrit else np.nan,Ambiguedades_etapa=ambig,Contraste_retenidas=kept.mean() if len(kept) else np.nan,Contraste_omitidas=omitted.mean() if len(omitted) else np.nan,Diferencia_contraste=contrast,AUC=auc,Registros_zona_original=len(zones)))
   for j,fl in enumerate(flags):boundary.append((int(runid),f'M{m}',j+1,float(dist[j]),int(fl)))
   # preserve every original zone and overlapping rows
   for idx,(a,b,lab,row) in enumerate(zones):saved.append((int(runid),f'M{m}',idx+1,a,b,lab))
  if runid%100==0:print('processed',runid,'elapsed',round(time.time()-t0,1),flush=True)
 M=pd.DataFrame(metrics);M.to_csv(BASE/'metricas_por_corrida.csv',index=False)
 pd.DataFrame(boundary,columns=['Corrida','Metodo','Posicion','Contraste','Frontera_retenida']).to_csv(BASE/'auditoria_fronteras.csv',index=False)
 pd.DataFrame(saved,columns=['Corrida','Metodo','Registro_original','KM_Inicio','KM_Fin','Etiqueta_original']).to_csv(BASE/'zonas_originales_montecarlo.csv',index=False)
 summary=M.groupby('Metodo').agg(Corridas=('Corrida','size'),Fronteras_media=('Fronteras_unicas','mean'),Fronteras_sd=('Fronteras_unicas','std'),Reduccion_media_pct=('Reduccion_pct','mean'),Reduccion_sd_pct=('Reduccion_pct','std'),Cobertura_media_pct=('Cobertura_pct','mean'),Cobertura_sd_pct=('Cobertura_pct','std'),Reporte_criticos_media_pct=('Reporte_criticos_pct','mean'),Reporte_criticos_sd_pct=('Reporte_criticos_pct','std'),Ambiguedades_media=('Ambiguedades_etapa','mean'),AUC_media=('AUC','mean'),Contraste_diferencia_media=('Diferencia_contraste','mean')).reset_index()
 summary.to_csv(BASE/'resumen_montecarlo.csv',index=False)
 wide=M.pivot(index='Corrida',columns='Metodo')
 pairs=[]
 for a,b in [('M2','M4'),('M3','M5'),('M4','M5'),('M2','M3')]:
  for field in ['Reduccion_pct','Cobertura_pct','Reporte_criticos_pct']:
   delta=(wide[field][b]-wide[field][a]).dropna().to_numpy()
   pairs.append(dict(Comparacion=f'{b}-{a}',Metrica=field,N=len(delta),Diferencia_media=float(delta.mean()),Diferencia_sd=float(delta.std(ddof=1)),IC95_normal_inferior=float(delta.mean()-1.96*delta.std(ddof=1)/np.sqrt(len(delta))),IC95_normal_superior=float(delta.mean()+1.96*delta.std(ddof=1)/np.sqrt(len(delta))),Fraccion_positiva=float(np.mean(delta>0)),Fraccion_cero=float(np.mean(delta==0))))
 pd.DataFrame(pairs).to_csv(BASE/'comparaciones_pareadas_montecarlo.csv',index=False)
 print(summary.to_string(index=False));print(pd.DataFrame(pairs).to_string(index=False));print('TOTAL',time.time()-t0)
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else None)
