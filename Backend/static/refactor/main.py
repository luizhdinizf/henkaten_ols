import cv2

import numpy as np

from colaborador import colaborador
from linha import linha
from workplace import workplace
from faceDetector import faceDetector
from screenController import screenController


mac ='0xb827ebb984f1'


class mainController():
    def __init__(self):
        self.mac ='0xb827ebb984f1'
        self.loggedUser = False
        self.saveNextFace = False
        self.workplace = workplace(mac)
        self.frame =[]
        self.cap = cv2.VideoCapture(0)
        self.linha = linha(self.workplace.area,self.workplace.cliente,self.workplace.linha)
        self.linha.calculateAllMissingSkills(self.workplace)
        self.screen = screenController()        
        self.faceDetector = faceDetector()        
        self.faceDetector.fillKnowFacesAndIndexes(self.frame,self.linha)
        self.screen.setParametersFromWorkplace(self.workplace)

    def show(self):
        while 1:
            _,self.frame = self.cap.read()
            self.faceDetector.locateFacesInImage(self.frame)
            self.faceDetector.encodeFacesInImage(self.frame)   
            self.faceDetector.recognizeFacesInImage(self.frame,self.linha)          
            self.screen.recognizedColabs=self.faceDetector.detectedColabs
            self.screen.frame=self.frame  
            self.screen.displayAll()
            if self.loggedUser == False:                
                self.screen.displayCenterRectangle()
                self.screen.displaySubtitule("Aguardando Login")
                if len(self.faceDetector.detectedColabs)>0:
                    self.loggedUser = True
            if self.saveNextFace == True:                
                self.screen.displayCenterRectangle()
                self.screen.displaySubtitule("Cadastrar")
                if len(self.faceDetector.detectedColabs)>0:
                    for colaborador in self.faceDetector.detectedColabs:
                        colaborador.updateFaceImage(self.frame)
                        cv2.imshow(colaborador.name,colaborador.faceImage)
                    self.saveNextFace = False
            
            self.screen.show()          
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('r'):
                self.loggedUser = False
            if key == ord('g'):
                self.faceDetector.encodeNextFace = True
        self.__del__()

   
    def __del__(self):
        cv2.destroyAllWindows()
        self.cap.release()
 





main1 = mainController()
main1.show()
