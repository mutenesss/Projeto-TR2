import requests
import time
import random

address = '127.0.0.1'
port = '5000'
urlAPI = f'http://{address}:{port}/api/data'

# Set max and min values for tank level
max_level = 2
min_level = 40

for i in range(50):
    value = random.randint(max_level, min_level)
    data_send = requests.post(urlAPI, json={'value': value})
    sleep_time = random.randint(3, 10)
    time.sleep(sleep_time)

