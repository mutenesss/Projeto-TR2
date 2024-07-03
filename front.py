import streamlit as st
import pandas as pd
import requests
import json
import time
import datetime as dt

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
    if not df.empty:

        # Rename columns
        df.rename(columns={0: 'ID', 1: 'medida', 2: 'data', 3:'hora'}, inplace=True)

        # Join columns data and hora into date_time
        df['date_time'] = df[['data', 'hora']].agg(' '.join, axis=1)
        df['date_time'] = pd.to_datetime(df['date_time'], format='%d/%m/%Y %H:%M:%S')

        # Drop columns data and hora
        #df.drop(columns=['data', 'hora'], inplace=True)

        def calc_level(row, limit):
            return (float(row)*100/limit)

        df['level'] = df['medida'].apply(lambda x: 100-(calc_level(x, min_level)))

        last_readings = df.head(6)
        # Get last 6 tank levels
            
            # Ensure 'date_time' column is in datetime format
        last_readings['date_time'] = pd.to_datetime(last_readings['date_time'])

            # Calculate the differences between consecutive readings
        last_readings['time_diff'] = last_readings['date_time'].diff().dt.total_seconds()
        last_readings['level_diff'] = last_readings['level'].diff()

            # Drop rows with NaN values resulting from the diff() operation
        last_readings = last_readings.dropna()

            # Calculate the rate of change
        last_readings['rate_of_change'] = last_readings['level_diff'] / last_readings['time_diff']
            
            # Calculate the average rate of change
        average_rate_of_change = last_readings['rate_of_change'].mean()

            # Check if the tank is emptying
        if average_rate_of_change >= 0:
            estimated_empty_time = None# Tank is not emptying
        else:
                # Get the most recent reading
            current_level = last_readings.iloc[-1]['level']
            current_date_time = last_readings.iloc[-1]['date_time']

                # Calculate the time to empty
            time_to_empty_seconds = current_level / abs(average_rate_of_change)
            estimated_empty_time = current_date_time + pd.to_timedelta(time_to_empty_seconds, unit='s')


        with placeholder.container():
            st.title('Monitoramento de Nível de Tanque de Combustível')
            # Define app layout 

            left_column, right_column = st.columns(2,vertical_alignment='bottom', gap='large')

            # Data visualization
            left_column.subheader('Nível do Tanque: Gráfico de Barras')
            left_column.bar_chart(data=df, x='date_time', y='level', x_label='Data e Hora', y_label='Nivel do Tanque')
            left_column.subheader('Nível do Tanque: Recorte dos Últimos 50 Registros')
            left_column.bar_chart(data=df.tail(50), x='date_time', y='level', x_label='Data e Hora', y_label='Nivel do Tanque')
            
            right_column.subheader('Nível do Tanque: Gráfico de Área')
            right_column.area_chart(data=df, x='date_time', y='level', x_label='Data e Hora', y_label='Nivel do Tanque')

            table_row = right_column.container()

            table_row.subheader('Tabela de Dados')
            table_row.dataframe(df)
            if estimated_empty_time != None:
                st.header(f'Previsão para esvaziar:\n') 
                st.subheader(estimated_empty_time.strftime('%H:%M:%S'))
            else:
                st.header(f'Tanque enchendo ou nível constante no momento.\n Sem previsão para esvaziar')
            st.header(f'Data e Hora Atuais: \n')
            st.subheader(f'{dt.datetime.today().strftime('%d/%m/%Y')}, {dt.datetime.now().strftime('%H:%M:%S')}')
            time.sleep(10)