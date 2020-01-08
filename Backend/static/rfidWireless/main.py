import serial
import requests
ultimo = ""
while 1:
    try:
        with serial.Serial("/dev/ttyACM0",19200,timeout=1) as ser:
            line=ser.readline().decode()[:-1]
            if line != "" and line != ultimo:
                ultimo = line
                url= "http://brmtz-dev-001:1880/escreve?codigo="+line
                r = requests.get(url)
                print(r.text)
    except Exception as e: print(e)
