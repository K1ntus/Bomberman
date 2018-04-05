#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from network import *
import sys
import pygame
import random
import socket
import pickle #send array over sockets
import select
import errno

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


def delete_player(socket):
    try:
        (ip,a,b,c) = socket.getsockname()
        nick_to_remove = nick_dictionnary[ip]
        for i in nick_dictionnary:
            if i == nick_to_remove:
                kill_character(nick_to_kill)
                nick_dictionnary.pop(i)
#                model.characters.remove(
    except:
        print("No such key to remove (nickname on leave)")
        pass

def remove_socket(socket_list,socket):
    socket_list.remove(socket)          #remove the socket from the list
    socket.close()                      #close the socket

def disconnect(socket_list, socket):
    (ip,a,b,c) = socket.getsockname()
    nick_to_remove = nick_dictionnary[ip]
    model.quit(nick_to_remove)
    
    delete_player(socket)
    remove_socket(socket_list, socket)
    
def adding_new_nick(model, socket):
    socket.send(b"ACK")
    (ip,a,b,c)=socket.getsockname()  
    nick_wanted=pickle.loads(socket.recv(1500))#attribute the nick parameters to this ip
    socket.send(b"ACK")
    
    new_nick_wanted = nick_wanted
    i=0
    while not model.look(new_nick_wanted) == None:
        new_nick_wanted = nick_wanted+str(i)
        i=i+1
    nick_dictionnary[ip] = new_nick_wanted
    model.add_character(nick_dictionnary[ip], True)
        

def receive_player_movement(model, socket):
    print("sending ack packet")
    socket.send(b"ACK")
    print("ack packet received from remote host")

    (ip,a,b,c) = socket.getsockname()
    username = nick_dictionnary[ip]
    
    movement = socket.recv(1500)#attribute the nick parameters to this ip
    socket.send(b"ACK")
    print("I received the order to move to: "+ movement.decode())
    model.move_character(username, int(movement.decode()))
    
    
            

def send_map(model, socket):
    
    #print("Envoie des caractères")
    characters_to_send = pickle.dumps(model.characters)
    socket.sendall(characters_to_send)
    
    socket.recv(1500)
    #print("Envoie des fruit")
    fruits_to_send = pickle.dumps(model.fruits)
    socket.sendall(fruits_to_send)

    socket.recv(1500)
    #print("Envoie des position de bombes")
    bombs_to_send = pickle.dumps(model.bombs)
    socket.sendall(bombs_to_send)
    
    socket.recv(1500)
    #print("Envoie des player_to_send ")
    player_to_send = pickle.dumps(model.player)
    socket.sendall(player_to_send)
    
    socket.recv(1500)
    #print("Envoie des data de la map")
    map_width = pickle.dumps(model.map.width)
    socket.sendall(map_width)
    
    socket.recv(1500)
    map_height = pickle.dumps(model.map.height)
    socket.sendall(map_height)
    
    socket.recv(1500)
    map_array_to_send = pickle.dumps(model.map.array)
    socket.sendall(map_array_to_send)
    
    socket.recv(1500)
    

# initialization
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)    #define the socket, putting it IPv6, TCP, etc
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  #bypass some -security- like port already used
s.bind(("",port))   #bind the socket to the port 7777
s.listen(1)         #put the socket on listen mode
socket_list=[s]     #init the socket list with the listening one
(ip,a,b,c) = s.getsockname()
s.settimeout(0.0)


nick_dictionnary={ip:"server"}

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
    #print("socket list : "+ str(socket_list) )
    for i in readable_socket:   #for each socket on the list
        if i == s:  #if the socket is the listening one
            (con,addr)=i.accept()               #we get the information (ie. socket and address) and accept his connection request
            socket_list.append(con)             #we had the socket to the socket list
            (socket_ip,a,b,c)=i.getsockname()        
        else:   #else we get the data
            data = i.recv(1500) #We receive the data of a length of 1500Bytes
            print("Data: " + str(data))
            if not data or data == '\n' or data == b'':
                disconnect(socket_list, i)
            try:
                if data == b"sending_nick":
                    adding_new_nick(model, i)
                    if not(nick_dictionnary[socket_ip] == "server"):
                        model.add_character(nick_dictionnary[socket_ip], True)
                #elif data == b"send_map":
                    #i.sendall(model.characters.encode()+"\n"+model.fruits.encode()+"\n"+model.bombs.encode()+"\n"+model.player.encode())
                send_map(model, i)
                if data == b"moving":
                    #i.sendall(model.characters.encode()+"\n"+model.fruits.encode()+"\n"+model.bombs.encode()+"\n"+model.player.encode())
                    receive_player_movement(model, i)
            except IndexError:
                eof=True
            except AttributeError:
                eof=True


# quit
print("Game Over!")
pygame.quit()
