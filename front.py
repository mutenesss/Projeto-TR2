import streamlit as st
import pandas as pd
import requests
import json
import random
import time

# Setup adress and port
address = '127.0.0.1'
port = '5000'
urlAPI = f'http://{address}:{port}/api/data'

# Set max and min values for tank level
max_level = 2
min_level = 40

# Create a placeholder for the data
placeholder = st.empty()
while True:
    # Request data from API
    def get_data():
        response = requests.get(urlAPI)
        data = response.json()
        return data

    # Transform data to DataFrame
    df = pd.DataFrame(get_data())
    print(df)

    # Rename columns
    df.rename(columns={0: 'ID', 1: 'medida', 2: 'data', 3:'hora'}, inplace=True)

    # Join columns data and hora into date_time
    df['date_time'] = df[['data', 'hora']].agg(' '.join, axis=1)
    df['date_time'] = pd.to_datetime(df['date_time'], format='%d/%m/%Y %H:%M:%S')

    # Drop columns data and hora
    #df.drop(columns=['data', 'hora'], inplace=True)

    def calc_level(row, limit):
        return (float(row)*100/limit)

    df['level'] = df['medida'].apply(lambda x: calc_level(x, min_level))

    with placeholder.container():
        st.title('Monitoramento de Nível de Tanque de Combustível')
        # Define app layout 

        left_column, middle_column, right_column = st.columns(3,vertical_alignment='bottom', gap='medium')

        # Data visualization
        left_column.subheader('Nível do Tanque: Gráfico de Barras')
        left_column.bar_chart(data=df, x='date_time', y='level', x_label='Data e Hora', y_label='Nivel do Tanque')

        middle_column.subheader('Nível do Tanque: Gráfico de Área')
        middle_column.area_chart(data=df, x='date_time', y='level', x_label='Data e Hora', y_label='Nivel do Tanque')

        right_column.subheader('Tabela de Dados')
        right_column.dataframe(df)

        time.sleep(10)
