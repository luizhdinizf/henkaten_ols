import cv2
from database import database
from linha import linha
from workplace import workplace
from faceDetector import faceDetector
from screenController import screenController
from statistics import mode
import subprocess
import requests
import json
import socket
import paho.mqtt.client as mqtt
import fcntl
import struct
import os
import time
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256', ifname[:15])
    )[20:24])




def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mac
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mac+"/#")
    client.subscribe("broadcast/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        global main1
    except:
        pass
    #print(msg.topic+" "+str(msg.payload))
    mensagem = str(msg.payload.decode("utf-8"))
  
    print(msg.topic+" "+mensagem)
    if mensagem == "reset":
        print("RESETANDO")
        try:
            main1.restartParams()
        except:
            pass
       # 
    elif mensagem == "cadastrar":
        try:
            main1.saveNextFace = True
        except:
            pass
        
    elif mensagem == "reboot":
        print("try to reboot")
        print(os.system("reboot"))

   

mac = socket.gethostname()
try:
    cap = cv2.VideoCapture(0)
except:
    pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("brmtz-dev-001", 1883, 60)
client.loop_start()


class mainController():

    def __init__(self):
        self.mac = mac
        client.publish(self.mac+"/logado", "false", retain=False)
        self.loggedUser = False
        self.saveNextFace = False
        self.doRecognition = True
        self.recognitionTimer = 0
        self.recogntionTimeout = 30
        self.loginTimer = 0
        self.loginTimeout = 1000
        self.frame = []
        self.screen = screenController()
        self.screen.hostname = mac
        self.faceDetector = faceDetector()
        self.workplace = workplace(mac)
        self.linha = linha(self.workplace.area, self.workplace.cliente, self.workplace.linha)
        self.linha.calculateAllMissingSkills(self.workplace)
        self.faceDetector.fillKnowFacesAndIndexes(self.linha)
        self.screen.setParametersFromWorkplace(self.workplace)

    def restartParams(self):
        client.publish(self.mac+"/logado", "false", retain=False)
        self.faceDetector = faceDetector()
        self.workplace = workplace(mac)
        self.linha = linha(self.workplace.area, self.workplace.cliente, self.workplace.linha)
        self.linha.calculateAllMissingSkills(self.workplace)
        self.faceDetector.fillKnowFacesAndIndexes(self.linha)
        self.screen.setParametersFromWorkplace(self.workplace)
        self.loggedUser = False
        self.loginTimer = 0
        subprocess.call("./.killChromium.sh")

    def show(self):
        while 1:
            _, self.frame = cap.read()
            self.frame = cv2.flip(self.frame, 1)
            self.faceDetector.locateFacesInImage(self.frame)
            if self.doRecognition is True:
                self.faceDetector.encodeFacesInImage(self.frame)
            self.faceDetector.compareAndRecognizeDetectedFaces(self.linha)

            self.screen.recognizedColabs = self.faceDetector.detectedColabs
            self.screen.frame = self.frame.copy()
            self.screen.displayAll()
            self.timingFunction()

            if self.saveNextFace is True:
                self.saveNextFaceFunction()
            elif self.loggedUser is False:
                self.doRecognition = False
                self.aguardarLoggin()

            self.screen.show()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('r'):
                self.restartParams()
            if key == ord('g'):
                self.saveNextFace = True
            if key == ord('l'):
                self.faceDetector.faceIndexes.append(3)
        self.__del__()

    def __del__(self):
        cv2.destroyAllWindows()
        cap.release()

    def timingFunction(self):
        if self.recognitionTimer > self.recogntionTimeout:
            self.doRecognition = True
            self.recognitionTimer = 0
        else:
            self.doRecognition = False
            self.recognitionTimer += 1

    def aguardarLoggin(self):
        self.linha.reconhecidos = []
        maxReconhecimentos = 5
        self.loginTimer += 1
        #self.linha.preencheReconhecidos(self.workplace)
        self.screen.displayCenterRectangle()
        self.faceDetector.encodeFacesInImage(self.frame)
        self.faceDetector.makeFaceIndex()
        stringSubtitle = "Aguardando Login: "+str(maxReconhecimentos-len(self.faceDetector.faceIndexes))
        #print(self.faceDetector.faceIndexes)
        if len(self.faceDetector.faceIndexes) >= maxReconhecimentos:
            client.publish(self.mac+"/logado", "true", retain=False)
            try:
                indiceDoColaboradorLogado = self.faceDetector.knownFacesIndexes[mode(self.faceDetector.faceIndexes)]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
                newColab = self.linha.colaboradores[indiceDoColaboradorLogado]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
                if (newColab.qualificado):
                    self.linha.reconhecidos = [newColab.name]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
                    self.linha.preencheReconhecidos(self.workplace)
                    self.faceDetector.faceIndexes = []
                    self.loggedUser = True                    
                    subprocess.Popen("./.ajudaMTZ.sh")
                else:
                    self.restartParams()
            except Exception as e:
                print(str(e))
                self.restartParams()
        if self.loginTimer > self.loginTimeout:
            self.restartParams()
        self.screen.displaySubtitule(stringSubtitle)

    def saveNextFaceFunction(self):
        if len(self.faceDetector.detectedColabs) > 0:
            for colab in self.faceDetector.detectedColabs:
                colab.updateFaceImage(self.frame)
                #cv2.imshow(colab.name, colab.faceImage)
                self.uploadImage(colab.faceImage)
            self.saveNextFace = False
        self.screen.displayCenterRectangle()
        self.screen.displaySubtitule("Cadastrar")

    def uploadImage(self, img):
        serverAddress = 'http://brmtz-dev-001:800'
        fullUrl = serverAddress + '/api/upload'
        content_type = 'image/jpeg'
        headers = {'content-type': content_type}
        _, img_encoded = cv2.imencode('.jpg', img)
        response = requests.post(fullUrl, data=img_encoded.tostring(), headers=headers)
        print(response.text)

if mac != "RMTZ3047":    
    try:
        print("TESTANDO")
        main1 = mainController()
        main1.show()
    except Exception as e:
        print(str(e))
        time.sleep(5)
        client.publish(mac+"/logado", "true", retain=False)
        subprocess.Popen("./.ajudaMTZ.sh")
        time.sleep(5)
        while 1:
            client.publish(mac+"/logado", "true", retain=False)
            time.sleep(20)

else:
    client.publish(mac+"/logado", "false", retain=True)

    while 1:
        cmd = "/sbin/ifconfig wlan0 | grep 'inet' |  awk '{print $2}'"
        ip = os.system(cmd)
        time.sleep(1)
