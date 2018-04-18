# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import sys
import socket
import select

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        self.s = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,proto=0, fileno=None)
        self.s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.s.setblocking(False)
        self.s.bind(('',port))
        self.s.listen(1)
        self.liste_socket = [self.s]

    # time event
        
    def tick(self, dt):
	# creation of sockets + connexion
        (lsock,_,_) = select.select(self.liste_socket,[],[],0)   #le 0 correspond au delais d'attente avant que ça bloque
        for sock in lsock:      #les sockets parmi la liste
            if sock == self.s and lsock:
                (con, ip) = self.s.accept() #on accepte un nouveau client aka nouvelle socket
                print("test 1")
                msg = joueur.recv(1000)
                self.liste_socket.append(con)
            else :
                print("nothing received")
                try:
                    recv_data = sock.recv(1500)
                    if not recv_data:          #On test les données reçues
                        self.liste_socket.remove(sock)
                        sock.close()
                        print("debug : le client est déconnecté")
                        break
                except:
                    print("debug: except de fin")
        return True

    
################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, file, host, port, nickname):
        self.file = file
        self.host = host
        self.port = port
        self.nickname = nickname

    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        # ...
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        # ...
        return True

    # time event

    def tick(self, dt):
        # ...
        return True
'''
    # creating sockets

    s = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,proto=0, fileno=None)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        s.bind((host,port))
    except socket.error:
        print("Echec de la connexion au port choisi")
        sys.exit()
    msg = s.recv(1500)

    while True:
        msg = ("input utilisateur")#ajouter le msg à envoyer aka les entrées claviers pour jouer
        s.send(msg)
    s.close()'''
