'''
Created on Mar 13, 2013

@author: dstu
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
import AIClass as AI
import CreatureClass as Cr
import colors
import Game as G

class Player(Cr.Creature):
    
    color = colors.white
    description = 'player'
    species = 'player'

    def __init__(self, **kwargs):
        super(Player, self).__init__(symbol = u'@', name=u"player",
                                     AIClass = AI.PlayerAI, maxHP=10, **kwargs)
        
    id = Column(Integer, ForeignKey('creatures.id'), primary_key=True)
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        if newTile is not None and level.placeCreature(self, newTile):
            return True
        elif newTile is not None:
            return newTile.bump(self)
        else:
            return level.bumpEdge(self)
        
    def die(self):
        message = self.The() + " dies!"
        G.message(message)
        print message
        
        G.game.quit()
    
    def the(self):
        return self.getName()
    
    def The(self):
        return self.getName()
    
    def giveItemToCreature(self, item, creature):
        self.getInventory().removeItem(item)
        creature.getInventory().addItem(item)
        
    def getQuestItemOfType(self, itemType):
        return self.getInventory().getQuestItemOfType(itemType)
    
    