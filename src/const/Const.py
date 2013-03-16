'''
Created on Mar 10, 2013

@author: dstu
'''

import libtcodpy as libtcod

# Global constants

TITLE = "delveRL"


########################
#
# UI
#
########################

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 70

LIMIT_FPS = 10

# Map dimensions
MAP_WIDTH = 80
MAP_HEIGHT = 50
MAP_X = 0
MAP_Y = 0

#PANEL_HEIGHT = 20
PANEL_WIDTH = MAP_WIDTH
PANEL_X = 0
PANEL_Y = 50

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#MAP_WIDTH = 10
#MAP_HEIGHT = 10

# Field of view constants
FOV_ALGO = libtcod.FOV_BASIC  #default FOV algorithm
FOV_LIGHT_WALLS = True


########################
#
# Dungeon Generation
#
########################

# Some dungeon generation constants
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
DUNGEON_MARGIN = 2
MAX_ROOMS_AND_CORRIDORS = 100
ROOM_CHANCE = 75

# Max monsters per room
MAX_ROOM_MONSTERS = 3

# Max items per room
MAX_ROOM_ITEMS = 2

#ROOM_MAX_SIZE = 3
#ROOM_MIN_SIZE = 1
#MAX_ROOMS = 3
#DUNGEON_MARGIN = 0

