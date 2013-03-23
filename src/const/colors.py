# A constants module for holding color objects

from Import import *

libtcod = importLibtcod()


# Common colors
black = libtcod.black
white = libtcod.white
red = libtcod.red
blue = libtcod.blue
lightBlue = libtcod.light_blue
darkBlue = libtcod.darker_blue

#blankBackground = libtcod.BKGND_NONE
# Wall and ground colors

colorWallNotInFOV = libtcod.darker_grey # libtcod.Color(0, 0, 100)
colorLightWall = libtcod.Color(130, 110, 50)
colorDarkGround = libtcod.Color(50, 50, 150)
colorLightGround = libtcod.Color(200, 180, 50)

colorWood = libtcod.darkest_sepia
colorRock = libtcod.light_grey
colorStone = libtcod.lighter_grey
colorGrass = libtcod.darker_green

colorNotInFOV = libtcod.grey