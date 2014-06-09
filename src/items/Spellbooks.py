'''
Created on Mar 23, 2013

@author: dstu
'''

import ItemClass as I
import colors
from randomChoice import weightedChoice


def getRandomSpellbook():
    bookClass = weightedChoice(weights)
    return bookClass()

class ObligatoryFireballSpellbook(I.Spellbook):
    
    __mapper_args__ = {
        'polymorphic_identity':'obligatory_fireball_spellbook'
    }
    color = colors.colorLeather
    
    def __init__(self, **kwargs):
        super(ObligatoryFireballSpellbook, self).__init__(description = "spellbook of Obligatory Fireball", **kwargs)
        
weights = {
           ObligatoryFireballSpellbook : 10
           }