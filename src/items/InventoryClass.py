'''
Created on May 17, 2012

@author: dstu
'''

import ItemClass as I
import colors

class Inventory():
    '''
    The inventory class.  Represents a collection of items, either on a tile, in a container or held by a person.
    Also provides some convenience methods.
    '''

    def __init__(self, **kwargs):
        
        self.items = []
        self.containingItem = None
        self.creature = None
        self.tile = None

    def printContents(self):
        for item in self.items:
            print item.getDescription()
    
    def addItem(self, itemIn):
        if self.items is None:
            self.items = []
        
        if self.items == []:
            self.items.append(itemIn)
            return self
        
        if not itemIn in self.items:
            if not type(itemIn).getStackable():
#                print itemIn.getDescription() + " is not stackable"
                self.items.append(itemIn)
                
            else:
                stacked = False
                for item in self.items:
                    if item.canStackWith(itemIn):
#                        print "Stacking " + itemIn.getDescription() + " and " + item.getDescription()
                        item.stackWith(itemIn)
                        stacked = True
                        del itemIn
                        break
                
                if not stacked:
                    self.items.append(itemIn)
                
            return self
        
        raise ValueError(itemIn + " already exists in container " + self)
    
    def removeItem(self, itemIn):
        if itemIn in self.items:
            self.items.remove(itemIn)
            return itemIn
        
        raise ValueError(itemIn + " does not exist in container " + self)
    
    def pop(self, ind = 0):
        if len(self.items) <= ind:
            return None
        itemToPop = self.items[ind]
        return self.removeItem(itemToPop)
    
    def getItem(self, ind):
        return self.items[ind]

    def getItems(self):
        return self.items
    
    def getCreature(self):
        return self.creature
    
    def setCreature(self, cr):
        self.creature = cr
        if cr.getInventory() is not self:
            cr.setInventory(self)

    def getItemOfType(self, itemType, questItem = False):
        for item in self.items:
            if isinstance(item, itemType):
                # If it's a quest item, don't bother checking questItem requirement
                if item.isQuestItem():
                    return item
                # If it's not, check the requirement
                if not questItem:
                    return item

        return None

    def getQuestItemOfType(self, itemType):
        return self.getItemOfType(itemType, True)

    def getContainingItem(self):
        return self.containingItem
    
    def setContainingItem(self, it):
        self.containingItem = it
        if self.containingItem.getInventory() is not self:
            self.containingItem.setInventory(self)

    def setItems(self, value):
        self.items = value

    def length(self):
        return len(self.items)
    
    def getTile(self):
        return self.tile
    
    def setTile(self, tile):
        self.tile = tile
        if tile.getInventory() is not self:
            tile.setInventory(self)
