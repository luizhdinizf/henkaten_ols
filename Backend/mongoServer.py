import numpy as np
import pandas as pd
from pymongo import MongoClient
import gridfs
import re

client = MongoClient("mongodb://mongo:27017/")
database = client["henkaten_ols"]


def importarCSVparaMongo():    
    df = pd.read_csv('/home/luiz/Projetos/colaboradores_utf.csv',encoding = 'utf-8')
    drops = (
    'ZENBARA','NECESSIDADE	REAL','DATA DE ADMISSÃO','VALIDADE DA OLS','EDIÇÃO',\
    'NOME','MATRÍCULA','AREA','CARGO','CLIENTE','LINHA','TURNO','NECESSIDADE','REAL')

    x=0
    for col in df.columns: 
        print(col)
        if col not in drops:
            collection.insert({'_id':x,'value':col})
            x+=1




def preencherLinhaAleatoriamente(cliente,area,linha,modelo):
    import random
    query = {}
    sort = [ ("value", 1) ]
    competencias = database["competencias"]
    cursor = competencias.find(query, sort = sort)

    competencias = []
    try:
        for doc in cursor:
            competencias.append(doc['value'])
    finally:
        client.close()
    for i in range(20):    
        x = [random.choice(competencias) for i in range(4)]
        postos.insert({'N':i,'cliente':cliente,'area':area,'linha':linha,'modelo':modelo,'requisitos':x,'colaboradores':[]})


def preencherPostos(postos,nivel):
    query = {}
    projection = {}
    projection["requisitos"] = 1.0
    cursor = postos.find({}, projection = projection)
    try:
        x=0
        for posto in cursor:    
            # print(doc)
                queryColaboradores = {}
                criterios=[]
                for requisito in posto['requisitos']:
                    criterio=  {
                        requisito : {
                            "$gt": str(nivel)
                    }
                    }
                    criterios.append(criterio)
                queryColaboradores["$and"]=criterios
                colaboradoresAptos = acharColaboradores(queryColaboradores,colaboradores)
                myquery = { "_id": posto['_id'] }
                newvalues = { "$set": { "colaboradores":colaboradoresAptos  } }
                postos.update_one(myquery, newvalues)
            
    finally:
        client.close()


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

def preencheReconhecidos(posto,ids):
    collection = database['postos']  
    result = collection.update_many( 
        {"N":posto}, 
        { 
                "$set":{ 
                        "reconhecidos":ids
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
    
def getColaboradoresDoPosto(args):
    try:
        collection = database['postos']
        posto = args['posto']
        ids = collection.find(
        { 
            "N" : posto
        }, 
        { 
            "reconhecidos" : 1.0
        }
        )
        reconhecidos = ids[0]['reconhecidos']
        collection = database['colaboradores']
        
        ids = collection.find(
        { 
            "MATRÍCULA" : reconhecidos[0]
        } 
    
        )
        #http://brmtz-dev-001:800/api/getColaboradoresDoPosto?posto=0
        retorno = ids[0]
    except:
        retorno="0"
    return(retorno)


def get_postos(args):
    collection = database['postos']
    query = {}
    workplaceInfo = collection.find(query)
    return workplaceInfo[:]


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

def retrieveLogged(date):
        from bson.json_util import dumps
        regx = re.compile("^"+date['date'], re.IGNORECASE)
   # { "date" : { $regex : /^08\/01\/2020/ }}
        collection = database["historico"]
        query = {}
        query["date"] = regx
        #query["CLIENTE"] = self.cliente
        #query["LINHA"] = self.linha
        cursor = collection.find(query)
        ret =[]
        for doc in cursor:
            ret.append(doc)
        return (ret)


def find_matriculas():
    collection = database["colaboradores"]
    query = {}
    cursor = collection.find(query)
    matriculas =[]
    for doc in cursor:
        if "FACE" not in doc:
            matriculas.append(doc['MATRÍCULA'])
    return matriculas