# while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        #data = conn.recv(1024).decode()
        #if not data:
            # if data is not received break
        #    break
        #print("from connected user: " + str(data))
        #data = input(' -> ')
        #conn.send(data.encode())  # send data to the client
		
import LGymConnect as LGymC
import time


class LGymClient:
    def __init__(self, host, port, id):
        self.host = host
        self.port = port
        self.id = id
        self.lgconnectClinet = LGymC.LGymConnect(self.host,self.port,1,40960)

    def connect(self):
        self.lgconnectClinet.clientProgram()
        data = self.lgconnectClinet.clientRecive()
        if self._cheackReciveMsg(data,True):
            self.lgconnectClinet.clientSend("command=hello&id="+str(self.id )+"\r\n")
            data = self.lgconnectClinet.clientRecive()
            return self._cheackReciveMsg(data,True)
        return False

    
    def _cheackReciveMsg(self, data, commands):
        data = str(data).strip()
        if not data:
            print("Connection lost")
            return False
        elif data.startswith("error"):
            print("Error de conexión "+str(data))
            return False
        elif data != "ok":
            if data.startswith("command") and commands:
                print("Comando enviado fuera de tiempo, lo ignoramos "+str(data))
                return True
            else:
                print("Error de conexión "+str(data))
                return False
        return True
    
    def _precessingPerception(self, data):
        print("Mostrando la percepcion")
        print(data)
        attributes = self._ParseDataToAttributes(data)
        if len(attributes) > 0:
            if self.IsCommand("perception_map",attributes) :
                if "parameters" in attributes:
                    parametersAttr = attributes["parameters"]
                    parameters = self._parseArray(";",parametersAttr,"float")
                    map = attributes["map"]
                    map = self._parseArray(";",map,"int")
                    return parameters, attributes["gameover"] == "True", attributes["destroyed"] == "True", map
                else:
                    return False, attributes["gameover"] == "True", attributes["destroyed"] == "True", False
        return False, False, False, False
    
    def _processMetricsMsg(self, data):
        attributes = self._ParseDataToAttributes(data)
        if len(attributes) > 0:
            if self.IsCommand("metrics",attributes) :
                idsStr = attributes["ids"]
                timeStr = attributes["time"]
                checkpointStr = attributes["checkpoints"]
                collisionsStr = attributes["collisions"]
                ids = self._parseArray(";",idsStr,"string")
                time = self._parseArray(";",timeStr,"float")
                checkpoint = self._parseArray(";",checkpointStr,"int")
                collisions = self._parseArray(";",collisionsStr,"int")
                dictionary = {}
                dictionary["ids"]=ids
                dictionary["time"]=time
                dictionary["checkpoints"]=checkpoint
                dictionary["collisions"]=collisions
                return dictionary
        return False

    def _parseArray(self, token, arr, type):
        arrSplited = arr.split(token)
        for i in range(0,len(arrSplited)):
            if type == "int" :
                arrSplited[i] = int(arrSplited[i].strip())
            elif type == "float" :
                arrSplited[i] = arrSplited[i].replace(",",".")
                arrSplited[i] = float(arrSplited[i].strip())
            else:
                arrSplited[i] = arrSplited[i].strip()
        return arrSplited


    def IsCommand(self, comm, attributes):
        return attributes["command"] == comm

    
    def _ParseDataToAttributes(self,data):
        dictionary = { }
        data = str(data).strip()
        if data != "":
            attributes = data.split("&")
            for a in attributes:
                command=a.split("=")
                dictionary[command[0].strip()] = command[1].strip()
        return dictionary

    def commandInit(self):
        self.lgconnectClinet.clientSend("command=init&id="+str(self.id )+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data,True)
    
    def addCustomAgent(self,id,agent):
        self.lgconnectClinet.clientSend("command=addagent&id="+str(self.id )+"&format=custom&type=mlpc&agentid="+id+"&agent="+agent+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data,True)
    
    def commandReset(self):
        self.lgconnectClinet.clientSend("command=reset&id="+str(self.id )+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data,True)
    
    def SendAction(self, idsArr, actionArr):
        if len(idsArr) != len(actionArr):
            return
        p = ""
        for i in range(0,len(idsArr)-1):
            p += idsArr[i] + "=" + actionArr[i] + "&"
        p += idsArr[len(idsArr)-1] + "=" + actionArr[len(actionArr)-1]
        self.lgconnectClinet.clientSend("command=actions&id="+str(self.id )+"&"+p+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data,True)
    
    def RecivePerception(self):
        data = self.lgconnectClinet.clientRecive()
        perceptions, gameover, destroyed, map = self._precessingPerception(data)
        if not perceptions:
            self.lgconnectClinet.clientSend("error=01&name=bad format\r\n")
        else:
            self.lgconnectClinet.clientSend("ok\r\n")
        return perceptions, gameover, destroyed, map

    def ReciveMetrics(self):
        data = self.lgconnectClinet.clientRecive()
        dictionary = self._processMetricsMsg(data)
        if not dictionary:
            self.lgconnectClinet.clientSend("error=01&name=bad format\r\n")
        else:
            self.lgconnectClinet.clientSend("ok\r\n")
        return dictionary

    def close(self):
        self.lgconnectClinet.clientClose()
        

def agentLoop(agent, debug):
    print("LGymClientInit")
    client = LGymClient(LGymC.getHostName(),80,agent.Id())
    if client.connect():
        if debug : 
            print("conexion establecida con el servidor")
        agentName=agent.Name()
        if debug : 
            print("Añadiendo agentes")
        if client.addCustomAgent(agent.Id(),agentName):
            if debug : 
                print("Agent ",agent.Id()," añadido")
            if client.commandInit():
                if debug :
                    print("Inicializado")
                agent.Start()
                finish = False
                win = False
                while not finish:
                    if debug :
                        print("Esperando percepcion...")
                    perception, gameover, destroyed, map = client.RecivePerception()
                    if gameover == True:
                        finish = True
                        win = True
                        if debug :
                            print("Game over, hemos ganado")
                    elif destroyed == True:
                        finish = True
                        win = False
                        if debug :
                            print("El Agente ha sido destruido")
                    else:
                        if debug :
                            print("Percepcion recibida")
                        if debug :
                            print("Enviando acciones")
                        action, fire=agent.Update(perception,map)
                        fireStr = "1" if fire == True else "0"
                        if client.SendAction(["movement","fire"],[str(action),fireStr]) :
                            if debug :
                                print("Acciones enviadas")
                        else :
                            finish = True
                            if debug :
                                print("Error en el envio de acciones, salimos...")
                agent.End(win)
        if debug :
            print("Finalizado")
    client.close()
    if debug :
        print("LGymClientClose")	