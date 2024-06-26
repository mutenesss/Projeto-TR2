from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import pandas as pd
from dash import Dash, dcc, html


app = Dash(__name__)
server = app.server
CORS(server)  


# Configuracao do banco de dados utilizado
DB_NAME = 'tr2.db'

# Rota da landing page
@server.route("/")
def homepage():
    return "HomePage!"

# Rota para receber dados do Arduino via POST
@server.route('/api/data', methods=['POST'])
def receive_data():
    # DateTime
    current_datetime = datetime.now()
    current_date = current_datetime.strftime('%d/%m/%Y')
    current_time = current_datetime.strftime('%H:%M:%S')


    data = request.get_json()
    sensor_value = data.get('value')

    if sensor_value is None:
        return jsonify({'error': 'Value not provided'}), 400

    try:
        # Inserir dados no banco de dados
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO ultrasonic (medida, data, hora) VALUES (?, ?, ?)', (sensor_value, current_date, current_time))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data inserted successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para obter todos os dados do banco de dados
@server.route('/api/data', methods=['GET'])
def get_all_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM ultrasonic ORDER BY id DESC')
    data = c.fetchall()
    conn.close()

    return jsonify(data)

@server.route('/api/data/dataframe', methods=['GET'])
def query_to_dataframe():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM ultrasonic ORDER BY id DESC", conn)
    conn.close()
    df['date_time'] = df[['data', 'hora']].agg(' '.join, axis=1)
    df['date_time'] = pd.to_datetime(df['date_time'], format='%d/%m/%Y %H:%M:%S')

    return df
    
@server.route('/api/data/layout', methods=['GET'])
def define_layout():
    df = query_to_dataframe()
    app_layout = html.Div(
        children=[
            html.H1(children='Projeto TR2'),
            html.P(children=('Apresenta o nível de um tanque de combustível obtido utilizando as medidas de um sensor ultrassonico (HC-SR04)')),
            dcc.Graph(figure={'data': [{'x': df['date_time'], 'y': df['medida'], 'type': 'line', 'name': 'Nível do tanque'}], 'layout': {'title': 'Nível do tanque'}}),
            dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
        ]
    )

    app.layout = app_layout
    return app.run_server(debug=True)


if __name__ == "__main__":
    app.layout = define_layout()
    server.run(host='0.0.0.0', debug=True)