class colaborador():
    def __init__(self):
        self.matricula = "-1"
        self.facePosition = [20, 30, 200, 300] #(top, right, bottom, left)
        self.faceImage = []
        self.name = ""
        self.skills = set([])
        self.missingSkills = []
        self.qualificado = False
        self.txtQualificado = 'N Qualificado'
        self.borderColor = (0, 0, 255) #bgr
        self.encodedFace = []

    def updateFaceImage(self, frame):
        (bottom, right, top, left) = self.facePosition
        self.faceImage = frame[bottom:top, left:right]

    def calculateMissingSkills(self, requiredSkills):
        self.missingSkills = requiredSkills - self.skills
        if len(self.missingSkills) > 0:
            self.setQuailificado(False)
        else:
            self.setQuailificado(True)

    def setQuailificado(self,qualificadoStatus):
        self.qualificado = qualificadoStatus
        if self.qualificado:
            self.txtQualificado = 'Qualificado'
            self.borderColor = (0, 255, 0)
        else:
            self.txtQualificado = 'N Qualificado'
            self.borderColor = (0, 0, 255)