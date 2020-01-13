#from mongoCli import *
import importlib
import face_recognition
from flask import make_response
from mongoServer import *
import cv2
import jsonpickle
import numpy as np
import random
from flask import Flask, render_template, flash, request,make_response, url_for,Response,redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import jsonify
from flask_cors import CORS
from bson import ObjectId
from bson.json_util import dumps
import sys
import json
import os
import shutil
import uuid



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
    
def scanStaticFolder():
    result =[]
    try:
        for root, dirs, files in os.walk("static/upload/desconhecido"):
            result = files[0]
            return result
    except:
        return result



# App config.

DEBUG = True
app = Flask(__name__)
CORS(app)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])    
    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form) 
        scanResult = scanStaticFolder()
        try:
            if len(scanResult) > 0:
                return render_template('index.html', form=form,img=scanResult)
            else:
                return("Sem imagens para Cadastrar")
        except:
            return("Sem imagens para Cadastrar ERRO!")


@app.route('/api/<function>',methods=['GET', 'POST'])
def api(function):   
    mod = importlib.import_module('mongoServer')
    func = getattr(mod, function)
    result = func(request.args)  
    
    response = dumps(result)
    return response

@app.route('/img/<id>', methods=['GET', 'POST'])
def image(id):     
    return render_template('img.html',img=id+'.jpg')


@app.route('/fill', methods=['GET'])
def fillFaces():
    try:
        stringReturn = ""
        for i in range(10):
            matriculas = find_matriculas()
            for root, dirs, files in os.walk("static/upload/templateSet"):
                for picture in files:
                    matricula = matriculas.pop()
                    stringReturn += matricula
                    stringReturn += "</br>"
                    src = "static/upload/templateSet/"+picture
                    frame = cv2.imread(src)
                    recognizedLocations = face_recognition.face_locations(frame)
                    encodedFaces = face_recognition.face_encodings(frame, recognizedLocations)
                    saveEncodedFace(matricula, list(encodedFaces[0]))
                    dest="static/upload/moved/" + matricula + ".jpg"
                   # shutil.move(src, dest)
        return stringReturn
    except Exception as e:
        return str(e)

@app.route('/fill2', methods=['GET'])
def fillFaces2():
    stringReturn = "Resultado:"
    matriculas = find_matriculas()
    for root, dirs, files in os.walk("static/upload/fotosccp"):
        for picture in files:
            try:
                matricula = picture[:-4]            
                src = "static/upload/fotosccp/"+picture
                frame = cv2.imread(src)
                recognizedLocations = face_recognition.face_locations(frame)
                encodedFaces = face_recognition.face_encodings(frame, recognizedLocations)
                saveEncodedFace(matricula, list(encodedFaces[0]))
                dest="static/upload/moved2/" + matricula + ".jpg"
                shutil.move(src, dest)
            except Exception as e:
                stringReturn += str(e)
                stringReturn +="</br>"
            # shutil.move(src, dest)
    return stringReturn
        

@app.route('/rename/<source>', methods=['GET', 'POST'])
def rename(source):
    registro = request.form['matricula']   
    src = "static/upload/desconhecido/"+source
    frame = cv2.imread(src)
    recognizedLocations = face_recognition.face_locations(frame)
    encodedFaces = face_recognition.face_encodings(frame, recognizedLocations)
    #return(str(len(encodedFaces)))
    saveEncodedFace(registro, list(encodedFaces[0]))
    dest="static/upload/" + registro + ".jpg"
    shutil.move(src, dest)
    return redirect("http://brmtz-dev-001:800", code=301)

@app.route('/remove/<source>', methods=['GET', 'POST'])
def remove(source):    
    
    src="static/upload/desconhecido/"+source   
    os.remove(src)
    return redirect("/", code=301)




@app.route('/api/clear', methods=['GET'])
def clearMain():
    collection = database['colaboradores'] 
    #frame = cv2.imread("static/upload/desconhecido/1341.jpg")  
   # recognizedLocations = face_recognition.face_locations(frame)
  #  encodedFaces = face_recognition.face_encodings(frame, recognizedLocations)
  #  enco = list(encodedFaces[0])
    result = collection.update_many( 
        {},
#        {"LINHA":"Main"}, 
        { 
                "$set":{ 
                        "FACE":"0"
                        }, 
                                 
                } 
        ) 
    return "Sucess"

@app.route('/retrieveLogged', methods=['GET'])
def loggeed():
     return render_template('logged.html')


@app.route('/api/upload', methods=['POST'])
def test2():
    id = str(random.randint(1000,9999))
    r = request
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite('static/upload/desconhecido/'+id+'.jpg',img)
    response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/teste', methods=['POST'])
def test():   
    r = request  

    return r.data

if __name__ == '__main__':
    app.run(host='0.0.0.0',ssl_context=('cert.pem', 'key.pem'))
