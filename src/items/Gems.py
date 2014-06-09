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
    color = colors.red
    def __init__(self, **kwargs):
        super(Ruby, self).__init__(description = "ruby", **kwargs)
        
class Emerald(I.Gem):
    color = colors.green
    def __init__(self, **kwargs):
        super(Emerald, self).__init__(description = "emerald", **kwargs)
        
        
class Diamond(I.Gem):
    color = colors.white
    def __init__(self, **kwargs):
        super(Diamond, self).__init__(description = "diamond", **kwargs)
        
        
weights = {
           Ruby : 10,
           Emerald : 10,
           Diamond : 5
           }