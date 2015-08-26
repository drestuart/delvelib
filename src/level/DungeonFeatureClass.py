'''
Created on Mar 12, 2013

@author: dstu
'''

from pubsub import pub
import colors
import symbols
import random

class DungeonFeature(colors.withBackgroundColor):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    description = u"dungeon feature"
    
    def __init__(self, symbol, **kwargs):
        super(DungeonFeature, self).__init__(**kwargs)
        self.symbol = symbol
        self.name = kwargs.get('name', None)
        self.tile = kwargs.get('tile', None)
        self.visible = kwargs.get('isVisible', True)
        
# TODO:
#     tileId = Column(Integer)
    
    def handleBump(self, creature):
        return False
    
    def isVisible(self):
        return self.visible
    
    def setVisible(self, val):
        self.visible = val

    def getBlockSight(self):
        return self.blockSight

    def getBlockMove(self):
        return self.blockMove

    def getSymbol(self):
        return self.symbol

    def getDescription(self):
        return self.description

    def getName(self):
        return self.name


    def getBaseSymbol(self):
        return self.baseSymbol


    def setBlockSight(self, value):
        self.blockSight = value


    def setBlockMove(self, value):
        self.blockMove = value


    def setSymbol(self, value):
        self.symbol = value

    def getTile(self):
        return self.tile
    
    def setTile(self, tile):
        self.tile = tile
        if tile.getFeature() is not self:
            tile.setFeature(self)

    def setName(self, value):
        self.name = value


    def setBaseSymbol(self, value):
        self.baseSymbol = value


class Door(DungeonFeature):
    
    color = colors.colorWood
    backgroundColor = colors.black
    description = u'a door'
    
    def __init__(self, **kwargs):
        super(Door, self).__init__(symbol = u'+', **kwargs)
        self.closed = True

    def open_(self):
        if self.isClosed():
            self.setClosed(False)
            pub.sendMessage("event.doorOpen", tile = self.tile)
            return True
        else:
            return False
        
    def close(self):
        if self.isClosed():
            return False
        else:
            # Fail to close if parent tile is blocked by e.g. a creature
            if self.tile.blocksMove():
                pub.sendMessage("event.doorBlocked", tile = self.tile)
                return False

            self.setClosed(True)
            pub.sendMessage("event.doorClose", tile = self.tile)
            return True
    
    def handleBump(self, creature):
        if self.isClosed():
            return self.open_()
        return False

    def isClosed(self):
        return self.closed
    
    def isOpen(self):
        return not self.isClosed()

    def setClosed(self, value):
        self.closed = value
        if value:
            self.symbol = u"+"
        else:
            self.symbol = u"'"

    def getSymbol(self):
        if self.closed:
            self.symbol = u"+"
        else:
            self.symbol = u"'"
        return self.symbol
    
    def getBlockSight(self):
        return self.isClosed()
    
    def getBlockMove(self):
        return self.isClosed()
    
    
class Stair(DungeonFeature):
    
    description = u'a stairway'
    
    def __init__(self, **kwargs):
        super(Stair, self).__init__(**kwargs)
        self.blockMove = False
        self.blockSight = False
        self.destination = kwargs.get('destination', None)
    
    def getDestination(self):
        return self.destination
    
    def setDestination(self, d):
        self.destination = d

class upStair(Stair):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'a stairway leading up'
    
    def __init__(self, **kwargs):
        super(upStair, self).__init__(symbol = u'<', **kwargs)
        
    blockMove = False
    blockSight = False
    
class downStair(Stair):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'a stairway leading down'
    
    def __init__(self, **kwargs):
        super(downStair, self).__init__(symbol = u'>', **kwargs)
        
    blockMove = False
    blockSight = False
    
class Altar(DungeonFeature):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'an altar'
    
    def __init__(self, **kwargs):
        super(Altar, self).__init__(symbol = u'_', **kwargs)
        
    blockMove = False
    blockSight = False
        
class Statue(DungeonFeature):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'a statue'
    
    def __init__(self, **kwargs):
        super(Statue, self).__init__(symbol = u'&', **kwargs)
        
    blockMove = True
    blockSight = False
        

class Tree(DungeonFeature):
    color = colors.colorTree
    backgroundColor = colors.black
    description = u'a tree'
    
    def __init__(self, **kwargs):
        super(Tree, self).__init__(symbol = random.choice([symbols.lowerTau, u'T']), **kwargs)
        
    blockMove = True
    blockSight = True
