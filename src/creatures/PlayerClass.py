'''
Created on Mar 13, 2013

@author: dstu
'''

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
import AIClass as AI
import CreatureClass as Cr
import colors

class Player(Cr.Creature):
    
    __tablename__ = "player"
#    __table_args__ = {'extend_existing': True}



    def __init__(self, **kwargs):
        super(Player, self).__init__(symbol = '@', color = colors.white, name="player",
                                     description = 'player', species = 'player', AIClass = AI.PlayerAI, maxHP=10, **kwargs)
        
        
    __mapper_args__ = {'polymorphic_identity': 'player'}
    
    id = Column(Integer, ForeignKey('creatures.id'), primary_key=True)
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        if newTile is not None and level.placeCreature(self, newTile):
            return True
        elif newTile is not None:
#             return False
            return newTile.bump(self)
        else:
            return level.bumpEdge(self)
    
    def the(self):
        return self.getName()
    
    def The(self):
        return self.getName()
    
        
    
    