import time

from flask import Flask
from mongoCli import *
import json
import sys


app = Flask(__name__)



def get_hit_count():
    while True:
        
        
        try:
            return 2
        except:
            return 5


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
