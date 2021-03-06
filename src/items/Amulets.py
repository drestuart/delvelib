'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice

def getRandomAmulet():
    amClass = weightedChoice(weights)
    return amClass()

class LuckAmulet(I.Amulet):
    color = colors.red
    itemType = "amulet_luck"
    description = "amulet of luck"
    
    def __init__(self, **kwargs):
        super(LuckAmulet, self).__init__(**kwargs)
        

weights = {
           LuckAmulet : 10
           }