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
    
    def __init__(self):
        self.tileWidth = None
        self.tileHeight = None
        self.wangTiles = []
    
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
                    print self.tileWidth, self.tileHeight
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
                    self.wangTiles.append(tileMap)
                    tileMap = None
                    continue
                
                # Check line width
                if len(line) != self.tileWidth:
                    raise Exception("Tile line is the wrong width: " + line + ": " +
                                        filename + " line " + str(lnum))
                
                # Check that the line includes only the allowed glyphs
                if not (re.match("^[" + glyphs + "]+$", line)):
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
            self.wangTiles.append(tileMap)
            tileMap = None
        
    
    def getTileWithConstraints(self, constraints):
        pass

class SquareWangTileSet(WangTileSet):
    
    def buildTile(self, tilestr):
        pass

class HerringboneWangTileSet(WangTileSet):
    
    def buildTile(self, tilestr):
        pass


def main():
    wset = SquareWangTileSet()
    wset.readFromFile("wangtiletest.txt")
    
    for tile in wset.wangTiles:
        print tile


if __name__ == "__main__":
    main()