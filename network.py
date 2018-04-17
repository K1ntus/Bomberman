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
        for i in self.socket:
            i.sendall(b'sending_map')
            i.recv(1500)
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


    def receive_map(self,):
        print("Receiving map ...")


        print("Receiving characters ...")
        characters = pickle.loads(self.socket.recv(1500))
        if not characters: characters_array = []
        else:
            characters_array = characters
        self.socket.send(b"ACK")
        #print("characters: "+str(characters_array)+"\n")
        self.model.characters = characters

        print("Receiving fruits ...")
        fruits = pickle.loads(self.socket.recv(1500))
        if not fruits: fruits_array = []
        else:
            fruits_array = fruits
        self.socket.sendall(b"ACK")
        #print("fruits: "+str(fruits_array)+"\n")
        self.model.fruits = fruits

        print("Receiving bombs ...")
        bombs = pickle.loads(self.socket.recv(1500))
        if not bombs: bombs_array = []
        else:
            bombs_array = bombs
        self.socket.send(b"ACK")
        #print("bombs: "+str(bombs_array)+"\n")
        self.model.bombs = bombs
        
        print("Receiving players ...")
        players = pickle.loads(self.socket.recv(1500))
        #print("players: "+str(players))
        if not players: players_array = []
        else:
            players_array = players
        self.socket.send(b"ACK")
        #print("players: "+str(players_array)+"\n")
        self.model.player = players

        print("Receiving map data ...")
        model.map.width = pickle.loads(self.socket.recv(1500))
        self.socket.send(b"ACK")
        model.map.height = pickle.loads(self.socket.recv(1500))
        self.socket.send(b"ACK")
        model.map.array = pickle.loads(self.socket.recv(1500))
        self.socket.send(b"ACK")
        #print("setting received data to the map from the model")

        
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
            print("\n\n******* S******* \nSend moving information to server ..."+"\n")
            
            socket.sendall(b'moving')
            data = socket.recv(1500)
            
            print("received ACK for moving my char from the server:  " + str(data))
            
            packet = bytes(str(direction), 'utf8')
            socket.sendall(packet)


            data=socket.recv(1500)
            print("received "+ str(data))
            
            print("direction sent with value "+str((packet))+"\n******* E******* \n\n")
            
            #self.socket.recv(1500)

            
    # time event
    def tick(self, dt):#a chaque tick on envoie les nouvelles info au serveur
        
        data = self.socket.recv(1500)
        print ("DATA: -----> "+data)
        if data == b'sending_map':
            print("blabla")
            self.socket.send(b'ACK')
            self.receive_map()

        return True
