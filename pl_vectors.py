import pandas as pd 
import os


import re
from functools import reduce

fecha = '20191018'
ruta = 'C:/Users/e054040/Downloads/pl_vectors_'+fecha+'_2/'
os.chdir(ruta)
nombre_cal = [x for x in os.listdir() if '.cal' in x][0]

y, m, d = fecha[:4], fecha[4:6], fecha[6:]

stress = 'TEPR_RPM_Out_HS1d1_Stress2[0-9]{3}_SIM_'+m+d+'.csv'
r = re.compile(stress)
stress_files = list(filter(r.search, os.listdir()))
stress = [pd.read_csv(x, skiprows =3).drop_duplicates() for x in stress_files]

def get_days_vector(ruta, nombre_cal):
    cal = pd.read_csv(ruta + nombre_cal, skiprows=1,encoding='iso-8859-1')
    cal = cal.iloc[:,0].to_frame('days')
    cal.days = (cal.days.str.extract('(.*?) #',expand=False))
    cal = pd.to_datetime(cal.days)
    fechas =  [x for x in  pd.date_range('2008-01-01', '2019-12-31') if x.weekday() not in [5,6]]
    fechas = pd.Series(fechas)[~pd.Series(fechas).isin(cal)].astype(str).reset_index(drop=True)
    return fechas

fechas = get_days_vector(ruta, nombre_cal)
fechas = fechas.loc[fechas<=y+'-'+m+'-'+d][::-1]

x = pd.read_csv('TEPR_RPM_Out_HS_1d1_SIM_'+m+d+'.csv', skiprows=3, index_col=0)
x.index = x.index.str.replace('-=-PORT', '')
x.columns = fechas[:500]
x = x.reset_index().melt(id_vars = 'index', var_name='fecha', value_name = 'pl')
x.columns = ['portfolio' if x=='index' else x for x in x.columns]

years_stress = [x.columns[1:].str.extract('([0-9]{4})').squeeze()[0] for x in stress]

fechas_col =  [fechas[fechas.str.contains(x)] for x in years_stress]
fechas_col = [pd.Series(['portfolio']).append(x) for x in fechas_col]
fechas_col_dic = [{x:y for x,y in zip(k.columns, v)} for k,v in zip(stress, fechas_col)]
df_stress_list = [x.rename(y, axis=1) for x,y in zip(stress,fechas_col_dic)]
stress_df = reduce(lambda x,y: x.merge(y,on='portfolio'), df_stress_list)
stress_df.portfolio = stress_df.portfolio.str.replace('-=-PORT','')
stress_df = stress_df.melt(id_vars = 'portfolio', var_name='fecha', value_name='pl')

pl = stress_df.append(x)
pl = pl.sort_values(['fecha', 'portfolio']).reset_index(drop=True)
pl.to_csv('PnL_' + fecha + '.csv')

