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
        except IndexError:
            return None
        
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
    def __init__(self, tilesWide, tilesHigh):
        super(HerringboneWangTileMap, self).__init__(tilesWide, tilesHigh)
        
    def buildMap(self):
        print "buildMap"
        
    def placeTile(self, tile, x, y):
        
        # Vertical tile
        if isinstance(tile, self.tileset.vTileClass):
            topTile = tile.getTopTile()
            bottomTile = tile.getBottomTile()
            
            # Place top tile
            if self.inBounds(x, y) and not self.getWangTile(x, y):
                self.addWangTile(x, y, topTile)
                
            # Place bottom tile
            if self.inBounds(x, y + 1) and not self.getWangTile(x, y + 1):
                self.addWangTile(x, y + 1, bottomTile)
        
        
        # Horizontal tile
        elif isinstance(tile, self.tileset.hTileClass):
            leftTile = tile.getLeftTile()
            rightTile = tile.getRightTile()
            
            # Place left tile
            if self.inBounds(x, y) and not self.getWangTile(x, y):
                self.addWangTile(x, y, leftTile)
                
            # Place right tile
            if self.inBounds(x + 1, y) and not self.getWangTile(x + 1, y):
                self.addWangTile(x + 1, y, rightTile)
        

    def printMap(self):
        '''
        Copied from SquareWangTileMap.  Could work?
        '''
        for tiley in range(self.tilesHigh):
            for i in range(self.tileset.tileHeight):
                row = ""
                for tilex in range(self.tilesWide):
                    wtile = self.getWangTile(tilex, tiley)
                    row += wtile.getTiles()[i]
                print row
    

class DungeonMap(HerringboneWangTileMap):
    def __init__(self, *args):
        super(DungeonMap, self).__init__(*args)
        self.tileset = RectWangTileSet(dungeonVTile, dungeonHTile)
        self.tileset.readFromFile("dungeon_vtiles.txt")
        print len(self.tileset.vWangTiles) + len(self.tileset.hWangTiles)


def main():
    townMap = TownMap(5, 5)
    townMap.buildMap()
    townMap.printMap()
    
    dungeonMap = DungeonMap(5, 5)
    dungeonMap.buildMap()
    dungeonMap.printMap()

if __name__ == "__main__":
    main()
