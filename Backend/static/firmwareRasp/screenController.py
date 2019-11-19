import cv2


class recognizedFace():
    def __init__(self, id):
        self._id = id
        self.position = [20, 30, 50, 60]
        self.name = 4
        self.skills = 2

    def calculateMissingSkills(self, requiredSkills):
        self.missingSkills = requiredSkills - self._skills


class ScreenController():

    def __init__(self, frame, cliente, area, linha, hostname, requisitos, mac):
        self._frame = frame
        self._cliente = cliente
        self._area = area
        self._linha = linha
        self._hostname = hostname
        self._requisitos = requisitos
        self._mac = mac
        self._recognizedFaces = 2

    def preparaDisplay(self, wpInfo, recognizedFaces, encodedFaces, names, missingSkills):
        displayDict = {
            'frame': frame,
            'linha': {'key0': 'value0', 'key1': 'value1'},
            'ids': []}
        ids = []
        linha = {}
        linha['Cliente'] = ' '+wpInfo['cliente']
        linha['Area'] = ' '+wpInfo['area']
        linha['Linha'] = ' '+wpInfo['linha']
        for i, req in enumerate(wpInfo['requisitos']):
            linha[str(i)] = req

        displayDict['linha'] = linha

        for face in recognizedFaces:
            if face['index'] == -1:
                dictFromFace = {
                    'position': face['position'],
                    'name': str(face['index']),
                    'missingSkills': ['Desconhecido']
                }
            else:

                dictFromFace = {
                    'position': face['position'],
                    'name': names[face['index']],
                    'missingSkills': missingSkills[face['index']]
                }
            ids.append(dictFromFace)
        displayDict['ids'] = ids
        return displayDict

    def displayScreen(displayDict):
        frame = displayIds(frame, ids)
        frame = displayInfo(frame, linha)
        cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            "Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Video', frame)

    def displayInfo(self, infos):
        fontSize = 0.5
        letterSpacing = int(24*fontSize+1)
        fontColor = (0, 255, 0)  # bgr green
        left = 10
        top = 10
        font = 4

        cv2.putText(self._frame, self._hostname, (left, top+letterSpacing*1),
                    font, fontSize, fontColor, 1)
        cv2.putText(self._frame, self._mac, (left, top+letterSpacing*2),
                    font, fontSize, fontColor, 1)
        cv2.putText(self._frame, self._cliente, (left, top+letterSpacing*3),
                    font, fontSize, fontColor, 1)
        cv2.putText(self._frame, self._area, (left, top+letterSpacing*4),
                    font, fontSize, fontColor, 1)
        cv2.putText(self._frame, self._linha, (left, top+letterSpacing*5),
                    font, fontSize, fontColor, 1)
        cv2.putText(self._frame, self._mac, (left, top+letterSpacing*6),
                    font, fontSize, fontColor, 1)


    def displayIds(self, ids):
        for colaborador in ids:
            (top, right, bottom, left) = colaborador['position']
            top *= scale
            right *= scale
            bottom *= scale
            left *= scale
            if len(colaborador['missingSkills']) > 0:
                txtQualificado = "N Qualificado"
                borderColor = (0, 0, 255)  # bgr
                fontSize = 0.5
                letterSpacing = int(24*fontSize+1)
                i = 1
                fontColor = (0, 0, 255)  # bgr
                for skill in colaborador['missingSkills']:
                    cv2.putText(self._frame, skill, (right, top+letterSpacing*i),
                                font, fontSize, fontColor, 1)
                    i += 1
            else:
                txtQualificado = "Qualificado"
                borderColor = (0, 255, 0)  # bgr
            cv2.rectangle(self._frame, (left, top), (right, bottom), borderColor, 2)
            cv2.rectangle(self._frame, (left, bottom - 35),
                        (right, bottom), borderColor, cv2.FILLED)
            cv2.putText(self._frame, colaborador['name'], (left + 6,
                                                    bottom - 6), font, 1.0, (255, 255, 255), 1)
            cv2.putText(self._frame, txtQualificado, (left + 6, top - 6),
                        font, 0.8, borderColor, 1)
        
