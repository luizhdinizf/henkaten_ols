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
from datetime import datetime
from database import database


def findMostFrequent(list):
    from collections import Counter
    x = Counter(list)
    inverse = [(value, key) for key, value in x.items()]
    return (max(inverse)[1])




class controller():
    def __init__(self, mac, cap, screen, faceDetector, linha, workplace):
        self.cap = cap
        self.mac = mac
        self.screen = screen
        self.faceDetector = faceDetector
        self.linha = linha
        self.maxReconhecimentos = 5
        self.detectedColabs = []
        self.frame = []
        self.workplace = workplace
        self.restart()
        self.logar = True
        self.logados = []
        self.saveNextFace = False
        self.simular = False

    def registraEvento(self,evento,dado):
        collection = database['historico']
        now = datetime.now()
        today = now.strftime("%d-%m-%Y, %H:%M:%S")
        dict = {"Posto": self.workplace.posto,"date":today,"dado":dado,"evento":evento} 
        result = collection.insert_one(dict)

    def restart(self):
        self.workplace.getInfo(self.mac)
        self.linha.findColaboradores(self.linha.queryParametros("Ato"))
        self.linha.calculateAllMissingSkills(self.workplace.requisitos)
        self.faceDetector.fillKnowFacesAndIndexes(self.linha)

    def validaLogin(self):
        matriculas = []
        for colab in self.logados:
            matriculas.append(colab.matricula)
        mostFrequentMatricula = findMostFrequent(matriculas)
        if mostFrequentMatricula != -1:
            colabLogado = colab = self.linha.findColabByMatricula(mostFrequentMatricula)
            if colabLogado.qualificado is True:                
                try:
                    if colabLogado not in self.workplace.logados:
                        self.registraEvento("login",colabLogado.name)
                        self.workplace.logados.add(colabLogado)
                    #self.workplace.preencheReconhecidos()
                except Exception as e:
                    print(e)
                self.screen.popupText = "Sucesso! Bem Vindo:"
                self.screen.popupText2 = colabLogado.name
                threading.Thread(target=self.displayPopup, args=()).start()
                subprocess.Popen("./.ajudaMTZ.sh")
                self.logar = False
            else:
                self.screen.popupText = "Falha no Login"
                self.screen.popupText2 = ""
                threading.Thread(target=self.displayPopup, args=()).start()                
        self.logados = []

    def displayPopup(self):
        self.screen.showPopup = True
        time.sleep(3)
        self.screen.showPopup = False

    def recognize(self):
        while 1:
            try:
                self.detectedColabs = []
                self.faceDetector.locateFacesInImage(self.frame)
                self.faceDetector.encodeFacesInImage(self.frame)
                self.faceDetector.compareAndRecognizeFaces()
                for faceLocation, matricula in zip(self.faceDetector.detectedFaceLocations,self.faceDetector.recognizedMatriculas):
                    colab = self.linha.findColabByMatricula(matricula)
                    colab.facePosition[0] = faceLocation[0]*self.faceDetector.scale
                    colab.facePosition[1] = faceLocation[1]*self.faceDetector.scale
                    colab.facePosition[2] = faceLocation[2]*self.faceDetector.scale
                    colab.facePosition[3] = faceLocation[3]*self.faceDetector.scale
                    self.detectedColabs.append(colab)
                    if self.logar is True and self.saveNextFace is False:
                        self.logados.append(colab)
                        if len(self.logados) > self.maxReconhecimentos:                           
                            self.validaLogin()
                    else:
                        self.logados = []                        
                    if self.saveNextFace is True:
                        colab.updateFaceImage(self.frame)
                        self.uploadImage(colab.faceImage)
                        self.saveNextFace = False
                time.sleep(0.2)

            except Exception as e:
                time.sleep(0.5)

    def show(self):
        threading.Thread(target=self.recognize, args=()).start()
        while 1:
            _, frameInicial = self.cap.read()
            if self.simular is False:
                self.frame = cv2.flip(frameInicial, 1)
            self.screen.recognizedColabs = self.detectedColabs
            self.screen.frame = self.frame.copy()
            self.screen.displayAll()
            if self.logar is True and self.saveNextFace is False:
                self.screen.displayCenterRectangle()
                stringSubtitle = "Aguardando Login: "+str(self.maxReconhecimentos-len(self.logados))
                self.screen.displaySubtitule(stringSubtitle)
            elif self.saveNextFace is True:
                self.screen.displayCenterRectangle()
                stringSubtitle = "Cadastramento"
                self.screen.displaySubtitule(stringSubtitle)

            if len(self.workplace.logados) == 0:
                subprocess.call("./.killChromium.sh")
                self.logar = True
            self.screen.show()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('l'):
                subprocess.call("./.killChromium.sh")
                self.logar = True
            if key == ord('g'):
                subprocess.call("./.killChromium.sh")
                self.saveNextFace = True
            if key == ord('r'):
                self.restart()
        self.__del__()

    def __del__(self):
        cv2.destroyAllWindows()
        self.cap.release()

    def uploadImage(self, img):
        serverAddress = 'http://brmtz-dev-001:800'
        fullUrl = serverAddress + '/api/upload'
        content_type = 'image/jpeg'
        headers = {'content-type': content_type}
        _, img_encoded = cv2.imencode('.jpg', img)
        response = requests.post(fullUrl, data=img_encoded.tostring(), headers=headers)