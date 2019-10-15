import numpy as np
import pandas as pd
from pymongo import MongoClient
import requests
import json
import cv2
import gridfs

client = MongoClient("mongodb://172.22.45.216:27017/")
database = client["henkaten_ols"]



def acharColaboradores(queryColaboradores):
    projection = {}
    projection["MATRÍCULA"] = 1.0    
    colaboradores=[]
    cursor = database.find(queryColaboradores, projection = projection)
    try:
        for doc in cursor:
            colaboradores.append((doc['_id']))
            #print(doc)
        return colaboradores
    finally:
        client.close()

def preencheReconhecidos(mac,nomes):
    collection = database['postos']  
    result = collection.update_many( 
        {"mac":mac}, 
        { 
                "$set":{ 
                        "reconhecidos":nomes
                        }, 
                                 
                } 
        ) 
   
def preencheColaboradores(posto,ids):
    collection = database['postos']
  
    result = collection.update_many( 
        {"N":posto}, 
        { 
                "$set":{ 
                        "colaboradores":ids
                        }, 
                                 
                } 
        ) 
 


def saveEncodedFace(registro,encodedFace):
    collection = database['colaboradores']
  
    result = collection.update_many( 
        {"MATRÍCULA":registro}, 
        { 
                "$set":{ 
                        "FACE":encodedFace
                        }, 
                                 
                } 
        ) 
   

def getFaceFromMatricula(registro):
    collection = database['colaboradores']
    query = {}
    query["MATRÍCULA"] = registro  
    projection = {}
    projection["FACE"] = 1.0

    cursor = collection.find(query, projection = projection)
    if 'FACE' in cursor[0]:
        encodedFace = np.asarray(cursor[0]['FACE'])
    else:
        encodedFace = None
    return(encodedFace)

def getFacesFromIds(ids):
    encodedFaces =[]
    nomes = []
    for matricula in ids:
        face = getFaceFromMatricula(matricula)
        if face is not None:
            encodedFaces.append(face)
            nomes.append(getNameFromMatricula(matricula))
        #encodedFaces.append(
    return(nomes,encodedFaces)

def getNameFromMatricula(registro):
    collection = database['colaboradores']
    query = {}
    query["MATRÍCULA"] = registro

    projection = {}
    projection["NOME"] = 1.0

    cursor = collection.find(query, projection = projection)
    if 'NOME' in cursor[0]:
        Name = cursor[0]['NOME']
    else:
        Name = None
    return(Name)

def getNamesFromIds(ids):
    Names =[]
    for matricula in ids:
        Name = getNameFromMatricula(matricula)
        Names.append(Name) if Name is not None else None
        #encodedFaces.append(
    return(Names)
    
def getColaboradoresDoPosto(posto):
    collection = database['postos']
    ids = collection.find(
    { 
        "_id" : posto
    }, 
    { 
        "colaboradores" : 1.0
    }
    )
    return(ids)



def getWorkplaceInfo(args): 
    mac = args['mac']
    collection = database['postos']
    query = {}
    query["mac"] = mac
    workplaceInfo = collection.find(query)
    #return mac
    return workplaceInfo[0]


def getMatriculaFromName(args): 
    name = args['name']
    if name == "Desconhecido":
        return 0
    collection = database['colaboradores']
    matriculas = collection.find(
    { 
        "NOME" : name
    }, 
    { 
        "MATRÍCULA" : 1.0
    }
    )
    try:
        #print(matriculas[0])
        return matriculas[0]['MATRÍCULA'] if matriculas[0]['MATRÍCULA'] is not None else None
    except:        
        return None

def getIdsFromNames(names):
    collection = database['colaboradores']
    ids =[]
    for name in names:
        id = getMatriculaFromName(name)    
        try:    
            ids.append(id) if id is not None else None
        except:
            pass
        #encodedFaces.append(
    return(ids)
def processMissingSkills(skillsRequeridas,matricula):
    nivel = 2
    #skillsRequeridas =["ACABAMENTO"]
    skillsDisponiveis=[]
    skillsColaborador=[]
    missing = []
    query={}
    try:
        collection = database['colaboradores']                
        query["MATRÍCULA"] = matricula       
        queryResult = collection.find(query)[0]
        skillsDisponiveis = set(list(queryResult.keys())[8:-7])
        for skill in skillsDisponiveis:       
                #print(int(queryResult[skill]))
                try:
                    if int(queryResult[skill]) > nivel:
                        skillsColaborador.append(skill)
                except:
                    pass     
        skillsColaborador= set(skillsColaborador)
        for skill in skillsRequeridas:
            #print (skill)
            if skill not in skillsColaborador:
                #print(skill)
                missing.append(skill)
        
        #missing = skillsRequeridas.difference(skillsColaborador)     
        #print(missing)
        return missing  
    except:
        return(skillsRequeridas)           
        #print("\n")

