# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import sys
import socket
import select
import pickle

import time
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

        
    def send_map(self, socket):
        print("\nEnvoie de la map ...")

        try:
            print("Envoie des caractères")
            characters_to_send = pickle.dumps(self.model.characters)
            socket.sendall(characters_to_send)
            socket.recv(1500)
            
            print("Envoie des fruit")
            fruits_to_send = pickle.dumps(self.model.fruits)
            socket.sendall(fruits_to_send)
            socket.recv(1500)

            print("Envoie des position de bombes")
            bombs_to_send = pickle.dumps(self.model.bombs)
            socket.sendall(bombs_to_send)
            socket.recv(1500)
            
            print("Envoie des player_to_send ")
            player_to_send = pickle.dumps(self.model.player)
            socket.sendall(player_to_send)
            socket.recv(1500)
            
            print("Envoie des data de la map")
            print("   -> map width")
            map_width = pickle.dumps(self.model.map.width)
            socket.sendall(map_width)
            socket.recv(1500)

            print("   -> map height")
            map_height = pickle.dumps(self.model.map.height)
            socket.sendall(map_height)
            socket.recv(1500)
            
            print("   -> map board")
            map_array_to_send = pickle.dumps(self.model.map.array)
            socket.sendall(map_array_to_send)
            socket.recv(1500)

            print("Map sent ! \n")
        except OSError as e:
            print("A socket disconnected: "+str(e))
            self.disconnect(socket)
            self.liste_socket.remove(socket)
            return
        except BrokenPipeError as e:
            print("A socket disconnected: "+str(e))
            self.disconnect(socket)
            self.liste_socket.remove(socket)
            return



    def receive_char_position(self, socket):
        (ip,a,b,c) = socket.getsockname()
        print("nick dico = " +str(self.nick_dictionnary))
        
        for i in self.nick_dictionnary:
            print("i= "+str(i)+" | socket= "+str(ip))
            if i == ip and not (ip == "::"):
                print("FOUND THE SOCKET")  
                for j in self.model.characters:
                    if j.nickname == self.nick_dictionnary[i]:
                        print("FOUND THE CHARACTER")
                        data = pickle.loads(socket.recv(1500))
                        
                        socket.send(b'ACK')

                        j = data
        time.sleep(1)
                

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
                                 
                    sock.recv(1500)    
                    sock.send(b'ACK')
                    self.receive_char_position(sock)
                    
                except BrokenPipeError as e:
                    print("Client disconnected: "+str(e))
                    self.disconnect(sock)
                    self.liste_socket.remove(sock)
                except ConnectionResetError as e:
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

        
        self.s.send(nickname.encode())
        self.s.recv(1500)

    def receive_map(self,model):
        print("\n---\n| Receiving map")

        print("| Receiving characters ...")
        characters = pickle.loads(self.s.recv(1500))
        if not characters: characters_array = []
        else:
            characters_array = characters
        self.s.send(b"ACK")
        #print("characters: "+str(characters_array)+"\n")
        model.characters = characters

        print("| Receiving fruits ...")
        fruits = pickle.loads(self.s.recv(1500))
        if not fruits: fruits_array = []
        else:
            fruits_array = fruits
        self.s.sendall(b"ACK")
        #print("fruits: "+str(fruits_array)+"\n")
        model.fruits = fruits

        print("| Receiving bombs ...")
        bombs = pickle.loads(self.s.recv(1500))
        if not bombs: bombs_array = []
        else:
            bombs_array = bombs
        self.s.send(b"ACK")
        #print("bombs: "+str(bombs_array)+"\n")
        model.bombs = bombs
        
        print("| Receiving players ...")
        players = pickle.loads(self.s.recv(1500))
        #print("players: "+str(players))
        if not players: players_array = []
        else:
            players_array = players
        self.s.send(b"ACK")
        #print("players: "+str(players_array)+"\n")
        model.player = players

        print("| Receiving map data ...")
        model.map.width = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        model.map.height = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        model.map.array = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        
        print("| Map well received\n---\n")

        

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
            #self.s.recv(1500)
        return True
    
    def send_my_pos(self):
        print("\n---\n| Sending my position\n")
        self.s.send(pickle.dumps(self.model.characters[0]))
        print("| Position sent")
        self.s.recv(1500)
        print("| Received ACK\n---\n")
        time.sleep(1)
        
    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        return True

    # time event

    def tick(self, dt):
        

        self.s.send(b'ACK')
        self.receive_map(self.model)


        self.s.send(b'ACK')
        self.s.recv(1500)
        #print("CHARACTERS: "+str(self.model.characters[0].pos))
        self.send_my_pos()
        
        return True
