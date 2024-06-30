import streamlit as st
import pandas as pd
import requests
import json

# Setup adress and port
address = '127.0.0.1'
port = '5000'
urlAPI = f'http://{address}:{port}/api/data'

# Set max and min values for tank level
max_level = 400
min_level = 2

# Request data from API
response = requests.get(urlAPI)
data = response.json()

# Transform data to DataFrame
df = pd.DataFrame(data)

# Rename columns
df.rename(columns={0: 'ID', 1: 'medida', 2: 'data', 3:'hora'}, inplace=True)

# Join columns data and hora into date_time
#df['date_time'] = df[['data', 'hora']].agg(' '.join, axis=1)
#df['date_time'] = pd.to_datetime(df['date_time'], format='%d/%m/%Y %H:%M:%S')

# Drop columns data and hora
#df.drop(columns=['data', 'hora'], inplace=True)

# Insert limit values into DataFrame
def calc_level(row, limit):
    return (float(row)*100/limit)

df['level'] = df['medida'].apply(lambda x: calc_level(x, max_level))

# Define app layout 

st.title('Monitoramento de Nível de Tanque de Combustível')

left_column, right_column = st.columns(2)

# Data visualization
left_column.subheader('Visualização de Dados')
left_column.line_chart(data=df,x='medida', y='ID', x_label='Medidas Lidas', y_label='ID da leitura')

right_column.subheader('Tabela de Dados')
right_column.dataframe(df)
right_column.line_chart(data=df, x='hora', y='level', x_label='Hora', y_label='Nivel do Tanque')
