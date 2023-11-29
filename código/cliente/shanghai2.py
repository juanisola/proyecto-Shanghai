LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()
#Native libs
import machine
import network
import time
from machine import Pin, PWM



#Third Party
from umqtt.simple import MQTTClient

# Internal libs
import constants
import json
received_data = {}
data_sensor = None
    
def connectMQTT():
    '''Connects to Broker'''
    # Client ID can be anything
    client = MQTTClient(
        client_id="other client",
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

    else:
      print('connected')
      print(wlan.status())
      status = wlan.ifconfig()

def make_connections():
    # Connect to internet and set MPU to start taking readings
    connect_to_internet(constants.INTERNET_NAME, constants.INTERNET_PASSWORD)
    return connectMQTT()


def my_callback(topic, response):  # Usar 'response' en lugar de 'msg'
    global received_data

    received_data = response  # Almacena los datos recibidos en la variable global
    
    try:
        response_str = response.decode('utf-8')

        data = json.loads(response_str)
        
        # Acceder a los valores individuales del diccionario como variables independientes
        gx = float(data.get('gx'))
        gy = float(data.get('gy'))
        if 10 > gy > 4:
            vel=60
        elif 15 > gy > 9:
            vel=70
        elif 20 > gy > 14:
            vel=80
        elif 25 > gy > 19:
            vel=90
        elif gy > 24:
            vel=100
        else:
            vel=0
            
        if -4 > gy > -10:
            vel2=60
        elif -9 > gy > -15:
            vel2=70
        elif -14 > gy > -20:
            vel2=80
        elif -19 > gy > -25:
            vel2=90
        elif gy < -24:
            vel2=100
        else:
            vel2=0
        
        zx= Pin(26, Pin.OUT)
        yx = Pin(27, Pin.OUT)
        if gx > 100:
            zx.value(1)
            yx.value(0)
            time.sleep(5)
            zx.value(0) 
            yx.value(0)
        elif gx < -100:
            zx.value(0)
            yx.value(1)
            time.sleep(5)
            zx.value(0)
            yx.value(0)
        print(vel,vel2)
        pwm0 = PWM(Pin(16))
        pwm0.freq(500)
        pwm0.duty_u16(vel*655)
        pwm1 = PWM(Pin(17))
        pwm1.freq(500)
        pwm1.duty_u16(vel2*655)
        

# Hacer uso de las variables individuales
        #print(f"Valor de gx: {gx}")
       # print(f"Valor de gy: {gy}")
    
    except ValueError as e:
        print("Error al decodificar JSON:", e)
    except Exception as ex:
        print("Error:", ex)
        

def subscribe(topic, client):
    '''Recieves data from the broker'''
    client.subscribe(topic)
    print("Subscribe Done")

client = make_connections()
client.set_callback(my_callback)
subscribe('Topic', client)

while True:
    time.sleep(0.2)
    client.check_msg()
print(gx)


