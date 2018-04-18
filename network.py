# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import sys
import socket
import select
import pickle
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
        self.s.listen(2)
        self.liste_socket = [self.s]

    # time event
    def send_map(self, socket):
        print("Sending map to: "+str(socket))
        packet_to_send = pickle.dumps(self.model)
        print("Will send: "+str(packet_to_send))
        socket.send(packet_to_send)
        print("Packet received: "+str(socket.recv(1500)))
        print("Map well sent ! Hourra !")
        
    def tick(self, dt):
	# creation of sockets + connexion
        (lsock,_,_) = select.select(self.liste_socket,[],[],0)   #le 0 correspond au delais d'attente avant que ça bloque
        for sock in lsock:      #les sockets parmi la liste
            if sock == self.s and lsock:
                (con, ip) = self.s.accept() #on accepte un nouveau client aka nouvelle socket
                print("test 1")
                self.liste_socket.append(con)
                self.model.add_character(con.recv(1500),True)
                con.send(b'ACK')
            else :
                try:
                    sock.recv(1500)
                    self.send_map(sock)
                except BrokenPipeError as e:
                    print("Client disconnected: "+str(e))
                    self.liste_socket.remove(sock)
                
        return True

    
################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, file, host, port, nickname):
        self.model = file
        self.host = host
        self.port = port
        self.nickname = nickname

        self.s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)
        self.s.connect((host, port))
        
        self.s.send(b'nickname')
        self.s.recv(1500)

    def receive_map(self, host_socket):
        print("Receiving map ...")
        packet_received = host_socket.recv(2048)
        print("My map is:   "+str(packet_received))
        try:
            packet_received = pickle.loads(packet_received)
            #print("Packet = "+str(packet_received))
        except EOFError:
            print("OMG ERROR")
            data = list()  # or whatever you want
        print("   -> sending ACK")
        host_socket.send(b'ACK')
        print("Map well received")
        return packet_received

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
        self.s.send(b'ACK')
        self.model = self.receive_map(self.s)
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
