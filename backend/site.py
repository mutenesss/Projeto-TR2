from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import pandas as pd
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq

dbc_css = ("/Bootstrap/assets/bootstrap/css/bootstrap.min.css","https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i&amp;display=swap","/Bootstrap/assets/fonts/fontawesome-all.min.css")
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
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
            dcc.Interval(id='interval-component', interval=60000),
        ]
    )
    
def layout_index():
    app.layout= html.Div(id='body', 
        children=[
        html.Div(id='wrapper', children=[navBar], style={'margin-right': '2px','fixed': False, 'height': '100%'}),
        html.Div(id='content_wrapper', children=[
            html.Div(id='content', children=[
                dbc.Container(id='container', fluid=True,children=[
                    html.Div(id='content', children=[data_containter]),
                    dbc.Row(children=[
                        dbc.Col(children=[
                            dbc.Card(children=[
                                dbc.CardHeader(children=[
                                    html.H6('Dados'),
                                ]),
                                dbc.CardBody(children=[
                                    html.H4('Ultima Medição'),
                                    dbc.Card(children=[
                                        dbc.CardBody(children=[
                                            html.P('Data: ' + str(df['data'].iloc[0])),
                                            html.P('Hora: ' + str(df['hora'].iloc[0])),
                                            html.P('Medida: ' + str(df['medida'].iloc[0])),
                                        ]),
                                    ]),
                                ]),                            
                            ]),
                            dbc.Card(children=[
                                dbc.CardHeader(children=[
                                    html.H6('Previsão para Esvaziar o Tanque'),
                                ]),
                                dbc.CardBody(children=[
                                    html.H4('Data: '),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ])
        ]),
        dcc.Interval(id='interval component', interval=60000, n_intervals=0)
    ])
    return app.layout

df = query_to_dataframe()
current_value = df['medida'].iloc[0]

navBar = html.Div(id='sidebar', children=[
    dbc.Nav(vertical=True, pills=True, justified=True, children=[
        dbc.NavLink('Dashboard', href='#', style={'color': 'white'}),
        dbc.NavLink('Tabela de Dados', href='#', style={'color': 'white'}),
        ], style={
            "position": "right",
            "width": "250px",
            "height": "100%",
            "background-color": "#4e73df",
            "padding": "10px",
            "fixed": False,
        })
    ])

data_containter = html.Div(id='data_container', children=[
    html.Div(id='data_header', children=[html.H2(html.B('Leitor do nível de tanque de combustível utilizando LoRa'))], style={'justify-content': 'center', 'align-items': 'center'}),
    dbc.Row(id='content_row',children=[
        dbc.Col(id='graph_col', children=[
            dbc.Card(id='graph_card', children=[
                dbc.CardHeader(id='card_header', children=[html.H6(html.B('Histórico do Tanque'), className='card-title')]),
                dbc.CardBody(id='card_body', children=[
                    dcc.Graph(id='graph', figure={'data': [{'x': df['date_time'], 'y': df['medida'], 'type': 'line', 'name': 'Historico do tanque'}], 'layout': {'title': 'Histórico do tanque'}}),
                ]),
            ]),
        ]),
        dbc.Col(id='tank_col', children=[
            dbc.Card(id='tank_card', children=[
                dbc.CardHeader(id='card_header', children=[html.H6(html.B('Nível do Tanque'), className='card-title')]),
                dbc.CardBody(id='card_body', children=[
                    daq.Tank(id='tank', value=current_value, label='Nível do Tanque', labelPosition='top', 
                         min=0, max=100, showCurrentValue=True, units='Moedas de 1 real', style={'margin-top': '10px', 'margin-left': '10px'}),
                ]),
            ]),
        ]),
    ]),
])


if __name__ == "__main__":
    layout_index()
    app.run_server(debug=True)
    #server.run(host='0.0.0.0', debug=True)