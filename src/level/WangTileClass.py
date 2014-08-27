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
from Util import rotateCW, rotateCCW, printArray

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
    
#     def satisfiesConstraints(self, constraints):
#         raise NotImplementedError()
    def satisfiesConstraints(self, constraints):
        for k, v in constraints.items():
            if v is not None and self.constraints[k] != v:
                return False
        return True

class SquareWangTile(WangTile):

    # Initialize constraints dict
    constraintSites = {'A' : None, 'B' : None, 'C' : None, 'D' : None}
    
class TownWangTile(SquareWangTile):
    
    defaultConstraint = None
    
#     def satisfiesConstraints(self, constraints):
#         for k, v in constraints.items():
#             if v is not None and self.constraints[k] != v:
#                 return False
#         return True

class RectangularWangTile(WangTile):
    defaultConstraint = None
    tileClass = SquareWangTile

    def getTile(self, x, y):
        raise NotImplementedError
    
    def getConstraintValue(self, constraint):
        raise NotImplementedError
    
#     def satisfiesConstraints(self, constraints):
#         raise NotImplementedError()
    
    

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
    
    def getTiles(self):
        left = self.leftTile.getTiles()
        right = self.rightTile.getTiles()
        rows = []
        
        for y in range(self.height):
            rows.append(left[y] + right[y])
        return rows
        
    def getConstraintValue(self, constraint):
        if constraint in 'ABF':
            newConstraint = {'A' : 'A', 'B': 'B', 'F' : 'D'}[constraint]
            return self.leftTile.getConstraintValue(newConstraint)
        elif constraint in 'CDE':
            newConstraint = {'C' : 'B', 'D': 'C', 'E' : 'D'}[constraint]
            return self.rightTile.getConstraintValue(newConstraint)
        else:
            raise ValueError(constraint)

class dungeonHTile(HorzWangTile):
    pass

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
    
    def getTiles(self):
        return self.topTile.getTiles() + self.bottomTile.getTiles()
    
    def getConstraintValue(self, constraint):
        if constraint in 'GHI':
            newConstraint = {'G' : 'A', 'H': 'B', 'I' : 'C'}[constraint]
            return self.topTile.getConstraintValue(newConstraint)
        elif constraint in 'JKL':
            newConstraint = {'J' : 'C', 'K': 'D', 'L' : 'A'}[constraint]
            return self.bottomTile.getConstraintValue(newConstraint)
        else:
            raise ValueError(constraint)
        
class dungeonVTile(VertWangTile):
    pass

