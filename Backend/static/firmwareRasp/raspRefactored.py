import cv2
import face_recognition
import numpy as np
from mongoCli import *
import uuid
import subprocess
import socket


font = 4
video_capture = cv2.VideoCapture(0)
def encodeSingleFromImagePath(path):
    FaceImage = cv2.imread(path)
    frameDetectedFacesLocations = face_recognition.face_locations(FaceImage)
    frameDetectedFacesEncoding = face_recognition.face_encodings(FaceImage, frameDetectedFacesLocations)
    return frameDetectedFacesEncoding[0]

#luizEncodedFace = encodeSingleFromImagePath("Backend/static/firmwareRasp/luiz.jpg")

def displayInfo(frame,infos):
    fontSize = 0.5
    letterSpacing = int(24*fontSize+1)
    i=1  
    fontColor = (0,255,0)#bgr
    left = 10
    top = 10
    
    cv2.putText(frame, hostname, (left, top+letterSpacing*i), font, fontSize, fontColor, 1)
    i+=1      
    cv2.putText(frame, mac, (left, top+letterSpacing*i), font, fontSize, fontColor, 1)
    i+=1 
    for key in infos:        
        text = '{}:{}'.format(key,infos[key])
        cv2.putText(frame, text, (left, top+letterSpacing*i), font, fontSize, fontColor, 1)
        i+=1
    return frame

def displayIds(frame,ids):
    for colaborador in ids:
        (top, right, bottom, left) = colaborador['position']
        top *= scale
        right *= scale
        bottom *= scale
        left *= scale
        if len(colaborador['missingSkills'])>0:
            txtQualificado = "N Qualificado"
            borderColor = (0,0,255) #bgr
            fontSize = 0.5
            letterSpacing = int(24*fontSize+1)
            i=1  
            fontColor = (0,0,255)#bgr
            for skill in colaborador['missingSkills']:
                cv2.putText(frame, skill, (right, top+letterSpacing*i), font, fontSize, fontColor, 1)
                i+=1
        else:
            txtQualificado = "Qualificado"
            borderColor = (0,255,0) #bgr
        cv2.rectangle(frame, (left, top), (right, bottom), borderColor, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), borderColor, cv2.FILLED)
        cv2.putText(frame, colaborador['name'], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.putText(frame, txtQualificado, (left + 6, top - 6), font, 0.8, borderColor, 1)
    return frame


def saveRecognition(frame,ids):          
    for colaborador in ids:       
        (bottom, right, top, left) = colaborador['position']  
        top *= scale
        right *= scale
        bottom *= scale
        left *= scale        
        cropped = frame[bottom:top, left:right]
        uplaodImage(cropped)
        cv2.imshow("cropped", cropped)
    print("SalvarImagem")    
    return frame

def displayScreen(displayDict):
    frame = displayDict['frame']  
    ids   = displayDict['ids']
    linha = displayDict['linha']
    frame = displayIds(frame,ids)
    frame = displayInfo(frame,linha)
    cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)   
    cv2.imshow('Video', frame)

def recognizeInImage(frame,knownFacesEncoded):
    returnedFaces =[]
    frameDetectedFacesLocations = face_recognition.face_locations(frame)
    if len(knownFacesEncoded) == 0:
        for index,face in enumerate(frameDetectedFacesLocations):
            foundFace ={
                'index':-1,
                'position':face
            }
            returnedFaces.append(foundFace)
    else:
        frameDetectedFacesEncoding = face_recognition.face_encodings(frame, frameDetectedFacesLocations)
        for frameFaceEncoding,frameFaceLocation in zip(frameDetectedFacesEncoding,frameDetectedFacesLocations):
            matches = face_recognition.compare_faces(knownFacesEncoded, frameFaceEncoding)
            index = -1
            knowFacesDistancesFromCurrent = face_recognition.face_distance(knownFacesEncoded, frameFaceEncoding)
            best_match_index = np.argmin(knowFacesDistancesFromCurrent)
            if matches[best_match_index]:
                    index = best_match_index
            foundFace ={
                'index':index,
                'position':frameFaceLocation
            }
            returnedFaces.append(foundFace)
    return returnedFaces

