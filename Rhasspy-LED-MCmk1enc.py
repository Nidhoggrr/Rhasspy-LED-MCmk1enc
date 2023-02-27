#!/usr/bin/env python
from time import sleep
import paho.mqtt.client as mqtt
import json
import os
import serial
import io
import time

rhasspyConfig = '/home/pi/.config/rhasspy/profiles/de/profile.json'

counter = 0
LED = "on"
mute = "off"
siteId = ""
MQTThost = ""

with open(rhasspyConfig,'r', encoding='UTF-8') as file:
    obj = json.loads(file.read())
    MQTTconfig = json.dumps(obj["mqtt"])
    MQTTconfig = MQTTconfig.replace("\"mqtt\": ","")
    MQTTconfig = json.loads(MQTTconfig)
    siteId = MQTTconfig["site_id"]
    MQTThost = MQTTconfig["host"]
    MQTThost = MQTThost.strip('"')
    if "port" in json.dumps(MQTTconfig):
      MQTTport = MQTTconfig["port"]
      MQTTport = MQTTport.strip('"')
      MQTTport = int(MQTTport)
    else:
      MQTTport = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("hermes/dialogueManager/sessionEnded/#")
    client.subscribe("hermes/hotword/toggleOff/#")

def on_message(client, userdata, msg):
    jsonData = json.loads(msg.payload)
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.5)
    if msg.topic == "hermes/hotword/toggleOff" and "dialogueSession" in str(msg.payload) and jsonData["siteId"] == siteId and LED == "on":
        ser.write('eyes.on\n'.encode())
        time.sleep(0.1)
        ser.write('mouth.listen\n'.encode())
        time.sleep(0.1)
    elif msg.topic == "hermes/dialogueManager/sessionEnded" and jsonData["siteId"] == siteId:
        ser.write('eyes.look=d\n'.encode())
        time.sleep(0.1)
        ser.write('mouth.viseme=1\n'.encode())
        time.sleep(0.1)
    elif jsonData["siteId"] == siteId and jsonData["reason"] == "playAudio" and LED == "on":
        ser.write('mouth.think\n'.encode())
        time.sleep(0.1)
        ser.write('eyes.blink=l\n'.encode())
        time.sleep(0.5)
        ser.write('eyes.blink=r\n'.encode())
        time.sleep(0.5)
        ser.write('eyes.blink=b\n'.encode())
        time.sleep(0.1)
    ser.close

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTThost, MQTTport, 60)
client.loop_forever()
