import time
import paho.mqtt.client as mqtt
from firebase import firebase
import json

firebase = firebase.FirebaseApplication("https://iot-proyecto-14113-default-rtdb.firebaseio.com/",None)

broker = "192.168.7.163"
topic = "esp32/input"
username = "esteban"
password = "esteban"

last_message = ""

def on_connect(client, userdata, flags, rc):
    print("Conectado con codigo de resultado: " + str(rc))
    client.subscribe(topic)
import json

last_messages = []
ponderaciones = [0.6,0.4]  # Ajusta las ponderaciones según tus necesidades
rociador_activo = False

def calcular_suma_ponderada():
    if len(last_messages) >= len(ponderaciones):
        suma_ponderada = sum(ponderaciones[i] * last_messages[i] for i in range(len(ponderaciones)))
        return suma_ponderada
    return None

def calcular_media_ponderada():
    suma_ponderada = calcular_suma_ponderada()
    if suma_ponderada is not None:
        media_ponderada = suma_ponderada / sum(ponderaciones)
        media_ponderada = round(media_ponderada)
        return media_ponderada
    return None

def on_message(client, userdata, msg):
    global last_messages
    
    last_water = json.loads(msg.payload.decode("utf-8"))["agua"]

    last_air = json.loads(msg.payload.decode("utf-8"))["calidad_aire"]

    last_humidity = json.loads(msg.payload.decode("utf-8"))["humedad"]

    last_humidity2 = json.loads(msg.payload.decode("utf-8"))["humedad2"]
    
    last_temp = json.loads(msg.payload.decode("utf-8"))["temperatura"]

    last_presure = json.loads(msg.payload.decode("utf-8"))["presion"]

    last_temp = round(last_temp)

    last_humidity = round(last_humidity)

    last_humidity2 = round(last_humidity2)

    print("Temp: {}*C   Humidity: {}%  Humidity2: {}%  Pressure: {}  Pa  Air: {} ppm  Bomba: {}".format(last_temp, last_humidity, last_humidity2, last_presure, last_air, last_water))
    
    last_messages.append(last_humidity)
    if len(last_messages) > len(ponderaciones):
        last_messages.pop(0)
    
    media_ponderada = calcular_media_ponderada()
    print(media_ponderada)
    if media_ponderada is not None:
        if media_ponderada > 75:
            rociador_activo = False
            print('Apagando')
        elif media_ponderada < 70:
            rociador_activo = True
            print('Encendiendo')
        else:
            print('Humedad estable')

    datos = {
        "water":last_water,
        "air":last_air,
        "temp":last_temp,   
        "presure":last_presure, 
        "humidity":last_humidity,
        "humidity2":last_humidity2,
        "humidity3": media_ponderada
    }

    humedades = {
        "humidity":last_humidity,
        "humidity2":last_humidity2,
        "humidity3":media_ponderada
    }

    firebase.post('/datos_sensores',datos)
    firebase.post('/datos_humedades',humedades)

client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883)

client.loop_forever()
