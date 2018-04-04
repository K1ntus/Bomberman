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
if not os.system("ping -c 1 " + host) is 0:
    print("Invalid host name or unreachable")
    sys.exit()

def receive_map(model, socket):
    print("Receiving map ...")
    
    socket.send("give_characters".encode())
    characters = socket.recv(1500)
    print("map characters: "+str(characters))
    if characters == b'':
        characters = []
            
    socket.send("give_fruits".encode())
    fruits = socket.recv(1500)
    print("map fruits: "+str(fruits))
    if fruits == b'':
        fruits = []
    
    socket.send("give_bombs".encode())
    bombs = socket.recv(1500)
    print("map bombs: "+str(bombs))
    if bombs == b'':
        bombs = []
    
    socket.send("give_players".encode())
    players = socket.recv(1500)
    print("map players: "+str(players))
    
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
