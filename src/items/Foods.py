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
    color = colors.colorMeat
    
    def __init__(self, **kwargs):
        super(Kebab, self).__init__(description = "kebab", **kwargs)
        
        
weights = {
           Kebab : 10
           }