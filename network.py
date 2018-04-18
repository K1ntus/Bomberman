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
        self.s.listen(1)
        
        self.liste_socket = [self.s]
        
        (ip,a,b,c) = self.s.getsockname()
        self.nick_dictionnary={ip:"server"}

    def first_connection(self, socket, nick_wanted):
        (ip,a,b,c)=socket.getsockname()  
        
        new_nick_wanted = nick_wanted
        i=0
        while not self.model.look(new_nick_wanted) == None:
            new_nick_wanted = nick_wanted+str(i)
            i=i+1
        self.nick_dictionnary[ip] = new_nick_wanted
        self.model.add_character(self.nick_dictionnary[ip], True)

    def disconnect(self,socket):
        (ip,a,b,c) = socket.getsockname()
        nick_to_remove = self.nick_dictionnary[ip]
        self.model.quit(nick_to_remove)

        try:
            (ip,a,b,c) = socket.getsockname()
            nick_to_remove = self.nick_dictionnary[ip]
            for i in nick_dictionnary:
                if i == nick_to_remove:
                    self.model.kill_character(nick_to_kill)
                    self.nick_dictionnary.pop(i)
        except:
            print("No such key to remove (nickname on leave)")
            pass
        socket.close()                      #close the socket
    
    # time event
    def send_map(self, socket):
        print("Sending map to: "+str(socket))
        packet_to_send = pickle.dumps(self.model)
        print("Will send: "+str(packet_to_send))
        socket.send(packet_to_send)
        print("Packet received: "+str(socket.recv(1500)))
        print("Map well sent ! Hourra !")

    def receive_player_movement(self,socket):
        print("sending ack packet")
        socket.send(b"ACK")
        print("ack packet received from remote host")

        (ip,a,b,c) = socket.getsockname()
        username = nick_dictionnary[ip]
        
        movement = socket.recv(1500)#attribute the nick parameters to this ip
        socket.send(b"ACK")
        print("I received the order to move to: "+ movement.decode())
        model.move_character(username, int(movement.decode()))        
        
    def tick(self, dt):
	# creation of sockets + connexion
        (lsock,_,_) = select.select(self.liste_socket,[],[],0)   #le 0 correspond au delais d'attente avant que ça bloque
        for sock in lsock:      #les sockets parmi la liste
            if sock == self.s and lsock:
                (con, ip) = self.s.accept() #on accepte un nouveau client aka nouvelle socket
                print("test 1")
                self.liste_socket.append(con)
                self.first_connection(con, con.recv(1500).decode())
                con.send(b'ACK')
            else :
                try:
                    sock.recv(1500)
                    self.send_map(sock)
                except BrokenPipeError as e:
                    print("Client disconnected: "+str(e))
                    self.disconnect(sock)
                    self.liste_socket.remove(sock)
                
        return True

    
################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        self.model = model
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
        try:
            packet_received = pickle.loads(packet_received)
            self.model = packet_received
            #print("Packet = "+str(packet_received))
        except EOFError:
            print("OMG ERROR")
            data = list()  # or whatever you want
        
        print("   -> sending ACK")
        host_socket.send(b'ACK')
        
        print("Map well received ...")

        

    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, s_server, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        s_server.send(direction.encode())
        s_server.recv(1500)
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        # ...
        return True

    # time event

    def tick(self, dt):
        self.s.send(b'ACK')
        self.receive_map(self.s)
        return True
