import ast,json,os,contextlib,io
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mpatches
try:
 import pywt
except ImportError:
 import types
 def wavedec(x, wavelet, level=1):
  if wavelet != 'haar' or level != 1: raise ValueError('Fallback only supports Haar level 1')
  x=np.asarray(x,dtype=float)
  if len(x)%2:x=np.r_[x,x[-1]]
  a=(x[0::2]+x[1::2])/np.sqrt(2)
  d=(x[0::2]-x[1::2])/np.sqrt(2)
  return [a,d]
 pywt=types.SimpleNamespace(Wavelet=lambda _:types.SimpleNamespace(dec_len=2),dwt_max_level=lambda data_len,filter_len:int(np.floor(np.log2(data_len))),wavedec=wavedec)

root=os.path.dirname(os.path.abspath(__file__));nb=json.load(open(root+'/Experimento Inglés.ipynb'))
def src(i):return ''.join(nb['cells'][i]['source'])
def funcs(i):
 tree=ast.parse(src(i));return compile(ast.Module(body=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))],type_ignores=[]),f'cell{i}','exec')
ns={'np':np,'pd':pd,'plt':plt,'mpatches':mpatches,'pywt':pywt}
exec(src(1),ns)
exec(funcs(3),ns)
# exact AHP weight matrices from original
exec('''criterios_matrix=np.array([[1,3,6],[1/3,1,2],[1/6,1/2,1]])
seguridad_matrix=np.array([[1,1],[1,1]])
operatividad_matrix=np.array([[1,5],[1/5,1]])
integridad_matrix=np.array([[1,1],[1,1]])
alternativas_matrix=np.array([[1,2,6],[1/2,1,3],[1/6,1/3,1]])
w0=ahp_weights(criterios_matrix)[0]
w1=ahp_weights(seguridad_matrix)[0]
w2=ahp_weights(operatividad_matrix)[0]
w3=ahp_weights(integridad_matrix)[0]
pesos_alt_vec=ahp_weights(alternativas_matrix)[0]
pesos_globales={'CF':w0[0]*w1[0],'TX':w0[0]*w1[1],'IRI':w0[1]*w2[0],'JF':w0[1]*w2[1],'LTE':w0[2]*w3[0],'DEF':w0[2]*w3[1]}
''',ns)
exec(funcs(8),ns)
exec(funcs(13),ns)
exec(src(27),ns)
exec(funcs(28),ns)
exec(funcs(46),ns)
exec(funcs(64),ns)
exec(funcs(86),ns)
print('functions ready')
for sheet in ['Representativa','Variabilidad']:
 d=pd.read_excel(root+'/Experimento.xlsx',sheet_name=sheet)
 print(sheet,len(d),d.columns.tolist(),d[['KM_Inicio','KM_Fin']].head(2).to_dict('records'))
 d['KM_Inicio']=d['KM_Inicio'].map(ns['km_estacado_a_km']);d['KM_Fin']=d['KM_Fin'].map(ns['km_estacado_a_km'])
 for col in ['IRI','JF','LTE','DEF','CF','TX']:d[col]=pd.to_numeric(d[col],errors='coerce')
 print('length',d.KM_Fin.max()-d.KM_Inicio.min())
 for name,fun in [('M2',lambda:ns['aplicar_metodologia2'](d)),('M3',lambda:ns['aplicar_metodologia3'](d)),('M4',lambda:ns['analizar_tramo_jerarquico_rigido_met4'](d,ns['umbrales'])),('M5',lambda:ns['analizar_tramo_jerarquico_rigido_met5'](d,ns['umbrales']))]:
  try:
   with contextlib.redirect_stdout(io.StringIO()):r=fun()
   print(name,len(r),r[['KM_Inicio','KM_Fin']].head(2).to_dict('records'),r.columns.tolist()[-8:])
  except Exception as e:print(name,'ERROR',type(e).__name__,str(e)[:240])
print('\nINTERVALS')
d=pd.read_excel(root+'/Experimento.xlsx',sheet_name='Representativa');d['KM_Inicio']=d['KM_Inicio'].map(ns['km_estacado_a_km']);d['KM_Fin']=d['KM_Fin'].map(ns['km_estacado_a_km'])
for m in [4,5]:
 with contextlib.redirect_stdout(io.StringIO()):r=ns[f'analizar_tramo_jerarquico_rigido_met{m}'](d,ns['umbrales'])
 print('M',m);print(r[['KM_Inicio','KM_Fin','Origen_Final','Clasificacion_Final']].to_string(index=False))
