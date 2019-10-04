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
from bson import ObjectId
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
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])    
    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form) 
        scanResult = scanStaticFolder()
        if len(scanResult) > 0:
            return render_template('index.html', form=form,img=scanResult)
        else:
            return("Sem imagens para Cadastrar")



@app.route('/api/<function>',methods=['GET', 'POST'])
def api(function):   
    mod = importlib.import_module('mongoServer')
    func = getattr(mod, function)
    result = func(request.args)  
    response = JSONEncoder().encode(result)
    return response

@app.route('/img/<id>', methods=['GET', 'POST'])
def image(id):     
    return render_template('img.html',img=id+'.jpg')
   
@app.route('/rename/<source>', methods=['GET', 'POST'])
def rename(source):     
    registro=request.form['matricula']   
    src="static/upload/desconhecido/"+source
    frame = cv2.imread(src)
    recognizedLocations = face_recognition.face_locations(frame)
    encodedFaces = face_recognition.face_encodings(frame, recognizedLocations)
    #return(str(len(encodedFaces)))
    saveEncodedFace(registro,list(encodedFaces[0]))
    dest="static/upload/"+registro+".jpg"
    shutil.move(src, dest)
    return redirect("/", code=301)

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
    app.run(host='0.0.0.0')
