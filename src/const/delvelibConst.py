'''
Created on Jun 27, 2014

@author: dstuart
'''

import delvelibColors as colors

########################
#
# UI
#
########################

LIMIT_FPS = 60

# Map dimensions
MAP_WIDTH = 75
MAP_HEIGHT = 30
MAP_X = 0
MAP_Y = 0
MAP_PANEL_DIMS = (MAP_X, MAP_Y, MAP_WIDTH, MAP_HEIGHT)

CHAR_PANEL_WIDTH = 25
CHAR_PANEL_HEIGHT = MAP_HEIGHT
CHAR_PANEL_X = MAP_WIDTH
CHAR_PANEL_Y = 0
CHAR_PANEL_DIMS = (CHAR_PANEL_X, CHAR_PANEL_Y, CHAR_PANEL_WIDTH, CHAR_PANEL_HEIGHT)

MESSAGE_PANEL_WIDTH = MAP_WIDTH + CHAR_PANEL_WIDTH
MESSAGE_PANEL_HEIGHT = 15
MESSAGE_PANEL_X = 0
MESSAGE_PANEL_Y = MAP_HEIGHT
MESSAGE_PANEL_DIMS = (MESSAGE_PANEL_X, MESSAGE_PANEL_Y, MESSAGE_PANEL_WIDTH, MESSAGE_PANEL_HEIGHT)

# Make sure the screen is actually big enough!

SCREEN_WIDTH = MESSAGE_PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT + MESSAGE_PANEL_HEIGHT

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
ENCODING_MODE = "strict"

# Field of view constants
FOV_RADIUS = 0
PLAYER_VISION_RADIUS = 10


########################
#
# Pathfinding
#
########################

HVCOST = 10
DIAGONALCOST = 10