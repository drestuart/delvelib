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

    def __init__(self, tiles, constraints, **kwargs):
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.tiles = tiles
        self.constraints = constraints

    def getTiles(self):
        return self.tiles
    
    def getTile(self, x, y):
        return self.tiles[y][x]
    
    def getCoords(self):
        return self.coords
    
    def setCoords(self, coords):
        self.x, self.y = coords # Top-left corner coords
    
    def getConstraints(self):
        return self.constraints
    
    def getConstraintValue(self, constraint):
        return self.constraints[constraint]
    
    def satisfiesConstraints(self, constraints):
        raise NotImplementedError()
    

class SquareWangTile(WangTile):

    # Initialize constraints dict
    constraintSites = {'A' : None, 'B' : None, 'C' : None, 'D' : None}
    
class TownWangTile(SquareWangTile):
    
    defaultConstraint = None
    
    def satisfiesConstraints(self, constraints):
        for k, v in constraints.items():
            if v is not None and self.constraints[k] != v:
                return False
        return True

class RectangularWangTile(WangTile):
    defaultConstraint = None
    tileClass = SquareWangTile

    def getTile(self, x, y):
        raise NotImplementedError
    
    def getConstraintValue(self, constraint):
        raise NotImplementedError
    
    def satisfiesConstraints(self, constraints):
        raise NotImplementedError()
    
    

class HorzWangTile(RectangularWangTile):
    
    # Initialize constraints dict
    constraintSites = {'A' : None, 'B' : None, 'C' : None,
                       'D' : None, 'E' : None, 'F' : None}
    
    def __init__(self, tiles, constraints, **kwargs):
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.constraints = constraints
        
        # Divide tiles into left and right halves
        leftTiles = []
        rightTiles = []
        for row in tiles:
            leftTiles.append(row[:self.width/2])
            rightTiles.append(row[self.width/2:])
            
        leftTileConstraints = {'A' : constraints['A'], 'B' : constraints['B'], 'C' : None, 'D' : constraints['F']}
        rightTileConstraints = {'A' : None, 'B' : constraints['C'], 'C' : constraints['D'], 'D' : constraints['E']}
        
        # Initialize left and right tiles
        self.leftTile = self.tileClass(leftTiles, leftTileConstraints, width = self.width/2, height = self.height)
        self.rightTile = self.tileClass(rightTiles, rightTileConstraints, width = self.width/2, height = self.height)
        

    def getLeftTile(self):
        return self.leftTile
    
    def getRightTile(self):
        return self.rightTile
    
    def getConstraintValue(self, constraint):
        if constraint in 'ABF':
            newConstraint = {'A' : 'A', 'B': 'B', 'F' : 'D'}[constraint]
            return self.leftTile.getConstraintValue(newConstraint)
        elif constraint in 'CDE':
            newConstraint = {'C' : 'B', 'D': 'C', 'E' : 'D'}[constraint]
            return self.rightTile.getConstraintValue(newConstraint)
        else:
            raise ValueError(constraint)


class VertWangTile(RectangularWangTile):
    
    # Initialize constraints dict
    constraintSites = {'G' : None, 'H' : None, 'I' : None,
                       'J' : None, 'K' : None, 'L' : None}
    
    def __init__(self, tiles, constraints, **kwargs):
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.constraints = constraints
        
        # Divide tiles into top and bottom halves
        topTiles = tiles[:self.height/2]
        bottomTiles = tiles[self.height/2:]
        
        # Translate constraints
        topTileConstraints = {'A' : constraints['G'], 'B': constraints['H'], 'C' : constraints['I'], 'D': None}
        bottomTileConstraints = {'A' : constraints['L'], 'B': None, 'C' : constraints['J'], 'D': constraints['K']}
        
        # Initialize top and bottom tiles
        self.topTile = self.tileClass(topTiles, topTileConstraints, width = self.width, height = self.height/2)
        self.bottomTile = self.tileClass(bottomTiles, bottomTileConstraints, width = self.width, height = self.height/2)
        
        
    def getTopTile(self):
        return self.topTile
    
    def getBottomTile(self):
        return self.bottomTile
    
    def getConstraintValue(self, constraint):
        if constraint in 'GHI':
            newConstraint = {'G' : 'A', 'H': 'B', 'I' : 'C'}[constraint]
            return self.topTile.getConstraintValue(newConstraint)
        elif constraint in 'JKL':
            newConstraint = {'J' : 'C', 'K': 'D', 'L' : 'A'}[constraint]
            return self.bottomTile.getConstraintValue(newConstraint)
        else:
            raise ValueError(constraint)

class WangTileSet(object):

    def __init__(self, tileClass):
        self.tileClass = tileClass
        self.defaultConstraint = tileClass.defaultConstraint
        self.tileWidth = None
        self.tileHeight = None
        self.wangTiles = []
        self.specialTiles = {}
        
    def getDefaultConstraint(self):
        return self.defaultConstraint
    
    def readFromFile(self, filename):
        tileMap = None
        glyphs = None
        tileType = None
        constraintDict = None
        
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
                
#                 if line == "*TILE*":
                m = re.match(r"\*(\w+)\*$", line)
                if m:
                    tileType = m.group(1)
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
                    self.buildTile(tileMap, constraintDict, tileType)
                    tileMap = None
                    tileType = None
                    constraintDict = None
                    continue
                
                m = re.match(r"constraints: (\d+)$", line)
                if m:
                    constraintStr = m.group(1)
                    constraintDict = deepcopy(self.tileClass.constraintSites)
                    
                    i = 0
                    for k in sorted(constraintDict.keys()):
                        constraintDict[k] = constraintStr[i]
                        i += 1
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
            self.buildTile(tileMap, constraintDict, tileType)
            tileMap = None
            tileType = None
            constraintDict = None
        
        print len(self.wangTiles)
        
    
    def getTilesWithConstraints(self, constraints):
        goodTiles = []
        for tile in self.wangTiles:
            if tile.satisfiesConstraints(constraints):
                goodTiles.append(tile)
                
        return goodTiles

    def getRandomTileWithConstraints(self, constraints):
        return random.choice(self.getTilesWithConstraints(constraints))

    def buildTile(self, squares, constraints, tileType):
        newTile = self.tileClass(squares, constraints, width = self.tileWidth, height = self.tileHeight)
        if (tileType.lower() == "tile"):
            self.wangTiles.append(newTile)
        else:
            self.specialTiles[tileType] = newTile


def main():
    vertRows = ['..+..',
                '..+..',
                '..+..',
                '..+..',
                '+++++',
                '+++++',
                '..+..',
                '..+..',
                '..+..',
                '..+..']
    
    horzRows = ['....++....',
                '....++....',
                '++++++++++',
                '....++....',
                '....++....']
    
    vtile = VertWangTile(vertRows, {'G' : 1, 'H' : 2, 'I' : 1, 'J' : 1, 'K' : 2, 'L' : 1}, width = 5, height = 10)
    htile = HorzWangTile(horzRows, {'A' : 2, 'B' : 1, 'C' : 1, 'D' : 2, 'E' : 1, 'F' : 1}, width = 10, height = 5)
    
    print vertRows
    print vtile.getTopTile().getTiles()
    print vtile.getBottomTile().getTiles()
    print vtile.getConstraintValue('G')
    
    print
    
    print horzRows
    print htile.getLeftTile().getTiles()
    print htile.getRightTile().getTiles()
    print htile.getConstraintValue('D')

if __name__ == "__main__":
    main()