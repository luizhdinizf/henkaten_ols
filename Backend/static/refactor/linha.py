from colaborador import colaborador
from database import database
from datetime import datetime


class linha():
    def __init__(self):
        self.colaboradores = []        

    def queryParametros(self, area):
        collection = database["colaboradores"]
        query = {}
        query["AREA"] = area
        #query["CLIENTE"] = self.cliente
        #query["LINHA"] = self.linha
        cursor = collection.find(query)
        return cursor

    def findColaboradores(self, parametros):       
        for doc in parametros:
            novoColaborador = {}
            novoColaborador = colaborador()
            novoColaborador.name = doc['NOME']
            novoColaborador.matricula = doc['MATRÍCULA']
            if "FACE" in doc:
                novoColaborador.encodedFace = doc["FACE"]  #ou np.asarray(cursor[0]['FACE'])
            Habilidades = []
            for key in doc:
                if doc[key] == '1' or doc[key] == '2' or doc[key] == '3' or doc[key] == '4' or doc[key] == '5':
                    Habilidades.append(key)
            novoColaborador.skills = set(Habilidades)
            self.colaboradores.append(novoColaborador)

    def calculateAllMissingSkills(self, requisitos):
        for colab in self.colaboradores:
            colab.calculateMissingSkills(requisitos)

    def findColabByMatricula(self, matriculaBuscada):
        for colab in self.colaboradores:
            if colab.matricula == matriculaBuscada:
                return colab
        unknownColab = colaborador()
        unknownColab.name = "Desconhecido"
        return unknownColab

    def printNames(self):
        for colab in self.colaboradores:
           print("a")

    def printMissingSkills(self):
        for colab in self.colaboradores:
            print(colab.missingSkills)

    
   