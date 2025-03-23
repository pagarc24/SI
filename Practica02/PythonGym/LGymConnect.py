import socket

def getHostName():
	server_socket = socket.socket()
	return socket.gethostname()
		
class LGymConnect:
	# get the hostname
	# host = socket.gethostname()
	# port = 5000  # initiate port no above 1024
	
	def __init__(self, host, port, numListen, bufferSize):
		self.port = port
		self.numListen = numListen
		self.host = host
		self.bufferSide = bufferSize #1024
	
	
	
	def serverProgram(self,GetData):
		server_socket = socket.socket()  # get instance
		# look closely. The bind() function takes tuple as argument
		server_socket.bind((self.host, self.port))  # bind host address and port together

		# configure how many client the server can listen simultaneously
		server_socket.listen(self.numListen)
		conn, address = server_socket.accept()  # accept new connection
		print("Connection from: " + str(address))
		conectionError = False
		while not conectionError:
			# receive data stream. it won't accept data packet greater than 1024 bytes
			data = conn.recv(self.bufferSide).decode("UTF-8")
			if not data:
				# if data is not received break
				conectionError = True
			print("from connected user: " + str(data))
			data = GetData(data) #input(' -> ')
			if data == "Bye!":
				conectionError = True
			conn.send(data.encode("UTF-8"))  # send data to the client

		conn.close()  # close the connection
		
	def clientProgram(self):
		#host = socket.gethostname()  # as both code is running on same pc
		#port = 5000  # socket server port number

		client_socket = socket.socket()  # instantiate
		client_socket.connect((self.host, self.port))  # connect to the server
		self.client_socket = client_socket;
		
		
	def clientSend(self,message):
		self.client_socket.send(message.encode("UTF-8"))
		
	def clientRecive(self):
		data = self.client_socket.recv(self.bufferSide).decode("UTF-8")  # receive response
		return data
		
	def clientClose(self):
		self.client_socket.close()
