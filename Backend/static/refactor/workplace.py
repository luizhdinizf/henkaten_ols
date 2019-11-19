from colaborador import colaborador
from database import *
class workplace():
    def __init__(self,mac):
        self.processo = ""
        self.posto = ""
        self.atividades = []
        self.requisitos = set([])
        self.area = ""
        self.cliente = ""
        self.linha = ""
        self.modelo = ""
        self.reconhecidos = ""
        self.mac = mac
        self.getInfo()

    def getInfo(self):
        collection = database['postos']
        query = {}
        query["mac"] = self.mac
        workplaceInfo = collection.find(query)[0]
        print(workplaceInfo)
        self.processo = workplaceInfo["Processo"]
        self.posto = workplaceInfo["Posto"]
        self.atividades = workplaceInfo["Atividades"]
        self.requisitos = set(workplaceInfo["requisitos"])
        self.area = workplaceInfo["area"]
        self.cliente = workplaceInfo["cliente"]
        self.linha = workplaceInfo["linha"]
        self.modelo = workplaceInfo["modelo"]
        self.reconhecidos = workplaceInfo["reconhecidos"]