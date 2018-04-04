#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from network import *
import sys
import pygame
import socket
import select

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)


################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if len(sys.argv) == 2:
    port = int(sys.argv[1])
    map_file = DEFAULT_MAP
elif len(sys.argv) == 3:
    port = int(sys.argv[1])
    map_file = sys.argv[2]
else:
    print("Usage: {} port [map_file]".format(sys.argv[0]))
    sys.exit()


def remove_socket(socket_list,socket):
    socket_list.remove(socket)          #remove the socket from the list
    socket.close()                      #close the socket


def send_map(model, socket):
    print("envoie de la map a la socket "+socket)
    socket.send(model.characters.encode())
    print("characters "+model.characters)
    socket.send(model.fruits.encode())
    print("fruits "+model.fruits)
    socket.send(model.bombs.encode())
    print("bombs "+model.bombs)
    socket.send(model.player.encode())
    print("players "+model.player)
    
# initialization
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)    #define the socket, putting it IPv6, TCP, etc
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  #bypass some -security- like port already used
s.bind(('',port))   #bind the socket to the port 7777
s.listen(1)         #put the socket on listen mode
socket_list=[s]     #init the socket list with the listening one
(ip,a,b,c) = s.getsockname()



pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
model = Model()
model.load_map(map_file)
for _ in range(10): model.add_fruit()
server = NetworkServerController(model, port)





# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    server.tick(dt)
    model.tick(dt)
    # view.tick(dt)
    
    (readable_socket, a,b) = select.select(socket_list, [],[])  #Work like a crossroad
    for i in readable_socket:   #for each socket on the list
        
        if i == s:  #if the socket is the listening one
            (con,addr)=i.accept()               #we get the information (ie. socket and address) and accept his connection request
            socket_list.append(con)             #we had the socket to the socket list
            (socket_ip,a,b,c)=i.getsockname()
        
        else:   #else we get the data
            data = i.recv(1500) #We receive the data of a length of 1500Bytes
            print(data.decode())
            if not data or data == '\n' or data == b'':    #if the data formatting is like nothing, or user closed the service
                j = remove_socket(socket_list,i)
            try:
                if data.decode() == "give_characters":
                    print("model characters = "+ str(model.characters))
                    s.send(model.characters.encode())
                if data.decode() == "give_fruits":
                    s.send(model.fruits.encode())
                if data.decode() == "give_bombs":
                    s.send(model.bombs.encode())
                if data.decode() == "give_players":
                    s.send(model.player.encode())
            except IndexError:
                eof=True
            except AttributeError:
                eof=True


# quit
print("Game Over!")
pygame.quit()
