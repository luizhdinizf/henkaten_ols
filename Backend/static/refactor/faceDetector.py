import face_recognition
from colaborador import *
import numpy as np
import cv2
class faceDetector():

    def __init__(self):
        self.scale = 4
        self.detectedFaceLocations=[]
        self.detectedColabs=[]
        self.detectedFaceEncodings=[]
        self.knownFacesIndexes=[]
        self.knownFacesEncoding=[]
        self.encodeNextFace=False

    def locateFacesInImage(self,frame):           
        frame = cv2.resize(frame, (0, 0), fx=1/self.scale, fy=1/self.scale)
        self.detectedFaceLocations = face_recognition.face_locations(frame) 
        

    def generateColabsWithoutDetectingFace(self):
        self.detectedColabs=[]  
        for face in self.detectedFaceLocations:
            unknownColab = colaborador()
            unknownColab.name = "Desconhecido"
            unknownColab.facePosition[0] = face[0]*self.scale
            unknownColab.facePosition[1] = face[1]*self.scale
            unknownColab.facePosition[2] = face[2]*self.scale
            unknownColab.facePosition[3] = face[3]*self.scale
            self.detectedColabs.append(unknownColab)

    def encodeFacesInImage(self,frame):       
        self.detectedFaceEncodings = face_recognition.face_encodings(frame, self.detectedFaceLocations)
        if self.encodeNextFace and len(self.detectedFaceEncodings)>0:
            self.encodeThisFace(frame)
            self.encodeNextFace = False
            
    def fillKnowFacesAndIndexes(self,frame,linha):
        for index,colab in enumerate(linha.colaboradores):
            if len(colab.encodedFace)>0:                
                self.knownFacesIndexes.append(index)
                self.knownFacesEncoding.append(colab.encodedFace)

    def encodeThisFace(self,frame):
        self.knownFacesIndexes=[5]
        self.knownFacesEncoding=self.detectedFaceEncodings
        print("Encoding")
         
    def recognizeFacesInImage(self,frame,linha):
        self.detectedColabs=[]
        for frameFaceEncoding, frameFaceLocation in zip(self.detectedFaceEncodings, self.detectedFaceLocations):
            matches = face_recognition.compare_faces(self.knownFacesEncoding, frameFaceEncoding)            
            knowFacesDistancesFromCurrent = face_recognition.face_distance(self.knownFacesEncoding, frameFaceEncoding)
            best_match_index = np.argmin(knowFacesDistancesFromCurrent)
            index = -1
            if matches[best_match_index]:
                    index = best_match_index
            if index == -1:
                unknownColab = colaborador()
                unknownColab.name = "Desconhecido"
                unknownColab.facePosition[0] = frameFaceLocation[0]*self.scale
                unknownColab.facePosition[1] = frameFaceLocation[1]*self.scale
                unknownColab.facePosition[2] = frameFaceLocation[2]*self.scale
                unknownColab.facePosition[3] = frameFaceLocation[3]*self.scale
                self.detectedColabs.append(unknownColab)
            else:
                newColab = linha.colaboradores[self.knownFacesIndexes[index]]
                newColab.facePosition[0] = frameFaceLocation[0]*self.scale
                newColab.facePosition[1] = frameFaceLocation[1]*self.scale
                newColab.facePosition[2] = frameFaceLocation[2]*self.scale
                newColab.facePosition[3] = frameFaceLocation[3]*self.scale 
                self.detectedColabs.append(newColab)
  