'''
##########################################################
#
# Created on Jul 11, 2014
#
# Adapted by Dan Stuart
# from the Herringbone Wang Tile algorithm by Sean Barrett:
# http://nothings.org/gamedev/herringbone/
# Retrieved 7/11/2014
# @author: dstuart
#
##########################################################
'''

class WangTile(object):
    
    def __init__(self, width, height, tiles):
        self.width = width
        self.height = height
        self.tiles = tiles

    def getTiles(self):
        return self.tiles
    
    def getTile(self, x, y):
        return self.tiles[y][x]

class SquareWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(SquareWangTile, self).__init__(width, width, tiles)
        

class VRectWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(VRectWangTile, self).__init__(width, width*2, tiles)


class HRectWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(HRectWangTile, self).__init__(width, width/2., tiles)


class WangTileMap(object):
    pass

class SquareWangTileMap(WangTileMap):
    pass

class HerringboneWangTileMap(WangTileMap):
    pass
