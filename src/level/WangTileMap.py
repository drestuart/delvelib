'''
Created on Jul 18, 2014

@author: dstuart
'''

from WangTileClass import SquareWangTileSet, TownWangTile, RectWangTileSet, dungeonVTile, dungeonHTile
from sys import maxint
from Util import ManhattanDistance
import random

class WangTileMap(object):
    def __init__(self, tilesWide, tilesHigh):
        self.tilesWide = tilesWide
        self.tilesHigh = tilesHigh
        self.levelMap = None
    
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
        
        self.buildMap()
                
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
        for row in self.getMapGlyphs():
            print row
    
    def getMapGlyphs(self):
        if self.levelMap != None:
            return self.levelMap
        
        retMap = []
        
        for tiley in range(self.tilesHigh):
            for i in range(self.tileset.tileHeight):
                row = ""
                for tilex in range(self.tilesWide):
                    wtile = self.getWangTile(tilex, tiley)
                    row += wtile.getTiles()[i]
                retMap.append(row)
        
        self.levelMap = retMap
        return retMap

class TownMap(SquareWangTileMap):
    def __init__(self, *args):
        self.tileset = SquareWangTileSet(TownWangTile)
        self.tileset.readFromFile("towntiles.txt")
        super(TownMap, self).__init__(*args)
    

class HerringboneWangTileMap(WangTileMap):
    def __init__(self, tilesWide, tilesHigh, **kwargs):
        super(HerringboneWangTileMap, self).__init__(tilesWide, tilesHigh)
        self.margin = kwargs.get("margin", 0)
        self.rooms = None
        
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
                
        # Build the map!
        self.buildMap()
        self.findRooms()
        self.enforceConnectivity()
            
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
        if self.levelMap != None:
            return self.levelMap
        
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
        
        self.levelMap = retMap
        return retMap
    
    def getRooms(self):
        return self.rooms
    
    def findRooms(self):
        if self.rooms != None:
            return self.rooms
        
        if self.levelMap == None:
            self.getMapGlyphs()
        
        roomGlyphs = self.tileset.roomGlyphs
        
        self.mapHeight = len(self.levelMap)
        self.mapWidth = len(self.levelMap[0])
        
        squaresSeen = []
        roomCoords = []
        
        # Recursive function aaaaaaaaaah
        def getConnectedRoomSquares(x, y):
            squaresSeen.append((x, y))
            toSearch = []
            thisRoom = [(x, y)]
            
            # Get adjacent (valid) coordinates
            if x > 0:
                toSearch.append((x-1, y))
                if y > 0:
                    toSearch.append((x-1, y-1))
            if x < self.mapWidth - 1:
                toSearch.append((x+1, y))
                if y < self.mapHeight - 1:
                    toSearch.append((x+1, y+1))
            
            if y > 0:
                toSearch.append((x, y-1))
                if x < self.mapWidth - 1:
                    toSearch.append((x+1, y-1))
            if y < self.mapHeight - 1:
                toSearch.append((x, y+1))
                if x > 0:
                    toSearch.append((x-1, y+1))
                
            for coords in toSearch:
                sx, sy = coords
                
                # Check that this is a valid square that we haven't seen before
                if not (sx, sy) in squaresSeen and self.levelMap[sy][sx] in roomGlyphs:
                    thisRoom += getConnectedRoomSquares(sx, sy)
            
            return thisRoom
        
        for y in range(self.mapHeight):
            row = self.levelMap[y]
            for x in range(self.mapWidth):
                square = row[x]
                if (x, y) in squaresSeen: continue
                if square not in roomGlyphs:
                    squaresSeen.append((x, y))
                    continue
                
                roomCoords.append(getConnectedRoomSquares(x, y))
        
        self.rooms = roomCoords
        return roomCoords
                
    def enforceConnectivity(self):
        # Set up AStar algo
        import AStar
        
        wallGlyph = self.tileset.wallGlyph
        mapdata = []

        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                square = self.levelMap[y][x]
                if square == wallGlyph:
                    mapdata.append(-1)
                else:
                    mapdata.append(1)
        
        self.astar = AStar.setUpMap(mapdata, self.mapWidth, self.mapHeight)
        
        # Find connected components
        connectedComponents = []
        
        # Start with first room
        connectedComponents.append([self.rooms[0]])
        
        # Look at all the others
        for room in self.rooms[1:]:
            connected = False
            fromx, fromy = room[0] # All rooms are simply connected, so choose the first square in each room
            
            for comp in connectedComponents:
                roomToFind = comp[0]
                tox, toy = roomToFind[0]
                
                path = AStar.findPath((fromx, fromy), (tox, toy), self.astar)
                
                if path is not None:
                    comp.append(room)
                    connected = True
                    break
            
            if connected == False:
                connectedComponents.append([room])
                
        if len(connectedComponents) == 1:
            # Nothing left to do
            return
        
        # Find the largest component by # of squares
        largestComp = None
        largestSize = 0
        
        for comp in connectedComponents:
            size = 0
            for room in comp:
                size += len(room)
            
            if size > largestSize:
                largestSize = size
                largestComp = comp
                
        # Connect each component to the largest one
        for comp in connectedComponents:
            if comp is largestComp:
                continue
            
            # Find the closest pairs of points in comp and largestComp
            closestPoints = []
            minDist = maxint
            
            # Loop over points in largestComp
            for p1 in [point for room in largestComp for point in room]:
                # Loop over points in comp
                for p2 in [point for room in comp for point in room]:
                    x1, y1 = p1
                    x2, y2 = p2
                    distance = ManhattanDistance(x1, x2, y1, y2)
                    
                    if distance < minDist:
                        closestPoints = [[p1, p2]]
                        minDist = distance
                    elif distance == minDist:
                        closestPoints.append([p1, p2])
            
            toPoint, fromPoint = random.choice(closestPoints)
            tox, toy = toPoint
            
            currentx, currenty = fromPoint
            tunnelGlyph = self.tileset.tunnelGlyph
            # Random-walk toward toPoint
            while True:
                dx = 0
                dy = 0
                
                if currentx < tox:
                    dx = 1
                elif currentx > tox:
                    dx = -1
                
                if currenty < toy:
                    dy = 1
                elif currenty > toy:
                    dy = -1
                    
                if dy == 0 or random.random() > 0.5:
                    # Step horizontally
                    nextx, nexty = currentx + dx, currenty
                else:
                    # Step vertically
                    nextx, nexty = currentx, currenty + dy
                
                # End if we're next to the goal square
                if (nextx, nexty) == (tox, toy):
                    break
                
                # Place a tunnel square
#                 self.levelMap[nexty][nextx] = tunnelGlyph
                # Silly stuff we have to do because strings are immutable
                row = self.levelMap[nexty]
                
                # Only replace wall squares
                if row[nextx] == wallGlyph:
                    rowl = list(row)
                    rowl[nextx] = tunnelGlyph
                    self.levelMap[nexty] = ''.join(rowl)
                
                currentx, currenty = nextx, nexty
                
                

class DungeonMap(HerringboneWangTileMap):
    def __init__(self, *args, **kwargs):
        self.tileset = RectWangTileSet(dungeonVTile, dungeonHTile)
        self.tileset.readFromFile("dungeon_vtiles.txt")
        super(DungeonMap, self).__init__(*args, **kwargs)


def main():
    townMap = TownMap(3, 3)
    townMap.printMap()
     
    print
    
    dungeonMap = DungeonMap(3, 3, margin = 1)
    dungeonMap.printMap()
    
if __name__ == "__main__":
    main()
