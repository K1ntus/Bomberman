# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from keyboard import *
import pickle


################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        self.clients = []
        self.socket = []

    # time event

    def tick(self, dt):
        print("clients list: "+str(self.clients))
        return True

################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################


    
class NetworkClientController:

    def __init__(self, model, host, port, nickname, socket):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        self.player = None
        self.socket = socket

    # keyboard events
    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False
    

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        if not self.model.player: return True
        self.nickname = self.model.player.nickname
        if direction in DIRECTIONS:
            self.model.move_character(self.nickname, direction)
            self.i_just_moved(self.socket,direction)
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        if not self.model.player: return True
        self.nickname = self.model.player.nickname
        self.model.drop_bomb(self.nickname)
        return True

    # look for a character, return None if not found
    def look(self, nickname):
        # https://stackoverflow.com/questions/9542738/python-find-in-list
        character = next( (c for c in self.characters if (c.nickname == nickname)), None) # first occurence
        return character
    
    def i_just_moved(self, socket, direction):
        print("******* S ********\nSend moving information to server ..."+"\n")
        socket.sendall(b'moving')
        socket.recv(1500)
        print("received ACK")
        packet = bytes(str(direction), 'utf8')
        socket.sendall(packet)
        print("received ACK")
        print("direction sent with value "+str((packet))+"\n******** E *******\n")
        #self.socket.recv(1500)
        
    # time event
    def tick(self, dt, socket):#a chaque tick on envoie les nouvelles info au serveur
        #print("SOCKET: "+str(self.socket))

        return True
