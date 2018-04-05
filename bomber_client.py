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

def receive_map(model, socket): #recepteur, ie server
    print("Receiving map ...")

    #print("Receiving characters ...")
    characters = socket.recv(1500)
    if not characters: characters_array = []
    else:
        characters_array = pickle.loads(characters)
    #socket.send(b"ACK")
    print("Characters: "+str(characters_array))

    print("Receiving fruits ...")
    fruits = socket.recv(1500)
    if not fruits: fruits_array = []
    else:
        fruits_array = pickle.loads(fruits)
    #socket.sendall(b"ACK")
    print("fruits: "+str(fruits_array))

    print("Receiving bombs ...")
    bombs = socket.recv(1500)
    if not bombs: bombs_array = []
    else:
        bombs_array = pickle.loads(bombs)
    #socket.send(b"ACK")
    print("bombs: "+str(bombs_array))

    print("Receiving players ...")
    players = socket.recv(1500)
    if not players: players_array = []
    else:
        players_array = pickle.loads(players)
    #socket.send(b"ACK")
    print("players: "+str(players_array))
            
    
    model.characters = characters.decode()
    model.fruits = fruits.decode()
    model.bombs = bombs.decode()
    model.player = players.decode()
    
port = int(sys.argv[2])
nickname = sys.argv[3]

# initialization
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)
s.connect((host, port))

pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()

model = Model()
model.load_map(DEFAULT_MAP) # TODO: the map, fruits and players should be received from server by network.
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
