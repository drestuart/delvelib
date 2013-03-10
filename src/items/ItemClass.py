'''
Created on Mar 10, 2013

@author: dstu
'''

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Float
import database as db

Base = db.saveDB.getDeclarativeBase()

class Item(Base):
    '''
    The abstract item baseclass
    '''
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}


    def __init__(self, **kwargs):
        self.weight = kwargs['weight']
        self.possessor = kwargs['possessor']
        self.type_ = kwargs['type_']
        self.onUse = kwargs['onUse']
        self.onDrop = kwargs['onDrop']
        self.onPickup = kwargs['onPickup']

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    type_ = Column(String)

    possessor = relationship("Creature", primaryjoin="Creature.id==Item.possessorId")
    possessorId = Column(Integer, ForeignKey("creatures.id"))
#    containerId = Column(Integer, ForeignKey("inventories.id"))
    
    # For items that have an inventory
#    inventoryId = Column(Integer, ForeignKey("inventories.id"))
#    inventory = relationship("Inventory", uselist=False, primaryjoin="Inventory.id==Item.inventoryId")

    
    __mapper_args__ = {
        'polymorphic_on':type_,
        'polymorphic_identity':'item'
    }
    
#    def getContainer(self):
#        return self.container
#    
#    def setContainer(self, val):
#        self.container = val
#        return self
    
    def drop(self):
        # TODO: Handle universal dropping logic
        self.onDrop()
        
    def pickup(self):
        # TODO: Handle universal pickup logic
        self.onPickup()
        
    def use(self):
        self.onUse()
    
    
    def getId(self):
        return self.id

    def setId(self, val):
        self.id = val
        return self
    
    def getWeight(self):
        return self.weight
    
    def setWeight(self, val):
        self.weight = val
        return self
    
    def getPossessor(self):
        return self.possessor
    
    def setPossessor(self, val):
        self.possessor = val
        return self
    
def main():
    pass


    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
