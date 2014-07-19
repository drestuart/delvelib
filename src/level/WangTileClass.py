'''
##########################################################
#
# Created on Jul 11, 2014
#
# Implemented by Dan Stuart
# from the Herringbone Wang Tile algorithm by Sean Barrett:
# http://nothings.org/gamedev/herringbone/
# Retrieved 7/11/2014
# @author: dstuart
#
##########################################################
'''

from copy import deepcopy
import re
import random

class WangTile(object):
    
    defaultConstraint = None

    def __init__(self, tiles, **kwargs):
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.tiles = tiles

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
        raise NotImplementedError()
    

class SquareWangTile(WangTile):
    
    def __init__(self, tiles, **kwargs):
        super(SquareWangTile, self).__init__(tiles, **kwargs)
        
        # Initialize constraints dict
        self.constraints = {'A' : None, 'B' : None, 'C' : None, 'D' : None}
        
        self.readConstraints()
        
    def readConstraints(self):
        raise NotImplementedError
    
class TownWangTile(SquareWangTile):
    
    defaultConstraint = None
    
    def readConstraints(self):
        '''
        ---B---
        |     |
        A     C
        |     |
        ---D---
        '''
        self.centerx, self.centery = self.width/2, self.height/2
        
        constraintLocations = { 'A' : (0, self.centery),
                                'B' : (self.centerx, 0),
                                'C' : (self.width - 1, self.centery),
                                'D' : (self.centerx, self.height - 1)}
        
        constraintTypes = {'.' : 1, '~' : 2}
        
        for k in constraintLocations.keys():
            loc = constraintLocations[k]
            tile = self.getTile(loc[0], loc[1])
            self.constraints[k] = constraintTypes[tile]
        
    def satisfiesConstraints(self, constraints):
        for k, v in constraints.items():
            if v is not None and self.constraints[k] != v:
                return False
        
        return True


class HRectWangTile(WangTile):
    
    def __init__(self, tiles, **kwargs):
        super(HRectWangTile, self).__init__(tiles, **kwargs)
        
        # Initialize constraints dict
        self.constraints = {'A' : None, 'B' : None, 'C' : None,
                            'D' : None, 'E' : None, 'F' : None}
        
        self.readConstraints()


class VRectWangTile(WangTile):
    
    def __init__(self, tiles, **kwargs):
        super(VRectWangTile, self).__init__(tiles, **kwargs)
        
        # Initialize constraints dict
        self.constraints = {'G' : None, 'H' : None, 'I' : None,
                            'J' : None, 'K' : None, 'L' : None}
        
        self.readConstraints()


class WangTileSet(object):

    def __init__(self, tileClass):
        self.tileClass = tileClass
        self.defaultConstraint = tileClass.defaultConstraint
        self.tileWidth = None
        self.tileHeight = None
        self.wangTiles = []
        
    def getDefaultConstraint(self):
        return self.defaultConstraint
    
    def readFromFile(self, filename):
        tileMap = None
        glyphs = None
        
        f = open(filename, 'r')
        lnum = 0
        
        for line in f:
            line = line.strip()
            lnum += 1
            
            # Skip comments
            if re.match(r"//", line):
                continue
            
            # Check for height and width specs before reading any tiles
            if self.tileWidth == None:
                if not line.startswith('width'):
                    continue
                
                m = re.search(r"^width: (\d+)\s*height: (\d+)", line)
                if m:
                    self.tileWidth = int(m.group(1))
                    self.tileHeight = int(m.group(2))
                else:
                    raise Exception("Bad tile description line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            if glyphs == None and line.startswith('glyphs'):
                m = re.search(r"^glyphs: (.+)$", line)
                if m:
                    glyphs = m.group(1)
                else:
                    raise Exception("Bad glyph line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            
            if tileMap == None:
                if line == "":
                    continue
                
                if line == "*TILE*":
                    tileMap = []
                    continue
            
            else:
                if line == "":
                    # Finish off tile if it's tall enough
                    if len(tileMap) < self.tileHeight:
                        raise Exception("Unexpected end of tile map after only " + len(tileMap) + " lines. " +
                                        filename + " line " + str(lnum))
                    
                    elif len(tileMap) > self.tileHeight:
                        raise Exception("Tile map too tall: " + len(tileMap) + " lines. " +
                                        filename + " line " + str(lnum))
                    
                    # Add this tile to the list and reset for the next one
                    self.buildTile(tileMap)
                    tileMap = None
                    continue
                
                # Check line width
                if len(line) != self.tileWidth:
                    raise Exception("Tile line is the wrong width: " + line + ": " +
                                        filename + " line " + str(lnum))
                
                # Check that the line includes only the allowed glyphs
                if not (re.match("^[" + re.escape(glyphs) + "]+$", line)):
                    raise Exception("Bad map line: " + line + " " + filename + " line " + str(lnum))
                
                tileMap.append(line)
        else:
            # At the end of the file, save the last tileMap if we haven't already
            f.close()
            
            if tileMap == None:
                return
            
            if len(tileMap) < self.tileHeight:
                raise Exception("Unexpected end of tile map after only " + len(tileMap) + " lines. " +
                                filename + " line " + lnum)
            
            elif len(tileMap) > self.tileHeight:
                raise Exception("Tile map too tall: " + len(tileMap) + " lines. " +
                                filename + " line " + str(lnum))
                
            # Add this tile to the list and reset for the next one
            self.buildTile(tileMap)
            tileMap = None
        
    
    def getTilesWithConstraints(self, constraints):
        goodTiles = []
        for tile in self.wangTiles:
            if tile.satisfiesConstraints(constraints):
                goodTiles.append(tile)
                
        return goodTiles

    def getRandomTileWithConstraints(self, constraints):
        return random.choice(self.getTilesWithConstraints(constraints))

    def buildTile(self, squares):
        newTile = self.tileClass(squares, width = self.tileWidth, height = self.tileHeight)
        self.wangTiles.append(newTile)


def main():
    wset = WangTileSet(TownWangTile)
    wset.readFromFile("wangtiletest.txt")
    
    print wset.getRandomTileWithConstraints({'A' : None, 'B' : 1, 'C' : 2, 'D' : None}).getTiles()


if __name__ == "__main__":
    main()