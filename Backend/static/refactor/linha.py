from colaborador import colaborador
from database import database
from datetime import datetime


class linha():
    def __init__(self,parametros):
        self.colaboradores = []
        self.reconhecidos = []
        self.findColaboradores(parametros)

    def findColaboradores(self,parametros):       
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

    def findColabByMatricula(self,matriculaBuscada):
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
            print("a")

    
    #request by date { "date" : { $regex : /^08\/01\/2020/ }}
    def preencheReconhecidos(self,workplace):
        #Retirar Daqui, deve ficar na classe linha
        if len(self.reconhecidos)>0:
            collection = database['historico']
            now = datetime.now()
            today = now.strftime("%d-%m-%Y, %H:%M:%S")
            dict = {"Posto": workplace.posto,"date":today,"reconhecidos": self.reconhecidos} 
            result = collection.insert_one(dict)

        #collection = database['postos']
       # result = collection.update_many( 
         #   {"mac": mac},
            #{
      #              "$set": {
      #                      "reconhecidos": self.reconhecidos
     # #                      },
     #               }
       #                  )