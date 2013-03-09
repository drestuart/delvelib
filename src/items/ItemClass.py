###############################################################
#
# OLD STUFF
#
###############################################################

# External imports
import libtcodpy as libtcod

from GetSetClass import *

# The item class-component
class Item(GetSet):
    def __init__(self, use_function=None):
        self.use_function = use_function
    
    #an item that can be picked up and used.
    def pickUp(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 52:
            message('Your inventory is full, cannot pick up '
                    + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

    def use(self):
        #just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
