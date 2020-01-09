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
import rede


cap = cv2.VideoCapture(0)
   

mac = socket.gethostname()




   



 
        

print("TESTANDO")
parametros = []
main1 = controller(mac,cap,screenController(),faceDetector(),linha(parametros))
#main1.show()
showThread = threading.Thread(target=main1.show, args=()).start()

teste = main1.faceDetector
def compareAndRecognizeFaces(teste):
    teste.recognizedMatriculas = []
    for frameFaceEncoding, _ in zip(teste.detectedFaceEncodings, teste.detectedFaceLocations):
        matches = face_recognition.compare_faces(teste.knownFacesEncoding[0], frameFaceEncoding, teste.sensibility)
        knowFacesDistancesFromCurrent = face_recognition.face_distance(teste.knownFacesEncoding[0], frameFaceEncoding)
        index = -1  
        try:
            best_match_index = np.argmin(knowFacesDistancesFromCurrent)
            if matches[best_match_index]:                
                index = best_match_index               
                teste.recognizedMatriculas.append(teste.knownFacesMatriculas[index])
            else:
                teste.recognizedMatriculas.append(index)
        except Exception as e:
            print(e)
            teste.recognizedMatriculas.append(index)
        print(teste.recognizedMatriculas)

compareAndRecognizeFaces(teste)
print(main1.faceDetector.recognizedMatriculas)
print(teste.recognizedMatriculas)
print(main1.linha.findColabByMatricula('0').name)
import numpy as np