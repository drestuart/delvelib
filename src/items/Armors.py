'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice

def getRandomArmor():
    armClass = weightedChoice(weights)
    return armClass()

class Breastplate(I.Armor):
    color = colors.colorSteel
    itemType = "armor_breastplate"
    description = "breastplate"
    
    def __init__(self, **kwargs):
        super(Breastplate, self).__init__(**kwargs)
        
weights = {
           Breastplate : 10
           }
