from database import database
from datetime import datetime
class workplace():
    def __init__(self):
        self.processo = ""
        self.posto = ""
        self.atividades = []
        self.requisitos = set([])
        self.area = ""
        self.cliente = ""
        self.linha = ""
        self.modelo = ""
        self.logados = set()

    def getInfo(self,mac):
        collection = database['postos']
        query = {}
        query["mac"] = mac
        workplaceInfo = collection.find(query)[0]
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
        self.preencheReconhecidos()

    def removerLogado(self, matricula):
        for colab in self.logados:
            if colab.matricula == matricula:
                self.logados.discard(colab)


   

     #request by date { "date" : { $regex : /^08\/01\/2020/ }}
    def preencheReconhecidos(self):        
        if len(self.logados) > 0:
            collection = database['historico']
            now = datetime.now()
            today = now.strftime("%d-%m-%Y, %H:%M:%S")
            for colab in self.logados:
                dict = {"Posto": self.posto,"date":today,"reconhecidos": colab.name} 
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