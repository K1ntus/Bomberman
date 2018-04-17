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
import pickle #send array over sockets ##RICK
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
    
def adding_new_nick(socket):
    
    (ip,a,b,c)=socket.getsockname()  
    nick_wanted=pickle.loads(socket.recv(1500))#attribute the nick parameters to this ip
    socket.send(b"ACK")
    
    new_nick_wanted = nick_wanted
    i=0
    while not server.model.look(new_nick_wanted) == None:
        new_nick_wanted = nick_wanted+str(i)
        i=i+1
    nick_dictionnary[ip] = new_nick_wanted
    server.model.add_character(nick_dictionnary[ip], True)
        

def receive_player_movement(socket):
    print("IM on the moving function ")

    (ip,a,b,c) = socket.getsockname()
    username = nick_dictionnary[ip]

    movement = socket.recv(1500)
    print("MOVING THE CHARACTER: "+ str(username) + "\n\n")
    print("MOVEMENT: "+str(movement) + " --> " + str(movement.decode()))
    socket.send(b"ACK")
    print("MOVING: Sent ACK")
        
    if server.model.look(username):
                

        print("I received the order to move to: "+ movement.decode())
        try:
            server.model.move_character(username, int(movement.decode()))
        except ValueError as e:
            print("Packet error: "+str(e))
            return False
        return True
    print("Unable to find the character:  "+username)
    return False
    
    


def send_map(socket):
    try:
        print("Envoie des caractères")
        characters_to_send = pickle.dumps(server.model.characters)
        socket.sendall(characters_to_send)
        socket.recv(1500)
        
        print("Envoie des fruit")
        fruits_to_send = pickle.dumps(server.model.fruits)
        socket.sendall(fruits_to_send)
        socket.recv(1500)

        print("Envoie des position de bombes")
        bombs_to_send = pickle.dumps(server.model.bombs)
        socket.sendall(bombs_to_send)
        socket.recv(1500)
        
        print("Envoie des player_to_send ")
        player_to_send = pickle.dumps(server.model.player)
        socket.sendall(player_to_send)
        socket.recv(1500)
        
        print("Envoie des data de la map")
        print("   -> map width")
        map_width = pickle.dumps(server.model.map.width)
        socket.sendall(map_width)
        socket.recv(1500)

        print("   -> map height")
        map_height = pickle.dumps(server.model.map.height)
        socket.sendall(map_height)
        socket.recv(1500)
        
        print("   -> map board")
        map_array_to_send = pickle.dumps(server.model.map.array)
        socket.sendall(map_array_to_send)
        socket.recv(1500)

        print("Map sent ! ")
    except OSError as e:
        print("A socket disconnected: "+str(e))
    

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

cmd = False



# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    model.tick(dt)
    # view.tick(dt)
    
    (readable_socket, a,b) = select.select(socket_list, [],[])  #Work like a crossroad
    #print("socket list : "+ str(socket_list) )
    for i in readable_socket:                   #for each socket on the list
        if i == s:                              #if the socket is the listening one
            (con,addr)=i.accept()               #we get the information (ie. socket and address) and accept his connection request
            socket_list.append(con)             #we had the socket to the socket list
            (socket_ip,a,b,c)=i.getsockname()
            server.socket.append(con)
            server.clients.append(con)
            cmd = True
        else:                           #else we get the data
            data = i.recv(1500)         #We receive the data of a length of 1500Bytes
            print("Data: " + str(data))
            
            if not data or data == '\n' or data == b'':
                disconnect(socket_list, i)
            try:
                if data == b"sending_nick":
                    i.send(b'ACK')
                    print("gonna send nick, ack has been sent")
                    adding_new_nick(i)
                elif data == b"moving":
                    i.send(b'ACK')
                    receive_player_movement(i)

                
            except IndexError:
                eof=True
            except AttributeError:
                eof=True

    server.tick(dt)

# quit
print("Game Over!")
pygame.quit()
