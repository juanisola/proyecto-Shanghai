LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

from imu import MPU6050
from time import sleep
from machine import Pin, I2C
import time
import network
import random
import json

#Third Party
from umqtt.robust import MQTTClient

# Internal libsd
import constants

    
def connectMQTT():
    '''Connects to Broker'''
    # Client ID can be anything
    client = MQTTClient(
        client_id=b"mahmood",
        server=constants.SERVER_HOSTNAME,
        port=0,
        user=constants.USER,
        password=constants.PASSWORD,
        keepalive=7200,
        ssl=True,
        ssl_params={'server_hostname': constants.SERVER_HOSTNAME}
    )
    client.connect()
    return client

def sensorxyz():
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    imu = MPU6050(i2c)

    sensor = {}  # Diccionario para almacenar los datos del sensor

    while True:
        ax = round(imu.accel.x, 2)
        ay = round(imu.accel.y, 2)
        az = round(imu.accel.z, 2)
        gx = round(imu.gyro.x) + 5.454188
        gy = (round(imu.gyro.y) + 3.204024) / 10
        gz = round(imu.gyro.z) - 0.5743985
        sleep(0.2)
        
        # Almacenar los datos en el diccionario
        sensor = {
            "gx": (gx),
            "gy": (gy)
            
        }
        sensor_data = json.dumps(sensor)
        
        # Devolver los datos del sensor
        return sensor_data

def connect_to_internet(ssid, password):
    # Pass in string arguments for ssid and password
    
    # Just making our internet connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('waiting for connection...')
      time.sleep(1)
    # Handle connection error
    if wlan.status() != 3:
       print(wlan.status())
       raise RuntimeError('network connection failed')
    else:
      print('connected')
      print(wlan.status())
      status = wlan.ifconfig()

def make_connections():
    # Connect to internet and set MPU to start taking readings
    connect_to_internet(constants.INTERNET_NAME, constants.INTERNET_PASSWORD)
    return connectMQTT()


def publish(topic, value, client):
    '''Sends data to the broker'''
    print(topic)
    print(value)
    client.publish(topic, value)
    print("Publish Done")

    

client = make_connections()


while True:
    sensor_data = sensorxyz()
    publish('Topic', str(sensor_data), client)
    
    time.sleep(0.2)




