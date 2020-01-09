import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mac
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mac+"/#")
    client.subscribe("broadcast/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        global main1
    except:
        pass
    #print(msg.topic+" "+str(msg.payload))
    mensagem = str(msg.payload.decode("utf-8"))
  
    print(msg.topic+" "+mensagem)
    if mensagem == "reset":
        print("RESETANDO")
        try:
            main1.restartParams()
        except:
            pass
       # 
    elif mensagem == "cadastrar":
        try:
            main1.saveNextFace = True
        except:
            pass
        
    elif mensagem == "reboot":
        print("try to reboot")
        print(os.system("reboot"))

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256', ifname[:15])
    )[20:24])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("brmtz-dev-001", 1883, 60)
client.loop_start()
