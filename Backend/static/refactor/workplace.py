from database import database
from datetime import datetime
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
        self.logados = set()
        self.mac = mac
        self.atualizaPosto()

    def getInfo(self):
        collection = database['postos']
        query = {}
        query["mac"] = self.mac
        print(self.mac)
        try:
            workplaceInfo = collection.find_one(query)
        except:
            pass
        self.processo = workplaceInfo["Processo"]
        self.posto = workplaceInfo["Posto"]
        self.atividades = workplaceInfo["Atividades"]
        self.requisitos = set(workplaceInfo["requisitos"])
        self.area = workplaceInfo["area"]
        self.cliente = workplaceInfo["cliente"]
        self.linha = workplaceInfo["linha"]
        self.modelo = workplaceInfo["modelo"]

    def removerLogados(self):
        self.logados = set()
        self.atualizaPosto()

    def removerLogado(self, matricula):
        for colab in self.logados:
            if colab.matricula == matricula:
                self.logados.discard(colab)
                self.atualizaPosto()

    def addLogado(self,colab):
        self.logados.add(colab)
        self.atualizaPosto()

    def atualizaPosto(self):
        print(self.logados)
        collection = database['postos']
        matriculas = [colab.matricula for colab in self.logados]
        query = {}
        query['mac'] = self.mac
        action = {
            "$set": {
                        "logados": list(matriculas)
                    },
        }
        collection.update_many(query, action)