# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
import sys
import socket
import select
import pickle

import threading

import time #time.sleep(1) #1000ms

################################################################################
#                               THREAD TIME OUT                                #
################################################################################
import signal

class TimeoutException (Exception):
    pass

def signalHandler (signum, frame):
    raise TimeoutException ()

TIMEOUT_DURATION = 5

signal.signal (signal.SIGALRM, signalHandler)
signal.alarm (TIMEOUT_DURATION)
################################################################################
#                                     CONSTANTE                                #
################################################################################


BAN_HAMMER = 0      #generating bombs on the map
CRAZY_FRUIT = 1     #generating new fruits
ISSOU = 2           #no event
STAR_RAIN = 3       #generating a star: invulnerability 1k ms
BOMB_AKBAR = 4

#multiple time the same event for probability
SERVER_EVENTS = [
        BAN_HAMMER, BAN_HAMMER,                 #2 - one bomb on each characters
        CRAZY_FRUIT, CRAZY_FRUIT, CRAZY_FRUIT,  #4 - 2 fruits appears
        ISSOU, ISSOU, ISSOU, ISSOU,             #3 - nothing
        STAR_RAIN,                              #1 - invulnerability
        BOMB_AKBAR, BOMB_AKBAR, BOMB_AKBAR, BOMB_AKBAR, BOMB_AKBAR, BOMB_AKBAR, BOMB_AKBAR
    ]                             

TICK_BEFORE_EVENT = 12500     #tick etween each server events in ms
MIN_PLAYER_FOR_EVENT = 2    #Minimal numbers of players to allow server events


