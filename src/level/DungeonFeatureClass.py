'''
Created on Mar 12, 2013

@author: dstu
'''

from pubsub import pub
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer, Boolean

import colors
import database as db
import symbols
import random

Base = db.saveDB.getDeclarativeBase()

class DungeonFeature(colors.withBackgroundColor, Base):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    __tablename__ = "dungeon_features"
    __table_args__ = {'extend_existing': True}
    
    description = u"dungeon feature"
    
    def __init__(self, symbol, **kwargs):
        super(DungeonFeature, self).__init__(**kwargs)
        self.symbol = symbol
        
        self.tile = kwargs.get('tile', None)
        
        self.visible = kwargs.get('isVisible', True)
        
        
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    symbol = Column(Unicode(length=1))
    
    tileId = Column(Integer)
    visible = Column(Boolean)
    featureType = Column(Unicode)
    
    __mapper_args__ = {'polymorphic_on': featureType,
                       'polymorphic_identity': u'feature'}

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

    def getTile(self):
        return self.tile

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


    def setTile(self, value):
        self.tile = value


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

    closed = Column(Boolean)
    
    __mapper_args__ = {'polymorphic_identity': u'door'}


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
    
    __mapper_args__ = {'polymorphic_identity': u'Stair'}
    
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
        
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': u'upStair'}
 
    blockMove = False
    blockSight = False
    
    def getDestination(self):
        return self.destination
    
    def setDestination(self, dest):
        self.destination = dest
    

class downStair(Stair):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'a stairway leading down'
    
    def __init__(self, **kwargs):
        super(downStair, self).__init__(symbol = u'>', **kwargs)
        
        self.destination = kwargs.get('destination', None)
        
    __mapper_args__ = {'polymorphic_identity': u'downStair'}
    
    blockMove = False
    blockSight = False
    
    def getDestination(self):
        return self.destination
    
    def setDestination(self, dest):
        self.destination = dest


class Altar(DungeonFeature):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'an altar'
    
    def __init__(self, **kwargs):
        super(Altar, self).__init__(symbol = u'_', **kwargs)
        
    blockMove = False
    blockSight = False
        
    __mapper_args__ = {'polymorphic_identity': u'altar'}
    
class Statue(DungeonFeature):
    color = colors.colorStone
    backgroundColor = colors.black
    description = u'a statue'
    
    def __init__(self, **kwargs):
        super(Statue, self).__init__(symbol = u'&', **kwargs)
        
    blockMove = True
    blockSight = False
        
    __mapper_args__ = {'polymorphic_identity': u'statue'}


class Tree(DungeonFeature):
    color = colors.colorTree
    backgroundColor = colors.black
    description = u'a tree'
    
    def __init__(self, **kwargs):
        super(Tree, self).__init__(symbol = random.choice([symbols.lowerTau, u'T']), **kwargs)
        
    blockMove = True
    blockSight = True
        
    __mapper_args__ = {'polymorphic_identity': u'tree'}
