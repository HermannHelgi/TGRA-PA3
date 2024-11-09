import socket
from _thread import *
import json

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)



server = 'localhost'
port = int(input("Please provide a port to host on: "))


try:
    s.bind((server,port))
except socket.error as e:
    print(str(e))



s.listen(2)
print("Waiting for a connection")
    
currentId = 0
game_state = {
    "PLAYERS" : {},
    "BULLETS" : {}
}
clients_connected = {} #Key: (ip,port) : # value: "ID"

def parse_reply(reply:dict):
    global game_state
    if "PLAYER" in reply:
        game_state["PLAYERS"][reply["PLAYER"]["ID"]] = reply["PLAYER"]
    if "BULLET" in reply:
        game_state["BULLETS"][reply["BULLET"]["ID"]] = reply["BULLET"]




def threaded_client(conn,addr):
    global currentId, game_state
    conn.send(str.encode(str(currentId)))
    clients_connected[addr] = str(currentId)
    currentId += 1
    reply = ''
    while True:
        try:
            data = conn.recv(50000)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = json.loads(reply)
                parse_reply(reply)

                
                print("Sending: game_state" )
                print(game_state)
            conn.sendall(str.encode(json.dumps(game_state)))


        except:
            break
    
    game_state["PLAYERS"].pop(clients_connected[addr])
    if clients_connected[addr] in game_state["BULLETS"]:
        game_state["BULLETS"].pop(clients_connected[addr])
    clients_connected.pop(addr)
    print(addr , " has disconected. closing connection.")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,addr))