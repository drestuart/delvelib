'''
Created on Jul 18, 2014

@author: dstuart
'''

from WangTileClass import WangTileSet, TownWangTile

townset = WangTileSet(TownWangTile)
townset.readFromFile("wangtiletest.txt")


class WangTileMap(object):
    def __init__(self):
        pass
    
    def getWangTile(self, x, y):
        try:
            return self.wangTiles[y][x]
        except IndexError:
            return None
        
    def addWangTile(self, x, y, tile):
        self.wangTiles[y][x] = tile


class SquareWangTileMap(WangTileMap):
    def __init__(self, tilesWide, tilesHigh):
        super(SquareWangTileMap, self).__init__()
        self.tilesWide = tilesWide
        self.tilesHigh = tilesHigh
        
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
                newTile = self.tileset.getRandomTileWithConstraints(constraints)
                self.addWangTile(x, y, newTile)
                
    def printMap(self):
        for tiley in range(self.tilesHigh):
            for i in range(self.tileset.tileHeight):
                row = ""
                for tilex in range(self.tilesWide):
                    wtile = self.getWangTile(tilex, tiley)
                    row += wtile.getTiles()[i]
                print row

class TownWangTileMap(SquareWangTileMap):
    
    tileset = townset
    

class HerringboneWangTileMap(WangTileMap):
    pass


def main():
    townMap = TownWangTileMap(5, 5)
    townMap.buildMap()
    townMap.printMap()

if __name__ == "__main__":
    main()
