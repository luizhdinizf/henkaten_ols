import face_recognition
import numpy as np
import cv2


class faceDetector():

    def __init__(self):
        self.detectedFaceLocations = []
        self.detectedFaceEncodings = []
        self.knownFacesMatriculas = []
        self.knownFacesEncoding = []
        self.recognizedMatriculas = []
        self.scale = 4
        self.sensibility = 0.5


    def locateFacesInImage(self, frame):
        frame = cv2.resize(frame, (0, 0), fx=1/self.scale, fy=1/self.scale)
        self.detectedFaceLocations = face_recognition.face_locations(frame)

    def encodeFacesInImage(self, frame):
        frame = cv2.resize(frame, (0, 0), fx=1/self.scale, fy=1/self.scale)
        self.detectedFaceEncodings = face_recognition.face_encodings(frame, self.detectedFaceLocations)

    def compareAndRecognizeFaces(self):
        self.recognizedMatriculas = []
        for frameFaceEncoding, _ in zip(self.detectedFaceEncodings, self.detectedFaceLocations):
            matches = face_recognition.compare_faces(self.knownFacesEncoding, frameFaceEncoding, self.sensibility)
            knowFacesDistancesFromCurrent = face_recognition.face_distance(self.knownFacesEncoding, frameFaceEncoding)
            index = -1
            try:
                best_match_index = np.argmin(knowFacesDistancesFromCurrent)
                if matches[best_match_index]:                
                    index = best_match_index               
                    self.recognizedMatriculas.append(self.knownFacesMatriculas[index])
                else:
                    self.recognizedMatriculas.append(index)
            except Exception as e:
                print(e)
                self.recognizedMatriculas.append(index)
        
        
    def fillKnowFacesAndIndexes(self, linha):
        for colab in linha.colaboradores:
            if len(colab.encodedFace) > 0:
                self.knownFacesMatriculas.append(colab.matricula)
                self.knownFacesEncoding.append(colab.encodedFace)

 

   



