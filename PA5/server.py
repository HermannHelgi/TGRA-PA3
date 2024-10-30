import socket
from _thread import *


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server = 'localhost'
port = 5555


try:
    s.bind((server,port))
except socket.error as e:
    print(str(e))



s.listen(2)
print("Waiting for a connection")
    
currentId = 0
content = {
    "players" : [],
    "bullets" : []
}
def threaded_client(conn):
    global currentId, content
    conn.send(str.encode(str(currentId)))
    currentId += 1
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = arr[1]

                reply = "Hello: " + str(id) + "this is server responding."

                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))