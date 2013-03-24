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
    
    __mapper_args__ = {
        'polymorphic_identity':'breastplate'
    }
    
    def __init__(self, **kwargs):
        super(Breastplate, self).__init__(color = colors.colorSteel, description = "breastplate", **kwargs)
        
weights = {
           Breastplate : 10
           }
