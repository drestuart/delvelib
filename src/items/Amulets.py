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
    
    __mapper_args__ = {
        'polymorphic_identity':'luck_amulet'
    }
    
    def __init__(self, **kwargs):
        super(LuckAmulet, self).__init__(color = colors.red, description = "amulet of luck", **kwargs)
        

weights = {
           LuckAmulet : 10
           }