def saveImageOnDatabase(wpInfo,image): 
    fs = gridfs.GridFS(database)   
    collection = database['linhas']  
    # convert ndarray to string
    imageString = image.tostring()

    # store the image
    imageID = fs.put(imageString, encoding='utf-8')

    # create our image meta data
    meta = {       
        
                'imageID': imageID,
                'shape': image.shape,
                'dtype': str(image.dtype)
            
        
    }
    query = {}
    query["cliente"] = wpInfo["cliente"]
    query["area"] = wpInfo["area"]
    query["linha"] = wpInfo["linha"]
    query["modelo"] = wpInfo["modelo"]

   
    collection.update(query, {'$push': {'desconhecidos': meta}})

def retrieveImage(wpInfo): 
        fs = gridfs.GridFS(database) 
        collection = database['linhas'] 
        query = {}
        query["cliente"] = wpInfo["cliente"]
        query["area"] = wpInfo["area"]
        query["linha"] = wpInfo["linha"]
        query["modelo"] = wpInfo["modelo"]
        image = collection.find_one(query)['desconhecidos'][0]   
        gOut = fs.get(image['imageID'])   
        img = np.frombuffer(gOut.read(), dtype=np.uint8)  
        img = np.reshape(img, image['shape'])
        return img














def getColaboradoresFromLinha(wpInfo):     
    collection = database["colaboradores"]

    query = {}
    query["AREA"] = wpInfo['area']
    query["CLIENTE"] = wpInfo['cliente']
    query["LINHA"] = wpInfo['linha']
    #print(query)
    colaboradores = []
    cursor = collection.find(query)
    #try:
    for doc in cursor:
        novoColaborador ={}    
        novoColaborador={
            'Nome':doc['NOME'],
            'Matricula':doc['MATRÍCULA']                            
            }
        if "FACE" in doc:
            novoColaborador['Face']=doc["FACE"]
        Habilidades = []
        for key in doc:   
            if doc[key] == '1' or doc[key] == '2' or doc[key] == '3' or doc[key] == '4' or doc[key] == '5':
                Habilidades.append(key)
        novoColaborador['Habilidades']=Habilidades
        colaboradores.append(novoColaborador)
    #except Exception as e: print(e)
    
    return colaboradores

def filtraComFace(colaboradores):
    colaboradoresComFace =[]
    for colaborador in colaboradores:        
        if 'Face' in colaborador:                
            colaboradoresComFace.append(colaborador)  
    return colaboradoresComFace    
 
def calculaMissing(colaboradores,requisitos):   
    i = 0
    for colaborador in colaboradores:        
        colaboradorSkills = set(colaborador['Habilidades'])
        colaborador.pop('Habilidades', None)
        missingSkills =[]
        for habilidadeRequsitada in requisitos:
            if habilidadeRequsitada not in colaboradorSkills:
                missingSkills.append(habilidadeRequsitada)
        colaborador['missingSkills'] = missingSkills
        colaboradores[i] = colaborador
        i+=1
    return colaboradores

def vetorizaColaboradores(colaboradores):    
    encodedFaces = []
    nomes =[]
    missingSkills =[]
    for colab in colaboradores:
        nomes.append(colab['Nome'])
        encodedFaces.append(colab['Face'])
        missingSkills.append(colab['missingSkills'])
    return (encodedFaces,nomes,missingSkills)


def getInformation(wpInfo):
    ColaboradoresFromLinha=getColaboradoresFromLinha(wpInfo)
    colaboradoresComFace=filtraComFace(ColaboradoresFromLinha)
    colaboradoresComFaceEMissingSkills=calculaMissing(colaboradoresComFace,wpInfo['requisitos'])
    encodedFaces,nomes,missingSkills = vetorizaColaboradores(colaboradoresComFaceEMissingSkills)
    return (encodedFaces,nomes,missingSkills)

def uplaodImage(img):
    addr = 'http://172.22.45.216:800'
    test_url = addr + '/api/upload'
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}   
    _, img_encoded = cv2.imencode('.jpg', img)
    response = requests.post(test_url, data=img_encoded.tostring(), headers=headers) 
    print(json.loads(response.text))
    
    
def regularizaPosto():     
    collection = database["postos"]
    query = {}
    cursor = collection.find(query)
    for doc in cursor:
        requisitos = doc['requisitos'].split(',')
        postoQueVaiSerEditadoQuery={}
        postoQueVaiSerEditadoQuery['_id'] = doc['_id']
        newvalues = { "$set": { "requisitos": requisitos} }
        collection.update_one(postoQueVaiSerEditadoQuery, newvalues) 
        print(doc)  
