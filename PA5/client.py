import socket

"""
This class is only taking care of the socket connection. No game logic is done here. 
"""
class Client:

    def __init__(self, host = "localhost",port = 4123):
        self.network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.buffer_size = 5000
        self.id = self.connect()

    def connect(self):
        self.network.connect(self.addr)
        return self.network.recv(self.buffer_size).decode()

    def send(self, data:str) -> str: 
        try:
            self.network.send(str.encode(data))
            reply = self.network.recv(self.buffer_size).decode()
            return reply
        except socket.error as e:
            return str(e)
