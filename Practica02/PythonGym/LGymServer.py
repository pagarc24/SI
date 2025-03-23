import LGymConnect as LGymC

def serverCommands(data):
	if data == "hello":
		return "Hollo I' LGymServer"
	elif data == "goodby":
		return "Bye!"
	return "error"

print("LGymServerInit")	
lgconnectClinet = LGymC.LGymConnect(LGymC.getHostName(),80,1,4096)
lgconnectClinet.serverProgram(serverCommands)
print("LGymServer Close")