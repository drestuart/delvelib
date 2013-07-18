'''
Created on Jul 18, 2013

@author: dstu
'''

import DamageType as dt

class DamageBundle(object):
    
    def __init__(self, *args):
        self.damage = []
        
        for arg in args:
            self.addDamage(arg[0], arg[1])
    
    def getDamage(self):
        return self.damage
    
    def setDamage(self, damIn):
        self.damage = damIn
    
    def addDamage(self, damageType, damageVal):
        
        if damageType not in dt.types:
            raise ValueError("Invalid damage type: " + str(damageType))
        
        self.damage.append((damageType, damageVal))

    def __str__(self):
        retStr = ""
        
        for ind in range(len(self.damage)):
            damageObj = self.damage[ind]
            
            damageType = damageObj[0]
            damageVal = damageObj[1]
            
            if ind == len(self.damage):
                retStr += " and "
            
            retStr += damageVal + " " + damageType
            
            if ind != len(self.damage):
                retStr += ", "
            
        return retStr

    def __repr__(self):
        return "DamageBundle:" + str(self.damage)