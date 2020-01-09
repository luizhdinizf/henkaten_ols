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
                self.workplace.logados.add(colabLogado)
                try:
                    self.workplace.preencheReconhecidos()
                except Exception as e:
                    print(e)
                self.screen.popupText = "Sucesso! Bem Vindo:"
                self.screen.popupText2 = colabLogado.name
                popupThread = threading.Thread(target=self.displayPopup, args=()).start()
                self.logar = False
            else:
                self.screen.popupText = "Falha no Login"
                self.popupText2 = ""
                popupThread = threading.Thread(target=self.displayPopup, args=()).start()                
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
                    if self.logar is True:
                        self.logados.append(colab)
                        if len(self.logados) > self.maxReconhecimentos:                           
                            self.validaLogin()
                    else:
                        self.logados = []
                time.sleep(0.2)

            except Exception as e:
                time.sleep(0.5)
            

    def show(self):
        recognitionThread = threading.Thread(target=self.recognize, args=()).start()
        while 1:
            _, frameInicial = self.cap.read()
            self.frame = cv2.flip(frameInicial, 1)
            self.screen.recognizedColabs = self.detectedColabs
            self.screen.frame = self.frame.copy()
            self.screen.displayAll()
            if self.logar is True:
                self.screen.displayCenterRectangle()
                stringSubtitle = "Aguardando Login: "+str(self.maxReconhecimentos-len(self.logados))
                self.screen.displaySubtitule(stringSubtitle)
            self.screen.show()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('l'):
                self.logar = True
            if key == ord('g'):
                self.saveNextFace = True
            if key == ord('r'):
                self.restart = True
        self.__del__()
    def __del__(self):
        cv2.destroyAllWindows()
        self.cap.release()