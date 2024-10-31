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
    "PLAYERS" : [],
    "BULLETS" : []
}

def parse_reply(reply:dict):
    global game_state
    if "PLAYER" in reply:
        if len(game_state["PLAYERS"]) < int(reply["PLAYER"]["ID"])+1: #First time player says its position
            game_state["PLAYERS"].append(reply["PLAYER"])
        else:
            game_state["PLAYERS"][int(reply["PLAYER"]["ID"])] = reply["PLAYER"]


def threaded_client(conn):
    global currentId, game_state
    conn.send(str.encode(str(currentId)))
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
                parse_reply(reply)


                print("Sending: game_state" )

            conn.sendall(str.encode(json.dumps(game_state)))
        except:
            break

    #TODO remove the player from game_state
    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))