class WangTileSet(object):

    def __init__(self):
        self.tileWidth = None
        self.tileHeight = None
        self.glyphs = None
        
    def getDefaultConstraint(self):
        return self.defaultConstraint
    
    def readFromFile(self, filename):
        tileMap = None
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
            
            # Read glyph list
            if self.glyphs == None and line.startswith('glyphs'):
                m = re.search(r"^glyphs: (.+)$", line)
                if m:
                    self.glyphs = m.group(1)
                else:
                    raise Exception("Bad glyph line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            # Read special glyphs
            if self.glyphs != None and line.startswith('wallglyph'):
                m = re.search(r"^wallglyph: (.)$", line)
                if m:
                    self.wallGlyph = m.group(1)
                else:
                    raise Exception("Bad wallglyph line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            if self.glyphs != None and line.startswith('roomglyphs'):
                m = re.search(r"^roomglyphs: (.+)$", line)
                if m:
                    self.roomGlyphs = m.group(1)
                else:
                    raise Exception("Bad roomglyphs line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            if self.glyphs != None and line.startswith('tunnelglyph'):
                m = re.search(r"^tunnelglyph: (.+)$", line)
                if m:
                    self.tunnelGlyph = m.group(1)
                else:
                    raise Exception("Bad tunnelglyph line: " + line + " " + filename + " line " + str(lnum))
                    
                continue
            
            # Look for a new tile
            if tileMap == None:
                if line == "":
                    continue
                
#                 if line == "*TILE*":
                m = re.match(r"\*(\w+)\*$", line)
                if m:
                    tileType = m.group(1)
                    tileMap = []
                    continue
            
            # Continue reading current tile
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
                if not (re.match("^[" + re.escape(self.glyphs) + "]+$", line)):
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
        
    
    def getTilesWithConstraints(self, constraints):
        goodTiles = []
        for tile in self.wangTiles:
            if tile.satisfiesConstraints(constraints):
                goodTiles.append(tile)
                
        return goodTiles

    def getRandomTile(self, constraints):
        return random.choice(self.getTilesWithConstraints(constraints))
    
class SquareWangTileSet(WangTileSet):
    
    def __init__(self, tileClass):
        super(SquareWangTileSet, self).__init__()
        self.tileClass = tileClass
        self.defaultConstraint = tileClass.defaultConstraint
        self.wangTiles = []
        self.specialTiles = {}


    def buildTile(self, squares, constraints, tileType):
        newTile = self.tileClass(squares, constraints, width = self.tileWidth, height = self.tileHeight)
        if (tileType.lower() == "tile"):
            self.wangTiles.append(newTile)
        else:
            self.specialTiles[tileType] = newTile
            
class RectWangTileSet(WangTileSet):
    
    def __init__(self, vTileClass, hTileClass):
        super(RectWangTileSet, self).__init__()
        self.vTileClass = vTileClass
        self.tileClass = vTileClass
        self.hTileClass = hTileClass
        self.defaultConstraint = vTileClass.defaultConstraint
        self.vWangTiles = []
        self.hWangTiles = []
        self.specialTiles = {}

    
    def buildTile(self, squares, constraints, tileType):
        # Build vertical tiles
        newVTile = self.vTileClass(squares, constraints, width = self.tileWidth, height = self.tileHeight)
        
        constraints180 = self.rotateConstraints(constraints, 180)
        newVTile180 = self.vTileClass(rotateCW(rotateCW(squares)), constraints180, width = self.tileWidth, height = self.tileHeight)
        
        # Build horizontal tiles
        constraints90 = self.rotateConstraints(constraints, 90)
        newHTile90 = self.hTileClass(rotateCW(squares), constraints90, width = self.tileHeight, height = self.tileWidth)
        
        constraints270 = self.rotateConstraints(constraints, 270)
        newHTile270 = self.hTileClass(rotateCCW(squares), constraints270, width = self.tileHeight, height = self.tileWidth)
        
        if (tileType.lower() == "tile"):
            self.vWangTiles += [newVTile, newVTile180]
            self.hWangTiles += [newHTile90, newHTile270]
            
    def rotateConstraints(self, constraints, angle):
        newConstraints = {}
        
        if angle == 90:
            newConstraints = {'A' : constraints['K'], 'B' : constraints['L'], 'C' : constraints['G'],
                              'D' : constraints['H'], 'E' : constraints['I'], 'F' : constraints['J']}
            
        elif angle == 180:
            newConstraints = {'G' : constraints['J'], 'H' : constraints['K'], 'I' : constraints['L'],
                              'J' : constraints['G'], 'K' : constraints['H'], 'L' : constraints['I']}
            
        elif angle == 270:
            newConstraints = {'A' : constraints['H'], 'B' : constraints['I'], 'C' : constraints['J'],
                              'D' : constraints['K'], 'E' : constraints['L'], 'F' : constraints['G']}
            
        else:
            raise ValueError(angle)
        
        return newConstraints
    
    def getTilesWithConstraints(self, constraints, tileList):
        goodTiles = []
        for tile in tileList:
            if tile.satisfiesConstraints(constraints):
                goodTiles.append(tile)
                
        return goodTiles
    
    def getRandomVTile(self, constraints):
        return random.choice(self.getTilesWithConstraints(constraints, self.vWangTiles))
    
    def getRandomHTile(self, constraints):
        return random.choice(self.getTilesWithConstraints(constraints, self.hWangTiles))
    

def main():
    rset = RectWangTileSet(dungeonVTile, dungeonHTile)
    rset.tileWidth = 11
    rset.tileHeight = 22
    rset.glyphs = "#,."
    
    squares = ["#####,#####",
               "#####,#####",
               ",,##,,#,,,,",
               "#,##,##,###",
               "#,##,##,###",
               "#,##,##,,##",
               "#,##,,##,##",
               "#,###,##,##",
               "#+###+##+##",
               "#.........#",
               "#.........#",
               "#.........#",
               "#.........#",
               "###########",
               "###########",
               "######,,,##",
               "####,,,#,,,",
               "####+######",
               "......#####",
               "......#####",
               "......#####",
               "#...#+#####"]
    constraints = {'G' : '2', 'H' : '1', 'I': '2', 'J' : '1', 'K' : '1', 'L': '2'}
    
    rset.buildTile(squares, constraints, "tile")
    
    printArray(rset.vWangTiles[0].getTiles())
    print rset.vWangTiles[0].getConstraints()
    printArray(rset.vWangTiles[1].getTiles())
    print rset.vWangTiles[1].getConstraints()
    
    printArray(rset.hWangTiles[0].getTiles())
    print rset.hWangTiles[0].getConstraints()
    printArray(rset.hWangTiles[1].getTiles())
    print rset.hWangTiles[1].getConstraints()

if __name__ == "__main__":
    main()