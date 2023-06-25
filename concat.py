import pandas as pd
import re
from sqlalchemy import create_engine
import pymysql
import mysql.connector
from sqlalchemy.orm import close_all_sessions
import numpy as np

####### Conseguir dataframes de Pandas a partir de tablas de la base de datos ####
def datatables_sql(table, database):
    db = create_engine("mysql+mysqlconnector://user:password@ip:port/"+str(database))
    my_data = pd.read_sql("SELECT * FROM "+str(table),db)
    close_all_sessions()
    return(my_data)

df_chemotherapy_cycle=datatables_sql("chemoterapy_cycle", "db")
df_hormonetherapy=datatables_sql("oral_drug", "db")
df_surgery=datatables_sql("surgery", "db")
df_radiotherapy=datatables_sql("radiotherapy", "db")
df_patient=datatables_sql("patient", "db")
df_tumor=datatables_sql("tumor", "db")
df_chemotherapy_schema=datatables_sql("chemoterapy_schema", "db")
df_comorbidity=datatables_sql("comorbidity", "db")

##Los parámetros reales para la conexión a la base de datos, incluyendo el nombre de la base de datos, no se 
## pueden mostrar. 

df_tumor=df_tumor.sort_values(["date"])
df_tumor['idx'] = df_tumor.groupby('ehr').cumcount()+1 #agrupar por ehr y sumar 1 cada vez que aparezca el mismo ehr
df_tumor_idx= df_tumor.pivot_table(index=['ehr'], columns='idx', 
                    values=['ehr', 'n_tumor', 'date', 'side', 'neoadjuvant', 'stage_diagnosis', 'stage_after_neo', 
                            't_prefix', 't_category', 'n_prefix', 'n_category', 'n_subcategory', 'm_category', 't_prefix_after_neoadj', 
                    't_category_after_neoadj', 'n_prefix_after_neoadj', 'n_category_after_neoadj', 'n_subcategory_after_neoadj', 
                    'm_category_after_neoadj', 'grade', 'ductal', 'lobular', 'nos',
                    'in_situ', 'invasive', 'associated_in_situ', 'er_positive',
                    'pr_positive', 'her2_positive', 'ki67', 'type'], aggfunc='first') #poner como columna los indices creados anteriormente
df_tumor_idx = df_tumor_idx.sort_index(axis=1, level=1) #ordenar por indice
df_tumor_idx.columns = [f'{x}_{y}' for x,y in df_tumor_idx.columns]
df_tumor_idx = df_tumor_idx.reset_index()
df_tumor_idx=df_tumor_idx.rename(columns=lambda x: re.sub('date_','tumor_date_',x))

df_tumor_idx


df_surgery= df_surgery.sort_values(["date_year", "date_month", "date_day"])
df_surgery['idx'] = df_surgery.groupby('ehr').cumcount()+1 #agrupar por ehr y sumar 1 cada vez que aparezca el mismo ehr
df_surgery_idx= df_surgery.pivot_table(index=['ehr'], columns='idx', 
                    values=['surgery', 'date_year', "date_month", "date_day"], aggfunc='first') #poner como columna los indices creados anteriormente

df_surgery_idx = df_surgery_idx.sort_index(axis=1, level=1) #ordenar por indice
df_surgery_idx.columns = [f'{x}_{y}' for x,y in df_surgery_idx.columns]
df_surgery_idx = df_surgery_idx.reset_index()

df_surgery_idx=df_surgery_idx.rename(columns=lambda x: re.sub('date_','surgery_date_',x))
df_surgery_idx


df_chemotherapy=pd.merge(df_chemotherapy_cycle, df_chemotherapy_schema, on="id_schema", how="left")
df_chemotherapy=df_chemotherapy.rename(columns={"name":"qt_schema"})
df_chemotherapy



