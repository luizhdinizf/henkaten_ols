from colaborador import colaborador
from database import database


class linha():
    def __init__(self, area, cliente, linha):
        self.colaboradores = []
        self.area = area
        self.cliente = cliente
        self.linha = linha
        self.findColaboradores()

    def findColaboradores(self):
        collection = database["colaboradores"]
        query = {}
        query["AREA"] = self.area
        #query["CLIENTE"] = self.cliente
        #query["LINHA"] = self.linha
        cursor = collection.find(query)
        for doc in cursor:
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

    def calculateAllMissingSkills(self, workplace):
        for colab in self.colaboradores:
            colab.calculateMissingSkills(workplace.requisitos)



    def printNames(self):
        for colab in self.colaboradores:
            print(colab.name)

    def printMissingSkills(self):
        for colab in self.colaboradores:
            print(colab.missingSkills)