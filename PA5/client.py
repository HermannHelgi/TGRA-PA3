import socket


class Client:

    def __init__(self, host = "localhost",port = 5555):
        self.network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.network.connect(self.addr)
        return self.network.recv(2048).decode()

    def send(self, data:str) -> str: 
        try:
            self.network.send(str.encode(data))
            reply = self.network.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