################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        threading.Thread.__init__(self)
        self.verrou = threading.Lock()      #verrou pour synchroniser les threads
        self.threads = {}                   #dictionnaire contenant de la forme SOCKET_CLIENT:THREAD_CLIENT
        
        self.model = model
        self.port = port
        
        self.s = socket.socket(family=socket.AF_INET6,type=socket.SOCK_STREAM,proto=0, fileno=None) #On cree la socket server ipv6
        self.s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)                                  #on bypass le cas ou le port est deja utilise          
        self.s.setblocking(False)
        self.s.bind(('',port))
        self.s.listen(1)
        
        self.liste_socket = [self.s]
        
        (ip,a,b,c) = self.s.getsockname()
        self.nick_dictionnary={self.s:"server"}

        self.tick_before_event = 0      #compteur entre chaque evenements serveurs




    def event_banHammer(self):  
        for c in self.model.characters:
            self.model.drop_bomb(c.nickname)
        
    def event_bombAkbar(self):  
        pos = self.model.map.random()
        for i in range(5):
            self.model.bombs.append(Bomb(self.model.map, pos))
            
    def map_event(self):    #fonction principale permettant la gestion des evenements aleatoires 
        if self.tick_before_event >= TICK_BEFORE_EVENT:
            choice = random.choice(SERVER_EVENTS)
            self.tick_before_event = 0
            
            if choice == BAN_HAMMER:    #Un evenement qui 'invoque' des bombes sous les pieds de chaques joueurs
                print("SERVER EVENT: ban hammer !")
                self.event_banHammer()
                return
            elif choice == STAR_RAIN:   #genere une etoile qui rend invulnerable
                print("SERVER EVENT: star rain !")
                #self.model.add_fruit(STAR)
                return
            elif choice == ISSOU:       #Aucun event
                print("SERVER EVENT: issou !")
                return
            elif choice == CRAZY_FRUIT: #Ajoute deux fruits aleatoirement
                print("SERVER EVENT: crazy fruit !")
                for _ in range(2): self.model.add_fruit()
                return
            elif choice == BOMB_AKBAR: #pluie de bombe, tu vas prendre cher
                print("SERVER EVENT: bomb akbar !")
                self.event_bombAkbar()
                return
        
    def send_map(self, socket):
        #print("\nEnvoie de la map ...")

        try:
            #print("Envoie des caractères")
            characters_to_send = pickle.dumps(self.model.characters)

            socket.sendall(characters_to_send)
            socket.recv(1500)
            
            #print("Envoie des fruit")
            fruits_to_send = pickle.dumps(self.model.fruits)
            socket.sendall(fruits_to_send)
            socket.recv(1500)
            
            #print("Envoie des bonus")
            items_to_send = pickle.dumps(self.model.bonus)
            socket.sendall(items_to_send)
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
        try:
            data = pickle.loads(socket.recv(2048))
            #print("DATA received:    "+str(data))
            socket.send(b'ACK')

            character = self.model.look(data.nickname)
            character.pos = data.pos
            
            character.direction = data.direction
        except EOFError as e:
            print("[0x12] error: "+ str(e))
            self.disconnect(socket)
            sys.exit()
                    
                
    def receive_bomb_position(self, socket):
        (ip,a,b,c) = socket.getsockname()
        nickname = self.nick_dictionnary[socket]
            
        data = pickle.loads(socket.recv(2048))
        socket.send(b'ACK')
        
        if not data == 'null':
            print("DROPPING A BOMB BY:  "+str(nickname))
            character = self.model.look(nickname)


            #Boucle for parcourant toutes les bombes deja placees
            #S'il y a deja une bombe a cette position, on quitte la fonction
            #sinon: on place une bombe a la position du joueur
            for bomb in self.model.bombs:
                if bomb.pos == character.pos:
                    return
                
            self.model.drop_bomb(nickname)
                
                

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
        self.model.add_character(self.nick_dictionnary[socket], isplayer = False)



    def disconnect(self,socket):
        port = 0
        ip = 0
        try:
            (ip,port,b,c)=socket.getsockname()
            if ip == '::':
                return
        except OSError as e:
            print("[0x0f]: "+str(e))
        
        print("A client as disconnected:   "+str(ip) + " : "+str(port))
        nick_to_remove = self.nick_dictionnary[socket]              #on recupere le pseudo de la socket
        for i in self.nick_dictionnary:                             
            if self.nick_dictionnary[i] == nick_to_remove:          #si la pos i est celle du pseudo
                self.model.quit(self.nick_dictionnary[socket])      #on expulse le joueur avec ce pseudo
                self.nick_dictionnary.pop(i)                        #on retire son pseudo du dictionnaire
                break
        self.liste_socket.remove(socket)    #on retire sa socket de la liste
        socket.close()                      #close the socket
        print("\n\n")


    def read_and_write(self, sock):
        (ip,port,c,d) = sock.getsockname()
        if sock == self.s:
            return
        try:
            if not self.nick_dictionnary.get(sock) == None:
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
            else:#TO DO (s il n y a pas le nickname de la socket dans le dico, ie. son perso est mort)
                self.send_map(sock)
                
                sock.recv(1500)    
                sock.send(b'ACK')
                return
                
        except TimeoutException as exc:
            print("Execution thread taking too much time to respond:  "+str(exc))
            pass
        except pickle.UnpicklingError:
            sys.exit()
            return
        except socket.timeout:
            print(str(ip) + " : "+str(port) + "  as lost connection")
            sock.send(b'ACK')
            print("Reconnection in pending ...")
            self.read_and_write(sock)
            print(str(ip) + " : "+str(port) + " just reconnected !")
            return False

       
    # time event 
    def tick(self, dt):
        signal.alarm (0)
        Thread = None
        if len(self.liste_socket) > (MIN_PLAYER_FOR_EVENT): #s il y a au moins deux joueurs
            self.tick_before_event += dt                    #a chaque tick, on incremente le compteur avant un event
        self.map_event()                                    #on appelle la fonction gerant les events 


        (readable_socket,_,_) = select.select(self.liste_socket,[],[],0)   #le 0 correspond au delais d'attente avant que ça bloque

        for sock in readable_socket:                    #les sockets parmi la liste
            

                    
            self.verrou.acquire()                       #On 'desactive' les autres threads
            
            if sock == self.s:  #premiere connexion
                    (con, (ip,a,b,c)) = self.s.accept() #on accepte un nouveau client aka nouvelle socket
                    print("ip: "+str(ip)+ "  :  "+str(a)+' connected')
                    con.settimeout(1)

                    self.liste_socket.append(con)       #on ajoute la nouvelle socket a la liste des sockets
                    
                    self.first_connection(con, con.recv(1500).decode()) #fonction recuperant le nickname, etc de la socket venant de se connecter
                    
                        
                    con.send(b'ACK')
                    con.recv(1500)  #paquets servant d accuses de reception pour ne pas 'corrompre les differents paquets
                        
                    self.send_map(con)  #on envoie la map a la socket
                                         
                    con.recv(1500)    
                    con.send(b'ACK')

                    

                    #on cree un nouveau thread (que l on  demarre)
                    #puis on l ajoute au dictionnaire de notre class
                    Thread = threading.Thread(None, self.read_and_write, None, (sock,)).start()
                    self.threads[con] = Thread


                    #ESSAYER CA MB
                    #self.verrou.release()#on deverouille le verrou qui etait utilise par le thread de cette socket


                
            else :  #si ce n est pas la premiere connexion
                signal.alarm (0)

                
                try:
                    if self.threads[sock] is not None and self.threads[sock].is_alive():        #si le thread est deja en train de fonctionner
                        pass#already running
                    
                    else:   #si il n y a pas de thread pour cette socket
                        #on cree un nouveau thread etc
                        Thread = threading.Thread(None, self.read_and_write, None, (sock,))
                        self.threads[sock] = Thread
                        Thread.start()
                        pass#run a new thread

                    
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
                except RuntimeError as e:
                    print("[Ln217] A socket disconnected: "+str(e))
                    self.disconnect(sock)
                    return
                except TimeoutException as exc:
                    print("Execution thread taking too much time to respond:  "+str(exc))
                    pass
            self.verrou.release()#on deverouille le verrou qui etait utilise par le thread de cette socket

                
                
        
        return True

    
