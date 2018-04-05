#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from keyboard import *
from network import *
import sys
import pygame
import socket
import pickle
import select
import os

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)

################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if len(sys.argv) != 4:
    print("Usage: {} host port nickname".format(sys.argv[0]))
    sys.exit()
host = sys.argv[1]

'''
if not os.system("ping -c 1 " + host) is 0:
    print("Invalid host name or unreachable")
    sys.exit()
'''

def receive_map(model, socket):
    print("Receiving map ..."+"\n")
    socket.sendall(b"send_map")

    print("Receiving characters ...")
    characters = pickle.loads(socket.recv(1500))
    if not characters: characters_array = []
    else:
        characters_array = characters
    socket.send(b"ACK")
    print("characters: "+str(characters_array)+"\n")
    model.characters = characters

    print("Receiving fruits ...")
    fruits = pickle.loads(socket.recv(1500))
    if not fruits: fruits_array = []
    else:
        fruits_array = fruits
    socket.sendall(b"ACK")
    print("fruits: "+str(fruits_array)+"\n")
    model.fruits = fruits

    print("Receiving bombs ...")
    bombs = pickle.loads(socket.recv(1500))
    if not bombs: bombs_array = []
    else:
        bombs_array = bombs
    socket.send(b"ACK")
    print("bombs: "+str(bombs_array)+"\n")
    model.bombs = bombs
    
    print("Receiving players ...")
    players = pickle.loads(socket.recv(1500))
    print("players: "+str(players))
    if not players: players_array = []
    else:
        players_array = players
    socket.send(b"ACK")
    print("players: "+str(players_array)+"\n")
    model.player = players
    
    model.map.width = pickle.loads(socket.recv(1500))
    socket.send(b"ACK")
    model.map.height = pickle.loads(socket.recv(1500))
    socket.send(b"ACK")
    model.map.array = pickle.loads(socket.recv(1500))
    socket.send(b"ACK")
    print("setting received data to the map from the model")
    


def send_nickname(nick, socket):
    print("Send nickname to the server ..."+"\n")
    socket.sendall(b"sending_nick")
    socket.recv(1500)

    print("sending is value")
    socket.sendall(pickle.dumps(nick))
    socket.recv(1500)
    
port = int(sys.argv[2])
nickname = sys.argv[3]

# initialization
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)
s.connect((host, port))

pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()

model = Model()
#model.load_map(DEFAULT_MAP) # TODO: the map, fruits and players should be received from server by network.
send_nickname(nickname, s)
receive_map(model,s)

view = GraphicView(model, nickname)

client = NetworkClientController(model, host, port, nickname)
kb = KeyboardController(client)

# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    if not kb.tick(dt): break
    if not client.tick(dt): break
    model.tick(dt)
    view.tick(dt)

# quit
print("Game Over!")
pygame.quit()
