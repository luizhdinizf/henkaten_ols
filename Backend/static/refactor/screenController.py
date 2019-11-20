from colaborador import colaborador
import numpy as np
import cv2


class screenController():

    def __init__(self):
        self.frame = np.zeros((1000, 1000, 3), np.uint8)
        self._cliente = 'a'
        self._area = 'b'
        self._linha = 'linha'
        self._modelo = ""
        self._hostname = 'hostname'
        self._requisitos = 'requisitos'
        self._mac = 'mac'
        self.recognizedColabs = []
        self.font = 4
        self.rectangleSizeInPercentOfScreen = 0.8

    def setParametersFromWorkplace(self, workplace):
        self._cliente = workplace.cliente
        self._area = workplace.area
        self._linha = workplace.linha
        self._requisitos = workplace.requisitos
        self._mac = workplace.mac
        self._modelo = workplace.modelo

    def displayAll(self):
        self.displayInfo()
        self.displayRecognizedFaces()

    def show(self):
        cv2.imshow('Video', self.frame)

    def displayCenterRectangle(self):
        frameMask = np.zeros(self.frame.shape, np.uint8)
        frameMask[:,:] = (255, 255, 255)
        self.screenSizeX = self.frame.shape[1]
        self.screenSizeY = self.frame.shape[0]
        self.screenCenterX = self.screenSizeX/2
        self.screenCenterY = self.screenSizeY/2
        rectangleLeft = int(self.screenCenterX-self.rectangleSizeInPercentOfScreen*self.screenSizeX/2)
        rectangleRight = int(self.screenCenterX+self.rectangleSizeInPercentOfScreen*self.screenSizeX/2)
        rectangleTop = int(self.screenCenterY-self.rectangleSizeInPercentOfScreen*self.screenSizeX/2/2)
        rectangleBottom = int(self.screenCenterY+self.rectangleSizeInPercentOfScreen*self.screenSizeX/2/2)
        cv2.rectangle(frameMask, (rectangleLeft, rectangleTop), (rectangleRight, rectangleBottom), (0, 255, 0), cv2.FILLED)
        alpha = 0.2
        cv2.addWeighted(frameMask, alpha, self.frame, 1 - alpha,
		0, self.frame)

    def displaySubtitule(self, text):
        self.screenSizeX = self.frame.shape[1]
        self.screenSizeY = self.frame.shape[0]
        self.screenCenterX = self.screenSizeX/2
        self.screenCenterY = self.screenSizeY/2
        titleTop = int(self.screenCenterY-self.rectangleSizeInPercentOfScreen*self.screenSizeX/2/2)-20
        titleLeft = int(self.screenCenterX-self.rectangleSizeInPercentOfScreen*self.screenSizeX/2)
        cv2.putText(self.frame, text, (titleLeft, titleTop), self.font, 1.5, (0, 0, 255), 1)


    def displayInfo(self):
        self.fontSize = 0.5
        letterSpacing = int(24*self.fontSize+1)
        self.fontColor = (0, 255, 0)  # bgr green
        left = 10
        top = 10
        cv2.putText(self.frame, self._hostname, (left, top+letterSpacing*1),self.font, self.fontSize, self.fontColor, 1)
        cv2.putText(self.frame, self._mac, (left, top+letterSpacing*2),self.font, self.fontSize, self.fontColor, 1)
        cv2.putText(self.frame, self._cliente, (left, top+letterSpacing*3),self.font, self.fontSize, self.fontColor, 1)
        cv2.putText(self.frame, self._area, (left, top+letterSpacing*4),self.font, self.fontSize, self.fontColor, 1)
        cv2.putText(self.frame, self._linha, (left, top+letterSpacing*5),self.font, self.fontSize, self.fontColor, 1)
        cv2.putText(self.frame, self._modelo, (left, top+letterSpacing*6),self.font, self.fontSize, self.fontColor, 1)

    def displayRecognizedFaces(self):        
        for colaborador in self.recognizedColabs:
            (top, right, bottom, left) = colaborador.facePosition
            self.fontSize = 0.5
            i=0
            letterSpacing = int(24*self.fontSize+1)
            for skill in colaborador.missingSkills:
                self.fontColor = (0,0,255)
                cv2.putText(self.frame, skill, (right, top+5+letterSpacing*i),self.font, self.fontSize, self.fontColor, 1)
                i += 1        
            cv2.rectangle(self.frame, (left, top), (right, bottom), colaborador.borderColor, 2)
            cv2.rectangle(self.frame, (left, bottom - 35),(right, bottom), colaborador.borderColor, cv2.FILLED)
            cv2.putText(self.frame, colaborador.name, (left + 6,bottom - 6), self.font, 1.0, (255, 255, 255), 1)
            cv2.putText(self.frame, colaborador.txtQualificado, (left + 6, top - 6),self.font, 0.8,colaborador.borderColor, 1)
