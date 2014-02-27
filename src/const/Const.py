'''
Created on Mar 10, 2013

@author: dstu
'''

import colors

# Global constants

TITLE = "delveRL"


########################
#
# UI
#
########################

LIMIT_FPS = 60

# Map dimensions
MAP_WIDTH = 75
MAP_HEIGHT = 45
MAP_X = 0
MAP_Y = 0
MAP_PANEL_DIMS = (MAP_X, MAP_Y, MAP_WIDTH, MAP_HEIGHT)

CHAR_PANEL_WIDTH = 25
CHAR_PANEL_HEIGHT = MAP_HEIGHT
CHAR_PANEL_X = MAP_WIDTH
CHAR_PANEL_Y = 0
CHAR_PANEL_DIMS = (CHAR_PANEL_X, CHAR_PANEL_Y, CHAR_PANEL_WIDTH, CHAR_PANEL_HEIGHT)

MESSAGE_PANEL_WIDTH = MAP_WIDTH + CHAR_PANEL_WIDTH
MESSAGE_PANEL_HEIGHT = 25
MESSAGE_PANEL_X = 0
MESSAGE_PANEL_Y = MAP_HEIGHT
MESSAGE_PANEL_DIMS = (MESSAGE_PANEL_X, MESSAGE_PANEL_Y, MESSAGE_PANEL_WIDTH, MESSAGE_PANEL_HEIGHT)

# Make sure the screen is actually big enough!

SCREEN_WIDTH = MESSAGE_PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_PANEL_HEIGHT

#PANEL_WIDTH = MAP_WIDTH
#PANEL_HEIGHT = 7
#PANEL_X = 0
## PANEL_Y = 50
#PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT


MENU_WIDTH = 25
MENU_MAX_WIDTH = 50
MENU_X = 20 #SCREEN_WIDTH - MENU_WIDTH
MENU_Y = 10
MENU_FPS = 20
MENU_MARGIN = 1
MENU_TEXT_COLOR = colors.white
MENU_SELECTED_COLOR = colors.goldenrod
MENU_UNSELECTED_COLOR = colors.black

PICK_UP_ITEM_MENU_HEADER = "Pick up what?"
PLAYER_INVENTORY_HEADER = "Inventory"
WEAR_MENU_HEADER = "Wear what?"
WIELD_MENU_HEADER = "Wield what?"
QUAFF_MENU_HEADER = "Drink what?"
READ_MENU_HEADER = "Read what?"
EAT_MENU_HEADER = "Eat what?"
ZAP_MENU_HEADER = "Zap what?"

BAR_WIDTH = 20

ENCODING = "utf_8"
ENCODING_MODE = "ignore"

#MSG_X = BAR_WIDTH + 2
#MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
#MSG_HEIGHT = PANEL_HEIGHT - 1

#MAP_WIDTH = 10
#MAP_HEIGHT = 10

# Field of view constants
#FOV_ALGO = libtcod.FOV_BASIC  #default FOV algorithm
FOV_RADIUS = 0
PLAYER_VISION_RADIUS = 10

########################
#
# World Map
#
########################

WORLD_MAP_WIDTH = 55
WORLD_MAP_HEIGHT = 93

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

TOWN_CELL_WIDTH = 40
TOWN_CELL_HEIGHT = 40

# Max monsters per room
MAX_ROOM_MONSTERS = 3

# Max items per room
MAX_ROOM_ITEMS = 2

#ROOM_MAX_SIZE = 3
#ROOM_MIN_SIZE = 1
#MAX_ROOMS = 3
#DUNGEON_MARGIN = 0

########################
#
# Pathfinding
#
########################

HVCOST = 10
DIAGONALCOST = 10