import cv2
import threading


from statistics import mode
import subprocess
import requests
import json
import socket


import fcntl
import struct
import os
import time

from controller import controller
from database import database
from linha import linha
from workplace import workplace
from faceDetector import faceDetector
from screenController import screenController
from colaborador import colaborador

import paho.mqtt.client as mqtt
import socket

mac = socket.gethostname()
cap = cv2.VideoCapture(0)   
main1 = controller(mac,cap,screenController(),faceDetector(),linha(),workplace())

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mac
    print(mac)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mac+"/#")
    client.subscribe("broadcast/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        global main1
        messagem = str(msg.payload.decode("utf-8"))
        mensagem = json.loads(messagem)
        command = mensagem["command"]
        print(msg.topic)
        print(mensagem)
        if command == "reset":
            print("RESETANDO")
            main1.restart()
        elif command == "login":
            print("Logando")
            main1.logar = True
        elif command == "logout":
            if mensagem['matricula'] == "all":
                main1.workplace.removerLogados()
            else:
                main1.workplace.removerLogado(mensagem['matricula'])

        elif command == "cadastrar":
                main1.saveNextFace = True

        elif command == "reboot":
            print("try to reboot")
            print(os.system("reboot"))
    except Exception as e:
        time.sleep(0.5)
        print(e)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256', ifname[:15])
    )[20:24])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("brmtz-dev-001", 1883, 60)
client.loop_start()

showThread = threading.Thread(target=main1.show, args=()).start()

