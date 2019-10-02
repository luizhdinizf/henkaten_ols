import face_recognition
import cv2
import numpy as np
from mongoServer import *
import uuid 
workplaceInfo = getWorkplaceInfo('0x87fdb4b8ca2d')
mac = hex(uuid.getnode()) 
ids = workplaceInfo['colaboradores']
faceNames,encodedFaces = getFacesFromIds(ids)


def recognizeInFrame(frame,encodedFaces,faceNames):
# Find all the faces and face encodings in the current frame of video
    recognizedLocations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, recognizedLocations)
    recognizedNames = []
    for face_encoding,recognizedLocation in zip(face_encodings,recognizedLocations):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(encodedFaces, face_encoding)
        name = "Desconhecido"

        # # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(encodedFaces, face_encoding)
        if len(encodedFaces) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = faceNames[best_match_index]
        recognizedNames.append(name)
    return([recognizedLocations,recognizedNames])
def displayMissingSkills(frame,missingSkills,intialX,intialY):
    try:
        fontSize = 0.5
        letterSpacing = int(24*fontSize+1)
        i=0      
        color = (0,0,255)
        for j,a in enumerate(missingSkills):
            cv2.putText(frame, a, (intialX, intialY+letterSpacing*(i+j)), font, fontSize, color, 1)
    except:
        pass
    return frame

def displayRecognition(frame,scale,recognizedLocations, recognizedNames,recognizedIds,wpInfo,saveImage,missingSkills):
    try:
        for (top, right, bottom, left), name,id in zip(recognizedLocations, recognizedNames,recognizedIds):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    
            
            if len(missingSkills) > 0:
                frame = displayMissingSkills(frame,missingSkills,right+5,top+10)
                color = (0,0,255)
            else:
                color=(0,255,0)
            #print(missingSkills)
            
            top *= scale
            right *= scale
            bottom *= scale
            left *= scale
            if name == "Desconhecido" and saveImage == True:   
                     
                saveImage = False       
                croppedFace = frame[top:bottom, left:right]
                cv2.imshow("Desc",croppedFace)                
                saveImageOnUrl(croppedFace,'a')
                #saveImageOnDatabase(wpInfo,croppedFace)



            name = name[0:10]
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
    except Exception as e: print(e)
    return saveImage,frame
        


def displayFrameInfo(frame,workplaceInfo):
    fontSize = 0.5
    letterSpacing = int(24*fontSize+1)
    intialX=10
    intialY=10
    i=0   
    color=(0,60,0)
    
    cv2.putText(frame, workplaceInfo['cliente'], (intialX, intialY), font, fontSize,color, 1)
    i+=1
    cv2.putText(frame, workplaceInfo['area'], (intialX, intialY+letterSpacing*i), font, fontSize, color, 1)
    i+=1
    cv2.putText(frame, workplaceInfo['linha'], (intialX, intialY+letterSpacing*i), font, fontSize, color, 1)
    i+=1
    cv2.putText(frame, workplaceInfo['modelo'], (intialX, intialY+letterSpacing*i), font, fontSize, color, 1)
    i+=1
    for j,a in enumerate(workplaceInfo['requisitos']):
        cv2.putText(frame, a, (intialX, intialY+letterSpacing*(i+j)), font, fontSize, color, 1)

    return frame

def startProcessing(workplaceInfo):
    video_capture = cv2.VideoCapture(0)
    recognizedLocations = []
    recognizedNames = []
    idsReconhecidos = []
    scale=1
    process_this_frame = True
    framesSemNimguem = 0
    timeoutReconhecimento = 100
    missingSkills=[]
    processado = 25
    
    workplaceInfo = getWorkplaceInfo('0x87fdb4b8ca2d')
    mac = hex(uuid.getnode()) 
    ids = workplaceInfo['colaboradores']
    faceNames,encodedFaces = getFacesFromIds(ids)
    saveImage = False
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=1/scale, fy=1/scale)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        frame = displayFrameInfo(frame,workplaceInfo)
        if process_this_frame:            
            recognizedLocations,recognizedNames = recognizeInFrame(rgb_small_frame,encodedFaces,faceNames)
            idsReconhecidos = getIdsFromNames(recognizedNames)  
            preencheReconhecidos(workplaceInfo['N'],idsReconhecidos)
            requisitos = list(workplaceInfo['requisitos'])              
            missingSkills=processMissingSkills(requisitos,idsReconhecidos)     
           # for a in [frame,scale,recognizedLocations,recognizedNames,idsReconhecidos,workplaceInfo,saveImage,missingSkills]:
              #  print(a)
       
        
        
        saveImage,frame = displayRecognition(frame,scale,recognizedLocations,recognizedNames,idsReconhecidos,workplaceInfo,saveImage,missingSkills)
        cv2.putText(frame, str(framesSemNimguem), (250, 50), font, 1.0, (255,255,255), 1)
        framesSemNimguem +=1
        
        if framesSemNimguem > timeoutReconhecimento:           
            workplaceInfo = getWorkplaceInfo('0x87fdb4b8ca2d')
            framesSemNimguem = 0
            preencheReconhecidos(workplaceInfo['N'],idsReconhecidos)   
            process_this_frame = True         
        else:            
            process_this_frame = False
        



        # Display the results
        

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        key= cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            workplaceInfo = getWorkplaceInfo('0x87fdb4b8ca2d')
            ids = workplaceInfo['colaboradores']
            faceNames,encodedFaces = getFacesFromIds(ids)         
        elif key == ord('g'):
            saveImage = True
        elif key == ord('p'):            
            newFace = retrieveImage(workplaceInfo)
            cv2.imshow('newFace', newFace)

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

font = 4
startProcessing(workplaceInfo)


