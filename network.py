# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from keyboard import *


################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        self.clients = []
        #   ...

    # time event

    def tick(self, dt):
        #NetworkClientController.add_client_to_server()
        for i in self.clients:
            i.model = self.model
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
        self.player = None

        # ...
        
    def add_client_to_server(self, newbie):
            for i in self.clients:
                if i == newbie:
                    return self.clients
            res = self.clients.append(newbie)
            return res
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
    

    # time event
    def tick(self, dt):#a chaque tick on envoie les nouvelles info au serveur
        #NetworkServerController.clients = add_client_to_server(self.nickname)
        event = KeyboardController.tick(self,dt)
        if event == False:
            self.model=NetworkServerController.model
        elif event == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    print(event.type)
                    self.model.drop_bomb(self.model, self.nickname)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.model.move_character(self.model, self.nickname, DIRECTION_UP)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    self.model.move_character(self.model, self.nickname, DIRECTION_DOWN)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.model.move_character(self.model, self.nickname, DIRECTION_LEFT)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.model.move_character(self.model, self.nickname, DIRECTION_RIGHT)

                NetworkServerController.model = self.model
            return True
        return None
