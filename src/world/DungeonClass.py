'''
Created on Jan 28, 2014

@author: dstuart
'''

from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import relationship, backref
from randomChoice import weightedChoice
from pubsub import pub

import database as db
import LevelClass as L
import Const as C


Base = db.saveDB.getDeclarativeBase()

class Dungeon(Base):
    
    __tablename__ = "dungeons"
    __table_args__ = {'extend_existing': True}

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "")
        self.startingDepth = kwargs.get('startingDepth', 0)
        self.withTown = kwargs.get("withTown", False)
        
        self.levels = []
    
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    startingDepth = Column(Integer)
    
    levels = relationship("Level", backref=backref("dungeon", uselist=False), 
                          primaryjoin="Dungeon.id==Level.dungeonId")
    
    dungeonType = Column(String)
    
    __mapper_args__ = {'polymorphic_on': dungeonType,
                       'polymorphic_identity': 'dungeon'}
    
    levelChances = {L.DungeonLevel : 7,
                    L.CaveLevel : 3}
    
#    defaultWidth = C.MAP_WIDTH     # 75
#    defaultHeight = C.MAP_HEIGHT   # 45
    
#    defaultWidth = 40
#    defaultHeight = 30
    
    defaultWidth = 100
    defaultHeight = 80
    
    def getLevels(self):
        return self.levels
    
    def generateLevels(self, numLevels = 4):
        
        # Build levels
        for i in range(numLevels):
            newDepth = self.startingDepth + i
            newName = self.name + " " + str(i + 1)
            
            if self.withTown and newDepth == self.startingDepth:
                newLevel = L.TownLevel(name = newName, depth = newDepth, cellsWide = 2, cellsHigh = 2)
                
            else:
                newLevelClass = weightedChoice(self.levelChances)
                newLevel = newLevelClass(name = newName, depth = newDepth, width = self.defaultWidth,
                                         height = self.defaultHeight) # Do something more interesting with the dimensions999 here
            
            newLevel.buildLevel()
            
            # TODO chance to generate a branch or loop
            
            # Connect levels
            if i > 0:
                plevel = self.levels[-1]
                
                # The depth values should be off by only 1. TODO better validation
                
                if plevel.depth < newLevel.depth:
                    L.connectLevels(plevel, newLevel)
                else:
                    L.connectLevels(newLevel, plevel)
            
            self.levels.append(newLevel)
            db.saveDB.save(newLevel)
            
        db.saveDB.save(self)

        # TODO Connect top level to world map
    
    
    