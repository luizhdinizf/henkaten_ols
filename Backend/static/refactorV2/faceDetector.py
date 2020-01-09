import face_recognition
from colaborador import colaborador
import numpy as np
import cv2


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

    def fillKnowFacesAndIndexes(self, linha):
        for index, colab in enumerate(linha.colaboradores):
            if len(colab.encodedFace) > 0:
                self.knownFacesIndexes.append(index)
                self.knownFacesEncoding.append(colab.encodedFace)

    def encodeThisFace(self, frame):
        self.knownFacesEncoding = self.detectedFaceEncodings

    def makeFaceIndex(self):
        self.detectedColabs = []
        if len(self.knownFacesEncoding) == 0 or len(self.detectedFaceEncodings) == 0:
            pass
        else:
            for frameFaceEncoding, frameFaceLocation in zip(self.detectedFaceEncodings, self.detectedFaceLocations):
                matches = face_recognition.compare_faces(self.knownFacesEncoding, frameFaceEncoding, self.sensibility)
                index = -1
                knowFacesDistancesFromCurrent = face_recognition.face_distance(self.knownFacesEncoding, frameFaceEncoding)
                best_match_index = np.argmin(knowFacesDistancesFromCurrent)
                if matches[best_match_index]:
                    index = best_match_index
                    self.faceIndexes.append(index)
                


    def findColabFromIndex(self, linha, index, frameFaceLocation):
        if index == -1:
            unknownColab = colaborador()
            unknownColab.name = "Desconhecido"
            unknownColab.facePosition[0] = frameFaceLocation[0]*self.scale
            unknownColab.facePosition[1] = frameFaceLocation[1]*self.scale
            unknownColab.facePosition[2] = frameFaceLocation[2]*self.scale
            unknownColab.facePosition[3] = frameFaceLocation[3]*self.scale
            return (unknownColab)
        else:
            newColab = linha.colaboradores[self.knownFacesIndexes[index]]
            newColab.facePosition[0] = frameFaceLocation[0]*self.scale
            newColab.facePosition[1] = frameFaceLocation[1]*self.scale
            newColab.facePosition[2] = frameFaceLocation[2]*self.scale
            newColab.facePosition[3] = frameFaceLocation[3]*self.scale
            return (newColab)


    def compareAndRecognizeDetectedFaces(self, linha):
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
                newColab = self.findColabFromIndex(linha, index, frameFaceLocation)
                self.detectedColabs.append(newColab)
