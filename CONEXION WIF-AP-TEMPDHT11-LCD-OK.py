from umqtt.simple import MQTTClient
import network
from machine import Pin, I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import time
from dht import DHT11

# Configuración de la conexión WiFi
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
ap_if.config(essid="ESP-AccessPoint-dan", authmode=3, password="12345678", max_clients=2, hidden=False)

print("ESSID:", ap_if.config('essid'))
print("Configuración de red (IP/netmask/gw/DNS):", ap_if.ifconfig())
print("Modo de autenticación:", ap_if.config("authmode"))
print("Nº máximo de clientes:", ap_if.config("max_clients"))
print("Oculta (True=Si / False=No):", ap_if.config("hidden"))
print("Activa (True=Si / False=No)", ap_if.active())

# Configuración de la conexión estación (STA)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("ZONA CREATIVA", "0150262194zc")

# Esperar hasta que se establezca la conexión STA
while not sta_if.isconnected():
    pass

print("Conectado a la red WiFi como estación")
print("Configuración de red STA (IP/netmask/gw/DNS):", sta_if.ifconfig())

# Configuración del LCD I2C
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)  # Ajusta la dirección del LCD según tu configuración

# Configuración de Thinger.io
user = 'dgarmijos'
device = 'Esp32New'
password_thinger = '1T&f#FK7$6LtlbSH'

# Función de callback al recibir mensajes
def callback(topic, msg):
    print('Mensaje recibido en el tema {}: {}'.format(topic, msg))

# Inicialización del cliente MQTT con usuario y contraseña

def readDht():
    dht11 = DHT11(Pin(15))
    dht11.measure()
    return dht11.temperature(), dht11.humidity()

def colectData():
    temp, hum = readDht()
    return temp, hum

while True:
    client = MQTTClient(client_id=device, server='backend.thinger.io', user=user, password=password_thinger, ssl=True)
    client.set_callback(callback)

    temp, hum = colectData()

    # Imprimir en el LCD
    lcd.putstr("Temp: {}C\nHumi: {}%".format(temp, hum))

    # Imprimir en la consola
    print("Temperatura:", temp, "°C - Humedad:", hum, "%")

    payload = "field1="+str(temp)+"&field2="+str(hum)

    client.connect()

    # Publicación del valor en Thinger.io
    topic = 'v2/users/{}/devices/{}/Data/Esp32New'.format(user, device)
    message = '{{"field1":{}, "field2":{}}}'.format(temp, hum)
    client.publish(topic, message)

    # Espera para permitir que el mensaje se envíe antes de desconectar
    time.sleep(4)

    # Desconexión del cliente MQTT
    client.disconnect()

    # Limpia el LCD para la siguiente iteración
    lcd.clear()
    time.sleep(1)
