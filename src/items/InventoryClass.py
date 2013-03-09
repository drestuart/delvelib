###############################################################
#
# OLD STUFF
#
###############################################################

# External imports
import libtcodpy as libtcod
from keys import *
from menu import *
from GetSetClass import *

INVENTORY_WIDTH = 50

class ItemInventory(GetSet):
    # A list of items, with some organization logic and the ability to choose an item out of a menu.
    def __init__(self):
        self.__dict__['items'] = []  # This will probably be a dict at some point
        
    def __len__(self):
        return len(self.items)
    
    def add(self, item):
        self.items.append(item)
        
    def __getitem__(self, ind):
        return self.items[ind]
        
        
# The inventory menu
def inventoryMenu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]
 
    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0:
        return None
    return inventory[index].item