def preparaDisplay(frame,wpInfo,recognizedFaces,encodedFaces,names,missingSkills):
    displayDict ={
    'frame':frame,
    'linha':{'key0':'value0','key1':'value1'},
    'ids':[]}
    ids = []
    linha={}
    linha['Cliente'] = ' '+wpInfo['cliente']
    linha['Area'] = ' '+wpInfo['area']
    linha['Linha'] = ' '+wpInfo['linha']
    for i,req in enumerate(wpInfo['requisitos']):
        linha[str(i)]=req
        
    displayDict['linha'] = linha
    
    for face in recognizedFaces:
        if face['index'] == -1:
            dictFromFace = {
            'position':face['position'],
            'name':str(face['index']),
            'missingSkills':['Desconhecido']   
        }
        else:          
            
            dictFromFace = {
                'position':face['position'],
                'name':names[face['index']],
                'missingSkills':missingSkills[face['index']]   
            }
        ids.append(dictFromFace)
    displayDict['ids'] = ids
    return displayDict



            
mac = hex(uuid.getnode())

print(mac)

wpInfo=getWorkplaceInfo({'mac':mac})
hostname = socket.gethostname()

print(mac)
print(hostname) #NissanMainDirec1

encodedFaces,nomes,missingSkills = getInformation(wpInfo)
scale = 4
processThisFrame = True
retrieveInformation = True
sendInformation = False
saveNextFace = False
logarColaborador = True
processedFrames = 0
framesFromLastRetrieve = 0
framesFromLastSend = 0
delaySalvar = 0
frameWithFace = []                   
cv2.namedWindow("cropped")
while 1:
    ret, frame = video_capture.read()  
    frame = cv2.flip(frame, 1)
    if retrieveInformation:  
        #wpInfo=getWorkplaceInfo({'mac':'0x87fdb4b8ca2d'})     
        encodedFaces,nomes,missingSkills = getInformation(wpInfo)
        retrieveInformation = False
    if processThisFrame:
        small_frame = cv2.resize(frame, (0, 0), fx=1/scale, fy=1/scale)
        try:
            recognizedFaces = recognizeInImage(small_frame,encodedFaces)
        except:
            pass
        if len(recognizedFaces)>0:
            frameWithFace = frame.copy()
        processThisFrame = False
    if sendInformation:
        print("INFORMING TO SERVER")        
        sendInformation = False
    if processedFrames > 30:
        processThisFrame = True
        processedFrames = 0
    else:
        processedFrames +=1
        
    if framesFromLastRetrieve  > 100:
        retrieveInformation = True
        framesFromLastRetrieve = 0
        try:            
            cv2.destroyWindow("cropped")
        except:
            pass
    else:
        framesFromLastRetrieve +=1 
       
   
    displayDict = preparaDisplay(frame,wpInfo,recognizedFaces,encodedFaces,nomes,missingSkills)
    if logarColaborador or saveNextFace:
        delaySalvar +=1
        maxTime = 150
        if delaySalvar < maxTime and logarColaborador:
            loginMessage = "Iniciando Login:" + str((maxTime-delaySalvar)/10)
        elif delaySalvar < maxTime and saveNextFace:
            loginMessage = "Iniciando Foto:" + str((maxTime-delaySalvar)/10)
        else:      
            loginMessage = "Pronto" 
        processThisFrame = False
        cv2.rectangle(frame, (100, 150), (500,400), (0, 255,0),)
        cv2.putText(frame, loginMessage, (0, 50), font, 1.8, (0, 0, 255), 1)
        if delaySalvar >maxTime:
            processThisFrame = True
        else:
            recognizedFaces = []
        if len(recognizedFaces)>0 and delaySalvar>maxTime:
            if logarColaborador:
                print(displayDict['ids'])
            if saveNextFace:
                saveRecognition(frameWithFace,displayDict['ids'])
            logarColaborador = False
            saveNextFace = False  
            delaySalvar = 0

   
    displayScreen(displayDict)
    key= cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('g'):
        saveNextFace = True
        print("g")
    if key == ord('y'):
        logarColaborador = True
    if key == ord('h'):
        missingSkills=[]
        print("h")
    if key == ord('j'):
        print(nomes)
        print("j")  
    if key == ord('r'):
        encodedFaces,nomes,missingSkills = getInformation(wpInfo)
video_capture.release()
cv2.destroyAllWindows()
