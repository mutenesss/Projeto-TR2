from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuracao do banco de dados utilizado
DB_NAME = 'tr2.db'

# Rota da landing page
@app.route("/")
def homepage():
    return "HomePage!"

# Rota para receber dados do Arduino via POST
@app.route('/api/data', methods=['POST'])
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
@app.route('/api/data', methods=['GET'])
def get_all_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM ultrasonic ORDER BY id DESC')
    data = c.fetchall()
    conn.close()

    return jsonify(data)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)