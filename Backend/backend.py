from mongoExample import *
from flask import make_response
import cv2
from flask import Flask, render_template, flash, request,make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

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
    
        print (form.errors)
        if request.method == 'POST':
            name=request.form['name']
            print (name)
    
        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('All the form fields are required. ')
    
        return render_template('hello.html', form=form)



@app.route('/recognition/<name>')
def hello_name(name):
    workplaceInfo = getWorkplaceInfo(name)
    output_img = retrieveImage(workplaceInfo)
    retval, buffer = cv2.imencode('.png', output_img)
    response = make_response(buffer.tobytes())
    response.headers['Content-Type'] = 'image/png'
    return response

if __name__ == '__main__':
    app.run()