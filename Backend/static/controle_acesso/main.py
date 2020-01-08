import cv2


from faceDetector import faceDetector
from screenController import screenController
import socket
import paho.mqtt.client as mqtt
import fcntl
import struct
import threading
import time

import RPi.GPIO as GPIO           # import RPi.GPIO module  
GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(4, GPIO.OUT) # set a port/pin as an output   


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256', ifname[:15])
    )[20:24])





try:
    cap = cv2.VideoCapture(0)
except:
    pass



class portao():

    def __init__(self):
        self.status = "Fechado"
        self.timer = 0
        self.timeoutAbrir = 10
        self.timeoutFechar = 10
        self.timeoutAberto = 15


    def processar(self):
        print("STARTING THREAD")
        while 1:
            if self.status == "Abrindo":

                time.sleep(self.timeoutAbrir)
                self.status = "Aberto"
                print(self.status)
            elif self.status == "Fechando":
                time.sleep(self.timeoutFechar)
                self.status = "Fechado"
                print(self.status)
            elif self.status == "Aberto":
                time.sleep(self.timeoutAberto)
                self.fechar()
                print(self.status)

    def abrir(self):
        if self.status == "Fechado":
            self.status = "Abrindo"
            print("Abrir")
            GPIO.output(4, 1)  
            print("Saida HIGH")
            time.sleep(0.3)
            GPIO.output(4, 0) 
            print("Saida LOW")
            
    def fechar(self):
        if self.status == "Aberto":
            self.status = "Fechando"
            print("Fechar")
            GPIO.output(4, 1)       # set port/pin value to 1/GPIO.HIGH/True  
            print("Saida HIGH")
            time.sleep(0.3)
            GPIO.output(4, 0) 
            print("Saida LOW")
            


class mainController():

    def __init__(self):
        _, self.frame = cap.read()
        self.loggedUser = False
        self.recognizer = faceDetector()
        self.recognizer.fillKnowFacesAndIndexes()
        self.screen = screenController()
        self.gate = portao()
        self.gateThread = threading.Thread(target=self.gate.processar, args=()).start()
        self.recognitionThread = threading.Thread(target=self.recognition, args=()).start()

    def recognition(self):
        while 1:
            self.recognizer.locateFacesInImage(self.frame)
            self.recognizer.encodeFacesInImage(self.frame)
            self.recognizer.compareAndRecognizeDetectedFaces()
            self.screen.recognizedColabs = self.recognizer.detectedColabs
            time.sleep(1)
    def display(self):
        self.screen.frame = self.frame.copy()
        self.screen.displayAll()
        self.screen.show()
    def show(self):
        while 1:
            _, self.frame = cap.read()
            self.frame = cv2.flip(self.frame, 1)
            self.display()
            for colab in self.recognizer.detectedColabs:
                if colab.qualificado is True:
                    self.gate.abrir()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.gateThread.stop()
                break

    def __del__(self):
        cv2.destroyAllWindows()
        cap.release()

main1 = mainController().show()
