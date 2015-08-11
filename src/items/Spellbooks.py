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
    color = colors.colorLeather
    itemType = "spellbook_obligatory_fireball"
    description = "spellbook of Obligatory Fireball"
    
    def __init__(self, **kwargs):
        super(ObligatoryFireballSpellbook, self).__init__(**kwargs)
        
weights = {
           ObligatoryFireballSpellbook : 10
           }