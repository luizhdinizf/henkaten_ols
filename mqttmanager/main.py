import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mac
    print(mac)
    client.connected_flag=True
    client.subscribe(mac+"/#")
    client.subscribe("$connected/#")
    client.subscribe("broadcast/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
 

    mensagem_str = str(msg.payload.decode("utf-8"))
    mensagem = json.loads(mensagem_str)
    command = mensagem["command"]
    print(msg.topic)
    print(mensagem)
    if command == "reset":
        print("RESETANDO")
        main1.restart()
    elif command == "login":
        try:
            subprocess.call("./.killChromium.sh")
        except:
            pass
        print("Logando")
        main1.logar = True
        
    elif command == "logout":
        mat = mensagem["matricula"]
        if mat == "all":
            main1.workplace.removerLogados()
            main1.registraEvento("logoutGeral", " ")
        else:
            colab = main1.linha.findColabByMatricula(mat)
            print(colab.name)
            print(colab in main1.workplace.logados)
            if colab in main1.workplace.logados:
                main1.registraEvento("logout", colab.name)
                main1.workplace.removerLogado(colab.matricula)
                main1.logar = True
                

    elif command == "cadastrar":
        try:
            subprocess.call("./.killChromium.sh")
        except:
            pass
        main1.saveNextFace = True

    elif command == "reboot":
