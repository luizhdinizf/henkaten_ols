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

class controller():

    def __init__(self,mac,cap,screen,faceDetector,linha):
        self.cap = cap
        self.mac = mac
        self.detectedColabs = []   
        self.frame = []
        self.screen = screen
        self.screen.hostname = mac
        self.faceDetector = faceDetector      
        self.linha = linha 
        self.faceDetector.fillKnowFacesAndIndexes(self.linha)


    def recognize(self):  
        while 1:
            try:                
                self.detectedColabs = []
                self.faceDetector.locateFacesInImage(self.frame)
                self.faceDetector.encodeFacesInImage(self.frame)
                self.faceDetector.compareAndRecognizeFaces()
                for faceLocation,matricula in zip(self.faceDetector.detectedFaceLocations,self.faceDetector.recognizedMatriculas):
                    colab = self.linha.findColabByMatricula(matricula)
                    colab.facePosition[0] = faceLocation[0]*self.faceDetector.scale
                    colab.facePosition[1] = faceLocation[1]*self.faceDetector.scale
                    colab.facePosition[2] = faceLocation[2]*self.faceDetector.scale
                    colab.facePosition[3] = faceLocation[3]*self.faceDetector.scale
                    self.detectedColabs.append(colab)
                time.sleep(0.5)
            except Exception as e:
                time.sleep(0.5)
                print(e)

    def show(self):
        recognitionThread = threading.Thread(target=self.recognize, args=()).start()
        while 1:
            _, self.frame = self.cap.read()
            self.frame = cv2.flip(self.frame, 1)            
            self.screen.recognizedColabs = self.detectedColabs
            self.screen.frame = self.frame.copy()
            self.screen.displayAll()
            self.screen.show()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('g'):
                self.saveNextFace = True
        self.__del__()
    def __del__(self):
        cv2.destroyAllWindows()
        self.cap.release()