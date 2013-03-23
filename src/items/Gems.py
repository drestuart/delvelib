'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomGem():
    gemClass = weightedChoice(weights)
    return gemClass()

class Ruby(I.Gem):
    def __init__(self, **kwargs):
        super(Ruby, self).__init__(color = colors.red, description = "a ruby", **kwargs)
        
class Emerald(I.Gem):
    def __init__(self, **kwargs):
        super(Emerald, self).__init__(color = colors.green, description = "an emerald", **kwargs)
        
        
class Diamond(I.Gem):
    def __init__(self, **kwargs):
        super(Diamond, self).__init__(color = colors.white, description = "a diamond", **kwargs)
        
        
weights = {
           Ruby : 10,
           Emerald : 10,
           Diamond : 5
           }