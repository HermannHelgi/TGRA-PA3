import socket
from _thread import *
import json

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server = 'localhost'
port = 4123


try:
    s.bind((server,port))
except socket.error as e:
    print(str(e))



s.listen(2)
print("Waiting for a connection")
    
currentId = 0
game_state = {
    "PLAYERS" : {},
    "BULLETS" : []
}
clients_connected = {} #Key: (ip,port) : # value: "ID"

def parse_reply(reply:dict):
    global game_state
    if "PLAYER" in reply:
        game_state["PLAYERS"][reply["PLAYER"]["ID"]] = reply["PLAYER"]
    #if "BULLET" in reply:
        #game_state["BULLETS"].append(reply)
        #return reply["BULLET"]["ID"],"BULLET"




def threaded_client(conn,addr):
    global currentId, game_state
    conn.send(str.encode(str(currentId)))
    clients_connected[addr] = str(currentId)
    currentId += 1
    reply = ''
    while True:
        try:
            data = conn.recv(5000)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = json.loads(reply)
                print(reply)
                parse_reply(reply)

                
                print("Sending: game_state" )

            conn.sendall(str.encode(json.dumps(game_state)))

            #Let everyone know of a new bullet. then remove it
            while(len(game_state["BULLETS"]) >0):
                game_state["BULLETS"].pop()

        except:
            break
    
    game_state["PLAYERS"].pop(clients_connected[addr])
    clients_connected.pop(addr)
    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,addr))