'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomFood():
    foodClass = weightedChoice(weights)
    return foodClass()

class Kebab(I.Food):
    
    __mapper_args__ = {
        'polymorphic_identity':'kebab'
    }
    
    def __init__(self, **kwargs):
        super(Kebab, self).__init__(color = colors.colorMeat, description = "kebab", **kwargs)
        
        
weights = {
           Kebab : 10
           }