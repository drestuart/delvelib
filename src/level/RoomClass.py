'''
Created on Mar 10, 2013

@author: dstu
'''

# The Rectangle class
class Rect(object):
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def getX1(self):
        return self.x1

    def getY1(self):
        return self.y1

    def getX2(self):
        return self.x2

    def getY2(self):
        return self.y2

    def getCenterX(self):
        return self.centerX

    def getCenterY(self):
        return self.centerY

    def setX1(self, value):
        self.x1 = value

    def setY1(self, value):
        self.y1 = value

    def setX2(self, value):
        self.x2 = value

    def setY2(self, value):
        self.y2 = value

    def setCenterX(self, value):
        self.centerX = value

    def setCenterY(self, value):
        self.centerY = value

    def delX1(self):
        del self.x1

    def delY1(self):
        del self.y1

    def delX2(self):
        del self.x2

    def delY2(self):
        del self.y2

    def delCenterX(self):
        del self.centerX

    def delCenterY(self):
        del self.centerY

    def getCenter(self):
        self.centerX = (self.x1 + self.x2) / 2
        self.centerY = (self.y1 + self.y2) / 2
        return (self.centerX, self.centerY)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
        
    def contains(self, x, y):
        return (self.x1 <= x and self.x2 >= x and
                self.y1 <= y and self.y2 >= y)


class Room():
    
    def __init__(self, **kwargs):
        self.tiles = set()
        self.level = None
    
    def getLevel(self):
        return self.level
    
    def setLevel(self, value):
        self.level = value
        if self not in self.level.getRooms():
            self.level.addRoom(self)

    def getTiles(self):
        return self.tiles
    
    def addTile(self, tile):
        self.tiles.add(tile)
        if tile.getRoom() is not self:
            tile.setRoom(self)

