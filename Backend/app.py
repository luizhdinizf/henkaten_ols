import time
import cv2
import jsonpickle
import numpy as np
import random
from flask import Flask, render_template, flash, request,Response
from mongoCli import *
import json
import sys
import numpy as np



app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'


def get_hit_count():
    while True:
        
        
        try:
            return 2
        except:
            return 5

@app.route('/api/upload', methods=['POST'])
def test():
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite('img.jpg',img)
    # do some fancy processing here....

    # build a response dict to send back to client
    response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
                }
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")
@app.route('/')
def hello():
    count = get_hit_count()
    workplaceInfo = getWorkplaceInfo('0x87fdb4b8ca2d')['colaboradores']
    print(workplaceInfo, file=sys.stderr)

    return 'Hello World! I have been seen ' + workplaceInfo[0]
#print()
print("run2")
if __name__ == "__main__":
    app.run(host='0.0.0.0')
