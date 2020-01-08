import face_recognition
from colaborador import colaborador
import numpy as np
import cv2
import os

path = 'c:\\projects\\hc2\\'





class faceDetector():

    def __init__(self):
        self.scale = 4
        self.detectedFaceLocations = []
        self.detectedColabs = []
        self.detectedFaceEncodings = []
        self.knownFacesIndexes = []
        self.knownFacesEncoding = []
        self.recognizedIndexes = []
        self.faceIndexes = []
        self.sensibility = 0.5

    def locateFacesInImage(self, frame):
        frame = cv2.resize(frame, (0, 0), fx=1/self.scale, fy=1/self.scale)
        self.detectedFaceLocations = face_recognition.face_locations(frame)

    def encodeFacesInImage(self, frame):
        frame = cv2.resize(frame, (0, 0), fx=1/self.scale, fy=1/self.scale)
        self.detectedFaceEncodings = face_recognition.face_encodings(frame, self.detectedFaceLocations)

    def generateColabsWithoutDetectingFace(self):
        self.detectedColabs = []
        for face in self.detectedFaceLocations:
            unknownColab = colaborador()
            unknownColab.name = "Desconhecido"
            unknownColab.facePosition[0] = face[0]*self.scale
            unknownColab.facePosition[1] = face[1]*self.scale
            unknownColab.facePosition[2] = face[2]*self.scale
            unknownColab.facePosition[3] = face[3]*self.scale
            self.detectedColabs.append(unknownColab)

    def fillKnowFacesAndIndexes(self):
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk("faces"):
            for file in f:
                if '.jpg' in file:
                    files.append(os.path.join(r, file))
        for index, loadedFace in enumerate(files):
            print(loadedFace)
            self.knownFacesIndexes.append(index)
            atualFace = cv2.imread(loadedFace)
            self.locateFacesInImage(atualFace)
            self.encodeFacesInImage(atualFace)
            self.knownFacesEncoding.append(self.detectedFaceEncodings[0])
        print(self.knownFacesEncoding)



    def findColabFromIndex(self, index, frameFaceLocation):
        if index == -1:
            unknownColab = colaborador()
            unknownColab.name = "Desconhecido"
            unknownColab.facePosition[0] = frameFaceLocation[0]*self.scale
            unknownColab.facePosition[1] = frameFaceLocation[1]*self.scale
            unknownColab.facePosition[2] = frameFaceLocation[2]*self.scale
            unknownColab.facePosition[3] = frameFaceLocation[3]*self.scale
            return (unknownColab)
        else:
            newColab = colaborador()
            newColab.name = "Reconhecido"
            newColab.qualificado = True
            newColab.borderColor = (0, 255, 0)
            newColab.txtQualificado = "Habilitado"
            newColab.facePosition[0] = frameFaceLocation[0]*self.scale
            newColab.facePosition[1] = frameFaceLocation[1]*self.scale
            newColab.facePosition[2] = frameFaceLocation[2]*self.scale
            newColab.facePosition[3] = frameFaceLocation[3]*self.scale
            return (newColab)

    def compareAndRecognizeDetectedFaces(self):
        self.detectedColabs = []
        if len(self.knownFacesEncoding) == 0 or len(self.detectedFaceEncodings) == 0:
            self.generateColabsWithoutDetectingFace()
        else:
            for frameFaceEncoding, frameFaceLocation in zip(self.detectedFaceEncodings, self.detectedFaceLocations):
                matches = face_recognition.compare_faces(self.knownFacesEncoding, frameFaceEncoding, self.sensibility)
                index = -1
                knowFacesDistancesFromCurrent = face_recognition.face_distance(self.knownFacesEncoding, frameFaceEncoding)
                best_match_index = np.argmin(knowFacesDistancesFromCurrent)
                if matches[best_match_index]:
                    index = best_match_index
                newColab = self.findColabFromIndex(index, frameFaceLocation)
                self.detectedColabs.append(newColab)
