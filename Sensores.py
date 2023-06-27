import time
import board
import adafruit_dht
import psutil
from Adafruit_BMP import BMP085
from firebase import firebase

firebase = firebase.FirebaseApplication("https://iot-proyecto-14113-default-rtdb.firebaseio.com/",None)

for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()

sensor = adafruit_dht.DHT11(board.D23)
bmp = BMP085.BMP085()


while True:
    try:
        temp = sensor.temperature
        humidity = sensor.humidity
        pressure = bmp.read_pressure()
        datos = {
            'temperatura':temp,
            'humedad':humidity,
            'presion':pressure,
        }
        print("Temperatura: {}*C   Humidity: {}%   Pressure: {}  Pa".format(temp, humidity, pressure))
        resultados = firebase.post('/datos_sensores',datos)

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error

    time.sleep(4.0)