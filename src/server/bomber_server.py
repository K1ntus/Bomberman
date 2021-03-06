#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

import sys

import pygame

from src.client.view import FPS
from src.common.model import DEFAULT_MAP, Model, STAR
from src.common.network import NetworkServerController


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

# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
model = Model()
model.load_map(map_file)
for _ in range(10): model.add_fruit()
model.add_bonus(STAR)
#for _ in range(2): model.add_bonus(PUSH) #unfinished item
server = NetworkServerController(model, port)
# view = GraphicView(model, "server")

# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    server.tick(dt)
    model.tick(dt)
    # view.tick(dt)

# quit
print("Game Over!")
pygame.quit()
