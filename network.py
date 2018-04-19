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
        self.nick_dictionnary={self.s:"server"}

        
    def send_map(self, socket):
        #print("\nEnvoie de la map ...")

        try:
            #print("Envoie des caractères")
            characters_to_send = pickle.dumps(self.model.characters)
            try:
                print("SENDING:   "+str(self.model.characters[0].nickname))
                print("SENDING:   "+str(self.model.characters[1].nickname))
            except:
                print("SENDING:   "+str(self.model.characters[0].nickname))

            socket.sendall(characters_to_send)
            socket.recv(1500)
            
            #print("Envoie des fruit")
            fruits_to_send = pickle.dumps(self.model.fruits)
            try:
                print("SENDING:   "+str(self.model.fruits[0]))
                print("SENDING:   "+str(self.model.fruits[1]))
            except:
                print("SENDING:   "+str(self.model.fruits[0]))


            socket.sendall(fruits_to_send)
            socket.recv(1500)

            #print("Envoie des position de bombes")
            bombs_to_send = pickle.dumps(self.model.bombs)
            socket.sendall(bombs_to_send)
            socket.recv(1500)
            
            #print("Envoie des data de la map")
            #print("   -> map width")
            map_width = pickle.dumps(self.model.map.width)
            socket.sendall(map_width)
            socket.recv(1500)

            #print("   -> map height")
            map_height = pickle.dumps(self.model.map.height)
            socket.sendall(map_height)
            socket.recv(1500)
            
            #print("   -> map board")
            map_array_to_send = pickle.dumps(self.model.map.array)
            socket.sendall(map_array_to_send)
            socket.recv(1500)

            #print("Map sent ! \n")
        except BrokenPipeError as e:
            print("[Ln74] A socket disconnected: "+str(e))
            self.disconnect(socket)
            return



    def receive_char_position(self, socket):
        
        for i in self.nick_dictionnary:
            #print("i= "+str(i)+" | socket= "+str(ip))
            (ip,a,b,c) = i.getsockname()
            if i == socket and not (ip == "::"):
                #print("FOUND THE SOCKET")
                inc = 0
                for j in self.model.characters:
                    if j.nickname == self.nick_dictionnary[i]:
                        try:
                            #print("FOUND THE CHARACTER")
                            data = pickle.loads(socket.recv(1500))
                            #print("Received: "+str(data.pos)+" !!!!")
                            
                            socket.send(b'ACK')

                            self.model.characters[inc] = data
                            
                        except OSError as e:
                            print("[Ln101] A socket disconnected: "+str(e))
                            self.disconnect(socket)
                            return
                        except BrokenPipeError as e:
                            print("[Ln106] A socket disconnected: "+str(e))
                            self.disconnect(socket)
                            return

                    inc = inc+1
                    
                
    def receive_bomb_position(self, socket):
        (ip,a,b,c) = socket.getsockname()
        nickname = self.nick_dictionnary[socket]
            
        data = pickle.loads(socket.recv(1500))
        socket.send(b'ACK')
        
        if not data == 'null':
            print("DROPPING A BOMB BY:  "+str(nickname))
            character = self.model.look(nickname)
            #self.model.drop_bomb(nickname)
            self.model.bombs.append(Bomb(self.model.map, character.pos))
                
                

    def first_connection(self, socket, nick_wanted):
        try:
            (ip,a,b,c)=socket.getsockname()
        except OSError:
            print("oups")
            return
        
        new_nick_wanted = nick_wanted
        i=0
        while not self.model.look(new_nick_wanted) == None:
            new_nick_wanted = nick_wanted+str(i)
            i=i+1
            
        self.nick_dictionnary[socket] = new_nick_wanted
        self.model.add_character(self.nick_dictionnary[socket], True)

    def disconnect(self,socket):
        try:
            (ip,a,b,c)=socket.getsockname()
        except OSError as e:
            print("nick dico:" +str(self.nick_dictionnary))
            print("socket list:" +str(self.liste_socket))
            print("oups: "+str(e))
            return
        
        nick_to_remove = self.nick_dictionnary[socket]
        for i in self.nick_dictionnary:
            if self.nick_dictionnary[i] == nick_to_remove:
                self.model.quit(self.nick_dictionnary[socket])
                self.nick_dictionnary.pop(i)
                break
        self.liste_socket.remove(socket)
        socket.close()                      #close the socket

    
       
    # time event 
    def tick(self, dt):
	# creation of sockets + connexion
        (readable_socket,_,_) = select.select(self.liste_socket,[],[],0)   #le 0 correspond au delais d'attente avant que ça bloque
        for sock in readable_socket:      #les sockets parmi la liste
            if sock == self.s:
                    (con, (ip,a,b,c)) = self.s.accept() #on accepte un nouveau client aka nouvelle socket
                    print("ip: "+str(ip)+' connected')

                    
                    self.liste_socket.append(con)
                    
                    self.first_connection(con, con.recv(1500).decode())
                    
                        
                    con.send(b'ACK')
                    con.recv(1500)
                        
                    self.send_map(con)
                                         
                    con.recv(1500)    
                    con.send(b'ACK')
                        
                
            else :
                #print(self.model.player)
                
                try:
                    sock.recv(1500)
                    self.receive_char_position(sock)
                                 
                    sock.recv(1500)    
                    sock.send(b'ACK')
                    self.receive_bomb_position(sock)
                    
                    
                    sock.recv(1500)    
                    sock.send(b'ACK')
                    self.send_map(sock)
                    
                    sock.recv(1500)    
                    sock.send(b'ACK')
                    
                except BrokenPipeError as e:
                    print("[Ln204] Client disconnected: "+str(e))
                    self.disconnect(sock)
                except ConnectionResetError as e:
                    print("[Ln208] Client disconnected: "+str(e))
                    self.disconnect(sock)
                except OSError as e:
                    print("[Ln212] A socket disconnected: "+str(e))
                    self.disconnect(sock)
                    return
                except EOFError as e:
                    print("[Ln217] A socket disconnected: "+str(e))
                    self.disconnect(sock)
                    return
                
        
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

        self.bomb_to_place = 'null'

        self.s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)
        self.s.connect((host, port))

        
        self.s.send(nickname.encode())
        
        self.s.recv(1500)
        self.s.send(b'ACK')
        
        self.receive_map(self.model)


        self.s.send(b'ACK')
        self.s.recv(1500)

        self.model.player = self.model.look(nickname)

    def receive_map(self,model):
        #print("\n---\n| Receiving map")

        #print("| Receiving characters ...")
        try:
            characters = pickle.loads(self.s.recv(1500))
            if not characters: characters_array = []
            else:
                characters_array = characters
            self.s.send(b"ACK")
            #print("characters: "+str(characters_array)+"\n")
            model.characters = characters
        except EOFError as e:
            print("Error while receiving char: "+str(e))
            model.characters = []

        #print("| Receiving fruits ...")
        fruits = pickle.loads(self.s.recv(1500))
        if not fruits: fruits_array = []
        else:
            fruits_array = fruits
        self.s.sendall(b"ACK")
        #print("fruits: "+str(fruits_array)+"\n")
        model.fruits = fruits

        #print("| Receiving bombs ...")
        bombs = pickle.loads(self.s.recv(1500))
        if not bombs: bombs_array = []
        else:
            bombs_array = bombs
        self.s.send(b"ACK")
        #print("bombs: "+str(bombs_array)+"\n")
        model.bombs = bombs
        

        #print("| Receiving map data ...")
        model.map.width = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        model.map.height = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        model.map.array = pickle.loads(self.s.recv(1500))
        self.s.send(b"ACK")
        
        #print("| Map well received\n---\n")

    def send_bomb_data(self):
        print("\n---\n| Sending new bomb data\n")
        bombs_to_send = pickle.dumps(self.bomb_to_place)
        self.s.sendall(bombs_to_send)
        print("| bomb data sent")
        self.s.recv(1500)
        print("| Received ACK\n---\n")
        self.bomb_to_place = 'null'
        
    def send_my_pos(self):
        print("\n---\n| Sending my position\n")
        self.s.send(pickle.dumps(self.model.look(self.nickname)))
        print("| Position sent")
        self.s.recv(1500)
        print("| Received ACK\n---\n")
        
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
    
        
    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        if not self.model.player: return True
        nickname = self.model.player.nickname
        self.model.drop_bomb(nickname)
        
        self.bomb_to_place ='null'
        for bomb in self.model.bombs:
            data_to_send = pickle.dumps('null')
            if bomb.pos == self.model.look(nickname).pos:
                self.bomb_to_place = bomb
                break
            
        return True

    # time event

    def tick(self, dt):
        
        self.s.send(b'ACK')


        self.send_my_pos()
        self.s.send(b'ACK')
        self.s.recv(1500)


        self.send_bomb_data()
        self.s.send(b'ACK')
        self.s.recv(1500)

        
        self.receive_map(self.model)
        self.s.send(b'ACK')
        self.s.recv(1500)

        
        return True
