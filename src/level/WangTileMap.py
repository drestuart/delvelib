'''
Created on Jul 18, 2014

@author: dstuart
'''

from WangTileClass import SquareWangTileSet, TownWangTile, RectWangTileSet, dungeonVTile, dungeonHTile



class WangTileMap(object):
    def __init__(self, tilesWide, tilesHigh):
        self.tilesWide = tilesWide
        self.tilesHigh = tilesHigh
    
    def getWangTile(self, x, y):
        try:
            return self.wangTiles[y][x]
        except (KeyError, IndexError):
            return None
        
    def hasTile(self, x, y):
        return (True if self.getWangTile(x, y) else False)
        
    def addWangTile(self, x, y, tile):
        self.wangTiles[y][x] = tile
        
    def inBounds(self, x, y):
        return (x >= 0 and x < self.tilesWide and y >= 0 and y < self.tilesHigh)


class SquareWangTileMap(WangTileMap):
    def __init__(self, tilesWide, tilesHigh):
        super(SquareWangTileMap, self).__init__(tilesWide, tilesHigh)
        
        self.wangTiles = []
        for y in range(self.tilesHigh):
            row = []
            for x in range(self.tilesWide):
                row.append(None)
            self.wangTiles.append(row)
                
    def getConstriants(self, x, y):
        '''
        ---B---
        |     |
        A     C
        |     |
        ---D---
        '''
        tileLeft = self.getWangTile(x - 1, y)
        tileUp = self.getWangTile(x, y - 1)
        tileRight = self.getWangTile(x + 1, y)
        tileDown = self.getWangTile(x, y + 1)
        
        constraints = { 'A' : tileLeft.getConstraintValue('C') 
                            if tileLeft is not None 
                            else self.tileset.getDefaultConstraint(),
                        'B' : tileUp.getConstraintValue('D') 
                            if tileUp is not None 
                            else self.tileset.getDefaultConstraint(),
                        'C' : tileRight.getConstraintValue('A') 
                            if tileRight is not None 
                            else self.tileset.getDefaultConstraint(),
                        'D' : tileDown.getConstraintValue('B') 
                            if tileDown is not None 
                            else self.tileset.getDefaultConstraint()}
        
        return constraints
    
    def buildMap(self):
        for y in range(self.tilesHigh):
            for x in range(self.tilesWide):
                constraints = self.getConstriants(x, y)
                newTile = self.tileset.getRandomTile(constraints)
                self.addWangTile(x, y, newTile)
                
    def printMap(self):
        for tiley in range(self.tilesHigh):
            for i in range(self.tileset.tileHeight):
                row = ""
                for tilex in range(self.tilesWide):
                    wtile = self.getWangTile(tilex, tiley)
                    row += wtile.getTiles()[i]
                print row

class TownMap(SquareWangTileMap):
    def __init__(self, *args):
        super(TownMap, self).__init__(*args)
        self.tileset = SquareWangTileSet(TownWangTile)
        self.tileset.readFromFile("towntiles.txt")
        print len(self.tileset.wangTiles)
    

class HerringboneWangTileMap(WangTileMap):
    def __init__(self, tilesWide, tilesHigh, **kwargs):
        super(HerringboneWangTileMap, self).__init__(tilesWide, tilesHigh)
        self.margin = kwargs.get("margin", 0)
        
        # Initialize wang tile structure for underlying square tiles
        # To simplify reading out map data
        self.wangTiles = {}
        for y in range(-1, self.tilesHigh + 1):
            self.wangTiles[y] = {}
            for x in range(-1, self.tilesWide + 1):
                self.wangTiles[y][x] = None
            
        # Initialize a similar structure to keep track of the rectangular tiles
        # For constraint purposes
        self.rTiles = {}
        for y in range(-1, self.tilesHigh + 1):
            self.rTiles[y] = {}
            for x in range(-1, self.tilesWide + 1):
                self.rTiles[y][x] = None
            
    def addRTile(self, x, y, tile):
        self.rTiles[y][x] = tile
        
    def getRTile(self, x, y):
        try:
            return self.rTiles[y][x]
        except KeyError:
            return None
        
    def hasRTile(self, x, y):
        return (True if self.getRTile(x, y) else False)
    
    def getConstraintAtPosition(self, x, y, constraintName):
#         print "Getting constraint", constraintName, "at position", (x, y)
        tile = self.getRTile(x, y)
        if tile:
