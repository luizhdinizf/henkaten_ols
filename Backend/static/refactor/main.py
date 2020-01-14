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

#mac = socket.gethostname()
mac = "RMTZ3097"
cap = cv2.VideoCapture(0)   
main1 = controller(mac,cap,screenController(),faceDetector(),linha(),workplace(mac))

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
    print("Message ARRIVED")  
    global main1
    mensagem_str = str(msg.payload.decode("utf-8"))
    mensagem = json.loads(mensagem_str)
    command = mensagem["command"]
    print(msg.topic)
    print(mensagem)
    if command == "reset":
        print("RESETANDO")
        main1.restart()
    elif command == "login":
        subprocess.call("./.killChromium.sh")
        print("Logando")
        main1.logar = True
        
    elif command == "logout":
        mat = mensagem["matricula"]
        if mat == "all":
            main1.workplace.removerLogados()
            main1.registraEvento("logoutGeral", " ")
        else:
            colab = main1.linha.findColabByMatricula(mat)
            if colab in main1.workplace.logados:
                main1.registraEvento("logout", colab.name)
                main1.workplace.removerLogado(colab.matricula)

    elif command == "cadastrar":
            subprocess.call("./.killChromium.sh")
            main1.saveNextFace = True

    elif command == "reboot":
        print("try to reboot")
        print(os.system("reboot"))


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

threading.Thread(target=main1.show, args=()).start()



