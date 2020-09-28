#!/usr/bin/env python
# coding: utf-8

# In[1]:


from matplotlib import pyplot as plt
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os


# In[2]:


yf.pdr_override()


# In[3]:


start_date = '{}-01-01'.format(date.today().year - 1)
end_date = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")


# In[4]:


now = datetime.now()
monday = (now - timedelta(days = now.weekday())).strftime("%Y-%m-%d")


# In[5]:


def first_business_day(date):
#     if date.day > 25:
#         date += timedelta(7)
    month = date.replace(day=1)
    if month.weekday() > 4:
        month = date.replace(day=(8 - month.weekday()))
    return month.strftime("%Y-%m-%d")


# In[6]:


month = first_business_day(date.today())
three_month = first_business_day((date.today() + relativedelta(months=-3)))
six_month = first_business_day((date.today() + relativedelta(months=-6)))


# In[7]:


def get_kpi_value(ticket, kpi):
    file = './crawlers/{}.json'.format(ticket)
    if os.path.exists(file):
        try:
            kpis = pd.read_json(file)
            return float(kpis[kpis['title'] == kpi]['value'].values[0].replace('.', '').replace(',', '.'))
        except:
            return 0
    return 0


# In[8]:


def sector_kpi(tickets, kpi):
    kpis = []
    for ticket in tickets:
        ticket = ticket.replace('.SA', '')
        kpis.append(get_kpi_value(ticket, kpi))
    kpis_len = len([i for i in kpis if i > 0])
    if kpis_len > 0:
        return sum(kpis) / kpis_len
    return 0


# In[17]:


def generate_json(empresas, indicador, arquivo):
    setores = {}
    for i in empresas[['Setor', 'Código Yahoo']].iterrows():
        setor = i[1]['Setor']
        codigo = i[1]['Código Yahoo']
        if setor not in setores:
            setores[setor] = []
        lista = setores[setor]
        lista.append(codigo)
        setores[setor] = lista
        
    val_indicador = pdr.get_data_yahoo(indicator, start=start_date, end=end_date)
    data = pdr.get_data_yahoo(list(empresas['Código Yahoo']), start=start_date, end=end_date)
    
    df_categories = pd.DataFrame()
    df_mean = pd.DataFrame()
    df_indicators = pd.DataFrame()
    
    for setor in setores.keys():
        df_categories[setor] = data['Close'][setores[setor]].mean(axis=1)
    df_categories[indicador] = val_indicador['Close']
    df_categories.fillna(method='ffill', inplace=True)
    
    setores[indicador] = [indicador]
    
    for setor in setores.keys():
        valor_ano = round(df_categories.iloc[0][setor], 2)
        valor_seis_meses = round(df_categories.iloc[df_categories.index.get_loc(six_month,method='nearest')][setor], 2)
        valor_tres_meses = round(df_categories.iloc[df_categories.index.get_loc(three_month,method='nearest')][setor], 2)
        valor_mes = round(df_categories.loc[month][setor], 2)
        valor_semana = round(df_categories.loc[monday][setor], 2)
        valor_ontem = round(df_categories.iloc[-2][setor], 2)
        valor_hoje = round(df_categories.iloc[-1][setor], 2)

        percent_ano = round((((valor_hoje - valor_ano) / valor_ano) * 100), 2)
        percent_seis_meses = round((((valor_hoje - valor_seis_meses) / valor_seis_meses) * 100), 2)
        percent_tres_meses = round((((valor_hoje - valor_tres_meses) / valor_tres_meses) * 100), 2)
        percent_mes = round((((valor_hoje - valor_mes) / valor_mes) * 100), 2)
        percent_semana = round((((valor_hoje - valor_semana) / valor_semana) * 100), 2)
        percent_hoje = round((((valor_hoje - valor_ontem) / valor_ontem) * 100), 2)
        
        pvp = round(sector_kpi(setores[setor], 'P/VP'), 2)
        
        line = pd.Series({
            'inicio_ano': valor_ano,
            'inicio_seis_meses': valor_seis_meses,
            'inicio_tres_meses': valor_tres_meses,
            'inicio_mes': valor_mes,
            'inicio_semana': valor_semana,
            'hoje': valor_hoje,
            'percent_ano': percent_ano,
            'percent_seis_meses': percent_seis_meses,
            'percent_tres_meses': percent_tres_meses,
            'percent_mes': percent_mes,
            'percent_semana': percent_semana,
            'percent_hoje': percent_hoje,
            'P/VP': pvp
        }, name=setor)
        df_mean = df_mean.append(line)
        
    df_mean.T.to_json('dashboard/src/' + arquivo)


# In[10]:


# https://blog.toroinvestimentos.com.br/empresas-listadas-b3-bovespa
empresas_ibov = pd.read_csv('empresas.csv', sep=';')
empresas_ibov['Código Yahoo'] = empresas_ibov['Código'].apply(lambda x: x + '.SA')
indicator = '^BVSP'
file = 'ibov.json'
generate_json(empresas_ibov, indicator, file)


# In[11]:


empresas_ibov = pd.read_csv('empresas_b3.csv', sep=';', encoding = "ISO-8859-1")
indicator = '^BVSP'
file = 'b3.json'
#empresas_ibov = empresas_ibov[empresas_ibov['Código Yahoo'].str.contains("\.SA")]
generate_json(empresas_ibov, indicator, file)


# In[18]:


empresas_ibov = pd.read_json('ifix.json')
empresas_ibov['Código Yahoo'] = empresas_ibov['Código'].apply(lambda x: x + '.SA')
indicator = 'IFIX.SA'
file = 'ifix.json'
generate_json(empresas_ibov, indicator, file)