#             print tile.__class__
            return tile.getConstraintValue(constraintName)
        return None
        
    def buildMap(self):
        
        startingStepsAndOffsets = [("placeHorz", 0),
                                   ("placeVert", 0),
                                   ("placeHorz", 2),
                                   ("placeHorz", -1)]
        
        vConstraintCoords = {"G" : (-1, 0, "J"),
                             "H" : (0, -1, "F"),
                             "I" : (1, 0, "A"),
                             "J" : (1, 1, "G"),
                             "K" : (0, 2, "C"),
                             "L" : (-1, 1, "D")}
        
        hConstraintCoords = {"A" : (-1, 0, "I"),
                             "B" : (0, -1, "E"),
                             "C" : (1, -1, "K"),
                             "D" : (2, 0, "L"),
                             "E" : (1, 1, "B"),
                             "F" : (0, 1, "H")}
        
        step, offset = startingStepsAndOffsets[0]
        
        currentX = offset
        currentY = 0
        
        # In some cases an extra row is required to fill in the last desired row!
        # Specifically when self.tilesHigh % 4 == 3
        while currentY < self.tilesHigh + 1: 
            if step == "placeHorz":

                # Place horizontal tile
                if not self.hasTile(currentX, currentY):
                    
                    # Read constraints from adjacent tiles
                    constraints = {}
                    
                    for k, v in hConstraintCoords.items():
                        dx, dy, constraintName = v
                        constraints[k] = self.getConstraintAtPosition(currentX + dx, currentY + dy, constraintName)

                    # Get random tile
                    tile = self.tileset.getRandomHTile(constraints)
                    
                    # Place it
                    self.placeTile(tile, currentX, currentY)
                
                currentX += 2
                
                # Place vertical tile up
                # Top-left corner is one row up!
                tilex, tiley = currentX, currentY - 1
                
                if not self.hasTile(tilex, tiley):
                    
                    # Read constraints from adjacent tiles
                    constraints = {}
                    
                    for k, v in vConstraintCoords.items():
                        dx, dy, constraintName = v
                        constraints[k] = self.getConstraintAtPosition(tilex + dx, tiley + dy, constraintName)

                    # Get random tile
                    tile = self.tileset.getRandomVTile(constraints)
                    
                    # Place it
                    self.placeTile(tile, tilex, tiley)
                
                currentX += 1
                
                step = "placeVert"
                
            elif step == "placeVert":
                
                if not self.hasTile(currentX, currentY):

                    # Read constraints from adjacent tiles
                    constraints = {}
                    
                    for k, v in vConstraintCoords.items():
                        dx, dy, constraintName = v
                        constraints[k] = self.getConstraintAtPosition(currentX + dx, currentY + dy, constraintName)

                    # Get random tile
                    tile = self.tileset.getRandomVTile(constraints)
                    
                    # Place it
                    self.placeTile(tile, currentX, currentY)
                
                currentX += 1
                step = "placeHorz"
                
            # Move to the next row
            if currentX >= self.tilesWide:
                currentY += 1
                
                # Get the next set of offset and first step.
                # This starts over in the list after the last element
                step, offset = startingStepsAndOffsets[currentY % len(startingStepsAndOffsets)]
                currentX = offset
                
        
    def placeTile(self, tile, x, y):
        
        # Vertical tile
        if isinstance(tile, self.tileset.vTileClass):
            topTile = tile.getTopTile()
            bottomTile = tile.getBottomTile()
            
            # Place top tile
            if self.inBounds(x, y) and not self.getWangTile(x, y):
                self.addWangTile(x, y, topTile)
                self.addRTile(x, y, tile)
                
            # Place bottom tile
            if self.inBounds(x, y + 1) and not self.getWangTile(x, y + 1):
                self.addWangTile(x, y + 1, bottomTile)
                self.addRTile(x, y + 1, tile)
        
        
        # Horizontal tile
        elif isinstance(tile, self.tileset.hTileClass):
            leftTile = tile.getLeftTile()
            rightTile = tile.getRightTile()
            
            # Place left tile
            if self.inBounds(x, y) and not self.getWangTile(x, y):
                self.addWangTile(x, y, leftTile)
                self.addRTile(x, y, tile)
                
            # Place right tile
            if self.inBounds(x + 1, y) and not self.getWangTile(x + 1, y):
                self.addWangTile(x + 1, y, rightTile)
                self.addRTile(x + 1, y, tile)
        

    def printMap(self):
        for row in self.getMapGlyphs():
            print row
    
    def getMapGlyphs(self):
        wallGlyph = self.tileset.wallGlyph
        retMap = []
        tileWidth = self.tileset.tileWidth
        
        # Top wall margin
        if self.margin:
            for dummy in range(self.margin):
                retMap.append(wallGlyph*(self.tilesWide * tileWidth + 2*self.margin))
        
        for tiley in range(self.tilesHigh):
            for i in range(tileWidth):
                row = ""
                
                # Left wall margin
                if self.margin:
                    row += wallGlyph*self.margin
                
                for tilex in range(self.tilesWide):
                    wtile = self.getWangTile(tilex, tiley)
                    if wtile:
                        row += "".join(wtile.getTiles()[i])
                    else:
                        row += "x"*self.tileset.tileWidth
                        
                # Right wall margin
                if self.margin:
                    row += wallGlyph*self.margin
                    
                retMap.append(row)
                
        # Bottom wall margin
        if self.margin:
            for dummy in range(self.margin):
                retMap.append(wallGlyph*(self.tilesWide * tileWidth + 2*self.margin))
                
        return retMap
    

class DungeonMap(HerringboneWangTileMap):
    def __init__(self, *args, **kwargs):
        super(DungeonMap, self).__init__(*args, **kwargs)
        self.tileset = RectWangTileSet(dungeonVTile, dungeonHTile)
        self.tileset.readFromFile("dungeon_vtiles.txt")
        print len(self.tileset.vWangTiles) + len(self.tileset.hWangTiles)


def main():
#     townMap = TownMap(5, 5)
#     townMap.buildMap()
#     townMap.printMap()
    
    dungeonMap = DungeonMap(5, 5, margin = 1)
    dungeonMap.buildMap()
    dungeonMap.printMap()


if __name__ == "__main__":
    main()
