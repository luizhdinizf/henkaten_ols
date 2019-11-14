import uuid
import subprocess
from pymongo import MongoClient
client = MongoClient("mongodb://brmtz-dev-001:27017/")
database = client["henkaten_ols"]

def getWorkplaceInfo(args): 
    mac = args['mac']
    collection = database['postos']
    query = {}
    query["mac"] = mac
    workplaceInfo = collection.find(query)
    #return mac
    return workplaceInfo[0]

mac = hex(uuid.getnode())
print(mac)
wpInfo=getWorkplaceInfo({'mac':mac})
hostname = wpInfo['cliente'] +'_' +wpInfo['linha']+'_'+wpInfo['Posto']
hostname = hostname.replace(" ", "_")
hostname = hostname.replace("_", "")
print(hostname) #NissanMainDirec1
proc = subprocess.Popen(['sudo','./hostnameSet.sh',hostname])

#subprocess.call(['hostname', hostname])
print("Finalizado")
