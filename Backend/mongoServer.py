import numpy as np
import pandas as pd
from pymongo import MongoClient
import gridfs
import re
import paho.mqtt.client as mqtt

client = MongoClient("mongodb://mongo:27017/")
database = client["henkaten_ols"]

mqttclient = mqtt.Client()
mqttclient.connect("mqtt", 1883, 60)
mqttclient.loop_start()

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
    from bson.objectid import ObjectId
    collection = database['postos']
    thing = collection.find_one({'_id': ObjectId(args['id']) })
    return thing


def getColaboradorFromMatricula(args):
    matricula = args['matricula']
    collection = database['colaboradores']
    data = collection.find_one({'MATRÍCULA': matricula})
    return data

def mqttMessage(args):
    mqttclient.publish(args['topic'],args['payload'])
    return "ok"
def mqttCommand(args):
    from bson.json_util import dumps
    payload = {}
    payload['command'] = args['command']
    payload['matricula']=args['dado']
    topic= args['topic']
    payload = dumps(payload)
    
    mqttclient.publish(topic,payload)
    return "ok"


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