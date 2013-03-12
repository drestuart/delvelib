# A constants module for holding color objects

from Import import *

libtcod = importLibtcod()

black = libtcod.black
white = libtcod.white
red = libtcod.red
# Wall and ground colors

colorDarkWall = libtcod.Color(0, 0, 100)
colorLightWall = libtcod.Color(130, 110, 50)
colorDarkGround = libtcod.Color(50, 50, 150)
colorLightGround = libtcod.Color(200, 180, 50)

colorWood = libtcod.sepia
colorRock = libtcod.light_grey
colorStone = libtcod.lighter_grey
colorGrass = libtcod.darker_green