################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        threading.Thread.__init__(self)
        self.verrou = threading.Lock()      #verrou pour synchroniser les threads
        
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname

        self.bomb_to_place = 'null'

        self.s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM, proto=0, fileno=None)
        self.s.connect((host, port))
        self.s.settimeout(1)

        
        self.s.send(nickname.encode())
        
        self.s.recv(1500)
        self.s.send(b'ACK')
        
        self.receive_map(self.model)


        self.s.send(b'ACK')
        self.s.recv(1500)
        
        self.model.player = self.model.look(nickname)
        
    def loose(self, model):
        if model.player.is_dead():
            printf("Le joueur " + str(self.nickname) + "a perdu\n")
            character = model.look(self.nickname)
            self.model.kill_character(character)

    def receive_map(self,model):
        #print("\n---\n| Receiving map")

        #print("| Receiving characters ...")
        characters = pickle.loads(self.s.recv(65536))
        if not characters: characters_array = []
        else:
            characters_array = characters
        self.s.send(b"ACK")
        #print("characters: "+str(characters_array)+"\n")
        model.characters = characters

        #print("| Receiving fruits ...")
        fruits = pickle.loads(self.s.recv(65536))
        if not fruits: fruits_array = []
        else:
            fruits_array = fruits
        self.s.sendall(b"ACK")
        #print("fruits: "+str(fruits_array)+"\n")
        model.fruits = fruits

        #print("| Receiving items ...")
        items = pickle.loads(self.s.recv(65536))
        if not items: items_array = []
        else:
            items_array = items
        self.s.sendall(b"ACK")
        #print("fruits: "+str(fruits_array)+"\n")
        model.bonus = items

        #print("| Receiving bombs ...")
        bombs = pickle.loads(self.s.recv(65536))
        if not bombs: bombs_array = []
        else:
            bombs_array = bombs
        self.s.send(b"ACK")
        #print("bombs: "+str(bombs_array)+"\n")
        model.bombs = bombs
        

        #print("| Receiving map data ...")
        model.map.width = pickle.loads(self.s.recv(65536))
        self.s.send(b"ACK")
        model.map.height = pickle.loads(self.s.recv(1024))
        self.s.send(b"ACK")
        model.map.array = pickle.loads(self.s.recv(1024))
        self.s.send(b"ACK")
        
        #print("| Map well received\n---\n")

    def send_bomb_data(self):
        #print("\n---\n| Sending new bomb data")
        bombs_to_send = pickle.dumps(self.bomb_to_place)
        self.s.sendall(bombs_to_send)
        #print("| bomb data sent")
        self.s.recv(1500)
        #print("| Received ACK\n---\n")
        self.bomb_to_place = 'null'
        
    def send_my_pos(self):
        #print("\n---\n| Sending my position")
        self.s.send(pickle.dumps(self.model.player))
        #print("| Position sent")
        self.s.recv(1500)
        #print("| Received ACK\n---\n")
        
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

    def spectate(self):
        print("a")
        #foncton appelée pour charger les data apres que le joueur soit mort

    def receive_all_data(self):                
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
                return

    # time event
    def tick(self, dt):
        #Thread = threading.Thread(None, self.receive_all_data, None, (self.s,)).start()
        signal.alarm (0)
        try:
            if not self.model.look(self.nickname) == None:
                self.receive_all_data()
        except socket.timeout:
            print("Timed out ...")
            self.s.settimeout(5)
            self.s.recv(1500)
            print("Reconnection ...")
            self.tick(dt)
            
            self.s.settimeout(1)
            print("Reconnected !")
            return True
            
        try:
            self.model.player = self.model.look(self.nickname)
        except AttributeError as e:
            self.model.player = None
            print("[0x001] disconnected: "+str(e))
            return False

        
        return True