df_chemotherapy_grouped=df_chemotherapy.groupby(['ehr', "qt_schema"]).size().reset_index().rename(columns={0:"n_cycles_schema"})
###Group data by ehr and qt_schema and counts number of rows in each group and then reset the index and renames the column of counts to n_cycles_schema. 
first_dates_chemotherapy=df_chemotherapy.sort_values(['ehr', "qt_schema"]).groupby(['ehr', "qt_schema"], as_index=False).first()
#extract first date value for each group formed in step one, grouping by ehr and qt_schema, and save in first_date_chemotherapy variable
first_dates_chemotherapy=first_dates_chemotherapy["date"]
last_dates_chemotherapy=df_chemotherapy.sort_values(['ehr', "qt_schema"]).groupby(['ehr', "qt_schema"], as_index=False).last()
#do the same, but for the last 
last_dates_chemotherapy=last_dates_chemotherapy["date"]
df_chemotherapy_grouped["first_date_schema"]=first_dates_chemotherapy
df_chemotherapy_grouped["last_date_schema"]=last_dates_chemotherapy
#add to the chemotherapy df
df_chemotherapy_grouped= df_chemotherapy_grouped.sort_values(["first_date_schema", "last_date_schema"])
df_chemotherapy_grouped["idx"]=df_chemotherapy_grouped.groupby("ehr").cumcount()+1
df_chemotherapy_idx= df_chemotherapy_grouped.pivot_table(index=['ehr'], columns='idx', 
                   values=["qt_schema", "n_cycles_schema", "first_date_schema", "last_date_schema" ], aggfunc='first')


df_chemotherapy_idx = df_chemotherapy_idx.sort_index(axis=1, level=1)
df_chemotherapy_idx.columns = [f'{x}_{y}' for x,y in df_chemotherapy_idx.columns]
df_chemotherapy_idx = df_chemotherapy_idx.reset_index()

df_chemotherapy_idx



df_radiotherapy['idx'] = df_radiotherapy.groupby('ehr').cumcount()+1
df_radiotherapy["n_radio"]= df_radiotherapy.groupby(['ehr'])['n_radiotherapy'].transform(max)

df_radiotherapy= df_radiotherapy.sort_values(["date_start", "date_end"])
df_radiotherapy_idx= df_radiotherapy.pivot_table(index=['ehr'], columns='idx', 
                   values=['date_start', 'date_end', "dose_gy"], aggfunc='first')
df_radiotherapy_idx = df_radiotherapy_idx.sort_index(axis=1, level=1)
df_radiotherapy_idx.columns = [f'{x}_{y}' for x,y in df_radiotherapy_idx.columns]
df_radiotherapy_idx = df_radiotherapy_idx.reset_index()

df_radiotherapy_result=pd.merge(df_radiotherapy_idx, df_radiotherapy[['ehr',"n_radio"]], on=['ehr'])

df_radiotherapy_result=df_radiotherapy_result.rename(columns=lambda x: re.sub('date_','radiotherapy_date_',x))
df_radiotherapy_result=df_radiotherapy_result.rename(columns=lambda x: re.sub('dose_','radiotherapy_dose_',x))

df_radiotherapy_result


df_hormonetherapy['idx'] = df_hormonetherapy.groupby('ehr').cumcount()+1
df_hormonetherapy_idx= df_hormonetherapy.pivot_table(index=['ehr'], columns='idx', 
                    values=["drug"], aggfunc='first')
df_hormonetherapy_idx = df_hormonetherapy_idx.sort_index(axis=1, level=1)
df_hormonetherapy_idx.columns = [f'{x}_{y}' for x,y in df_hormonetherapy_idx.columns]
df_hormonetherapy_idx = df_hormonetherapy_idx.reset_index()
df_hormonetherapy_idx


df_comorbidity["negated"] = df_comorbidity["negated"].replace(["no ", " no"], "0")
df_comorbidity["negated"] = df_comorbidity["negated"].replace(["si ", " si", 'si  '], "1")
df_comorbidity_unstacked=df_comorbidity.astype(str).groupby(['ehr', 'comorbidity'])['negated'].agg(';'.join).unstack()
df_comorbidity_unstacked_2 = df_comorbidity_unstacked.replace({'0': 'no', '1': 'yes'}, regex=True)
df_comorbidity_unstacked_2
df_comorbidity_final = df_comorbidity_unstacked_2.reset_index()
df_comorbidity_final["ehr"]=df_comorbidity_final["ehr"].astype(int)


df_merge= pd.merge(df_patient,df_surgery_idx, on='ehr',how='left')
df_merge_1 =pd.merge(df_merge,df_radiotherapy_result, on='ehr',how='left')
df_merge_2 =pd.merge(df_merge_1, df_chemotherapy_idx, on='ehr',how='left')
df_merge_3 =pd.merge(df_merge_2, df_tumor_idx, on='ehr',how='left')
df_merge_4 =pd.merge(df_merge_3, df_comorbidity_final, on='ehr',how='left')
df_merge_5 =pd.merge(df_merge_4, df_hormonetherapy_idx, on='ehr',how='left')
df_merge_5.to_csv("df_descriptivo_final.csv", sep=';')
