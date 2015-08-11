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
    itemType = "gem_ruby"
    description = "ruby"

    def __init__(self, **kwargs):
        super(Ruby, self).__init__(**kwargs)
        
class Emerald(I.Gem):
    color = colors.green
    itemType = "gem_emerald"
    description = "emerald"

    def __init__(self, **kwargs):
        super(Emerald, self).__init__(**kwargs)
        
        
class Diamond(I.Gem):
    color = colors.white
    itemType = "gem_diamond"
    description = "diamond"

    def __init__(self, **kwargs):
        super(Diamond, self).__init__(**kwargs)
        
        
weights = {
           Ruby : 10,
           Emerald : 10,
           Diamond : 5
           }