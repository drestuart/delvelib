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

from copy import deepcopy

class WangTile(object):
    
    def __init__(self, width, height, tiles):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.constraints = dict()

    def getTiles(self):
        return self.tiles
    
    def getTile(self, x, y):
        return self.tiles[y][x]
    
    def getCoords(self):
        return self.coords
    
    def setCoords(self, coords):
        self.x, self.y = coords # Top-left corner coords
    
    def getConstraintValue(self, constraint):
        return self.constraints[constraint]
    
    def copy(self):
        return deepcopy(self)
    
    def satisfiesConstraints(self, constraints):
        pass

class SquareWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(SquareWangTile, self).__init__(width, width, tiles)
        
        # Initialize constraints dict
        self.constraints = {'A' : None, 'B' : None, 'C' : None, 'D' : None}
        
        self.readConstraints()
        
    def readConstraints(self):
        pass
    

class HRectWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(HRectWangTile, self).__init__(width, width/2., tiles)
        
        # Initialize constraints dict
        self.constraints = {'A' : None, 'B' : None, 'C' : None,
                            'D' : None, 'E' : None, 'F' : None}
        
        self.readConstraints()
        
    def readConstraints(self):
        pass


class VRectWangTile(WangTile):
    
    def __init__(self, width, tiles):
        super(VRectWangTile, self).__init__(width, width*2, tiles)
        
        # Initialize constraints dict
        self.constraints = {'G' : None, 'H' : None, 'I' : None,
                            'J' : None, 'K' : None, 'L' : None}
        
        self.readConstraints()
        
    def readConstraints(self):
        pass


class WangTileSet(object):
    
    def readFromFile(self, filename):
        pass
    
    def getTileWithConstraints(self, constraints):
        pass

class SquareWangTileSet(WangTileSet):
    
    def buildTile(self, tilestr):
        pass

class HerringboneWangTileSet(WangTileSet):
    
    def buildTile(self, tilestr):
        pass
    

class WangTileMap(object):
    pass

class SquareWangTileMap(WangTileMap):
    pass

class HerringboneWangTileMap(WangTileMap):
    pass
