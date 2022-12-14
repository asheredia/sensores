#!/usr/bin/env python

# This script works as a Environmental Station, so it will compute (random) values
# through its virtual sensor and it will publish the message composed by the values
# calculated before on the MQTT channel, as long as the station works correctly.

# importing libraries
import paho.mqtt.client as mqtt
import Adafruit_DHT
import RPi.GPIO as GPIO
import os
import socket
import ssl
from time import sleep
from random import randint
import json
import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN)
 
connflag = False
 
def on_connect(client, userdata, flags, rc):                        # function for making connection between
    global connflag                                                 # the MQTT client and the broker
    print("Connected to AWS")
    connflag = True
    print("Connection returned result: " + str(rc) )
 
def on_message(client, userdata, msg):                              # function for ending messages
    print(msg.topic+" "+str(msg.payload))
 
#def on_log(client, userdata, level, buf):
#    print(msg.topic+" "+str(msg.payload))
 
mqttc = mqtt.Client()                                               # MQTT client object
mqttc.on_connect = on_connect                                       # assign on_connect function
mqttc.on_message = on_message                                       # assign on_message function
#mqttc.on_log = on_log

#### Change following parameters #### 
awshost = "a3d6q5aedgtyoc-ats.iot.us-east-2.amazonaws.com"          # endpoint
awsport = 8883                                                      # port no.   
clientId = "sensor"                                                 # client id
thingName = "wheather-smartThing"                                   # thing name
caPath = "../certs/AmazonRootCA1.pem"                               # rootCA certificate
certPath = "../certs/certificate.pem.crt"                           # client certificate
keyPath = "../certs/private.pem.key"                                # private key
 
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED,
              tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)       # pass parameters
 
mqttc.connect(awshost, awsport, keepalive=60)                       # connect to AWS server
 
mqttc.loop_start()                                                  # start the loop for sending
                                                                    # messages continuously
while(1):
    sensor = Adafruit_DHT.DHT11
    pin = 4
    sleep(5)                                                        # waiting between messages
    if connflag == True:
        #temp = str(randint(-50,50))                                 # computation of all the (random) values
        #hum = str(randint(0, 100))                                  # of the sensors, for this
        hum, temp = Adafruit_DHT.read_retry(sensor, pin)
        #wind_dir = str(randint(0, 360))                             # specific station (with id 1)
        #wind_int = str(randint(0, 100))
        rain = (GPIO.input(18) / 255) * 100
        rain = (rain - 100) * -1
        #,str(randint(0, 50))
        time = str(datetime.datetime.now())[:19]                    # computation of the current date and time
        
        data ={"id":"1", "datetime":time, "temperature":temp, "humidity":hum}
        jsonData = json.dumps(data)
        mqttc.publish("sensor/data", jsonData, 1)                   # publish this message on the
                                                                    # MQTT channel with QoS 1
                                                                    
        print("Message sent: time ",time)                           # a simple check which confirms that
        print("Message sent: temperature ",temp," Celsius")         # the message was sent correctly
        print("Message sent: humidity ",hum," %")
        #print("Message sent: windDirection ",wind_dir," Degrees")
        #print("Message sent: windIntensity ",wind_int," m/s")
        print("Message sent: rainHeight ",rain," %\n")
    else:
        print("waiting for connection...")
