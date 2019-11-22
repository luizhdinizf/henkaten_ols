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


mac = socket.gethostname()
cap = cv2.VideoCapture(0)


class mainController():

    def __init__(self):
        self.mac = mac
        self.loggedUser = False
        self.saveNextFace = False
        self.doRecognition = True
        self.recognitionTimer = 0
        self.recogntionTimeout = 30
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
        self.faceDetector = faceDetector()
        self.workplace = workplace(mac)
        self.linha = linha(self.workplace.area, self.workplace.cliente, self.workplace.linha)
        self.linha.calculateAllMissingSkills(self.workplace)
        self.faceDetector.fillKnowFacesAndIndexes(self.linha)
        self.screen.setParametersFromWorkplace(self.workplace)
        self.loggedUser = False
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
            if self.loggedUser is False:
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
                self.doRecognition = not self.doRecognition
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
        self.linha.preencheReconhecidos(mac)
        self.screen.displayCenterRectangle()
        self.faceDetector.encodeFacesInImage(self.frame)
        self.faceDetector.makeFaceIndex()
        stringSubtitle = "Aguardando Login: "+str(maxReconhecimentos-len(self.faceDetector.faceIndexes))
        print(self.faceDetector.faceIndexes)
        if len(self.faceDetector.faceIndexes) > maxReconhecimentos:
            indiceDoColaboradorLogado = self.faceDetector.knownFacesIndexes[mode(self.faceDetector.faceIndexes)]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
            newColab = self.linha.colaboradores[indiceDoColaboradorLogado]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
            self.linha.reconhecidos = [newColab.matricula]  #Editar esta Linha para fazer login de mais de um ao mesmo tempo
            self.linha.preencheReconhecidos(mac)
            self.faceDetector.faceIndexes = []
            self.loggedUser = True
            #subprocess.call("./.ajudaMTZ.sh")
            subprocess.Popen("./.ajudaMTZ.sh")

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
        print(json.loads(response.text))


main1=mainController()
main1.show()
