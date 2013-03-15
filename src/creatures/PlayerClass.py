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
        super(Player, self).__init__(symbol = '@', baseColor = colors.white, baseBackground = colors.black, name="player",
                                     description = '', species = 'player', AIClass = AI.PlayerAI, maxHP=10, **kwargs)
        
        
    __mapper_args__ = {'polymorphic_identity': 'player'}
    
    id = Column(Integer, ForeignKey('creatures.id'), primary_key=True)
    
    def move(self, dx, dy):
        
        newX = self.getX() + dx
        newY = self.getY() + dy
        level = self.getLevel()
        newTile = level.getTile(newX, newY)
        
        if level.placeCreature(self, newTile):
            
            #Remove self from the old tile
#            oldTile = self.map.getTile(self.coordinates)
#            oldTile.removeCreature()
        
#            self.setPosition(self.map, newCoords)
            #self.energy -= self.moveCost
                        
            print self.name + " moves to", self.getX(), self.getY()
            self.getLevel().setNeedToComputeFOV(True)
            return True
        
        else:
            return False
    
    def the(self):
        return self.getName()
    
    def The(self):
        return self.getName()
    
        
    
    