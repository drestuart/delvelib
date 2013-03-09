'''
Created on Apr 27, 2012

@author: dstu
'''
from random import randint
import re

class Dice(object):
    '''
    A class to represent a quantity of dice, with modifiers, and convert to and
    from a standard string representation.  Also supports "rolling" the dice
    to get a random integer out.
    '''
    
    @staticmethod
    def fromString(instance, strdef):
        strdef = str(strdef)
        words = re.split(r" *(?:\+|-) *", strdef)
        modifiers = re.findall(r"\+|-", strdef)
        
        if len(modifiers) == len(words) - 1:
            modifiers.insert(0, "+")
            
        elif len(modifiers) == len(words):
            pass
        
        else:
            raise ValueError("Wrong number of modifiers: " + strdef)
        
        for w, mod in zip(words, modifiers):
#            print w
            if (re.match(r"^\d+$", w)):
                if (mod == '-'):
                    instance.setModifier(instance.getModifier() + int(mod + w))
                else:
                    instance.setModifier(instance.getModifier() + int(w))
                    
            elif (re.match(r"\d+d\d+", w)):
                num, sides = w.split("d")
                instance.addDice(int(num), int(sides))
                
            else:
                raise ValueError("Token did not match: " + w + "in definition: " + strdef)
        
        return instance
            

    def __init__(self, strdef = None):
        
        self.dice = []
        self.modifier = 0
        
        if strdef:
            self = Dice.fromString(self, strdef)
            
    def toString(self):
        pass

    def getDice(self):
        return self.dice
    
    def setDice(self, val):
        self.dice = val
        return self
    
    def getModifier(self):
        return self.modifier
    
    def setModifier(self, val):
        self.modifier = int(val)
        return self
        
    def roll(self):
        result = 0
        
        for num, die in self.dice:
            for i in range(num):
                result += die.roll()
        
        result += self.modifier
        
        return max(0, result)
    
    def addDie(self, sides):
        return self.__changeNumberOfDice(1, int(sides))
        
    def removeDie(self, sides):
        return self.__changeNumberOfDice(-1, int(sides))
    
    def getMax(self):
        result = 0
        for num, die in self.dice:
            result += num*die.getSides()
        result += self.modifier
        return max(0, result)
    
    def getMin(self):
        result = 0
        for num, die in self.dice:
            result += num
        result += self.modifier
        return max(0, result)
    
    def addDice(self, *args):
        if len(args) == 0:
            raise ValueError("addDice() takes one or two arguments")
        
        elif len(args) == 1:
            # Add a Dice object
            return self.__addDiceObject(args[0])
        
        elif len(args) == 2:
            # Add some Die objects by number and sides
            return self.__changeNumberOfDice(int(args[0]), int(args[1]))
        
        else:
            raise ValueError("addDice() takes one or two arguments")
    
    def __addDiceObject(self, obj):
        if isinstance(obj, Dice):
            for (num, die) in obj.getDice():
                self.__changeNumberOfDice(num, die.getSides())
                
            return self
        
        elif isinstance(obj, type("")):
            self.__addDiceObject(Dice.fromString(obj))
            return self
        
        else:
            raise ValueError("Requires Dice or String class object")
    
    def __changeNumberOfDice(self, diff, sides):
        
        for num, die in self.dice:
            if die.getSides() == sides:
                
                self.dice.remove((num, die))
                num = max(num + diff, 0)
                
                if num:
                    self.dice.append((num, die))
                    
                return self
        
        if diff > 0:
            self.dice.append((diff, Die(sides)))
    
    
class Die(object):
    '''
    A class to represent a single die.
    '''

    def __init__(self, sides):
        self.sides = sides
    
    sides = 0
    
    def getSides(self):
        return self.sides
    
    def setSides(self, val):
        self.sides = val
        return self
    
    def roll(self):
        return randint(1, self.sides)
    
    def __repr__(self):
        return "d" + str(self.sides)
    
    
def main():
    diceBag = Dice("3d6 - 5")
    print diceBag.roll()
    print diceBag.roll()
    print diceBag.dice
    print str(diceBag.getMin()) + "->" + str(diceBag.getMax())
    
    diceBag = Dice("3d6 - 5")
    print diceBag.roll()
    print diceBag.roll()
    print diceBag.dice
    print str(diceBag.getMin()) + "->" + str(diceBag.getMax())
    
    const = Dice("4")
    print const.roll()
    print const.roll()
    print const.dice
    print str(const.getMin()) + "->" + str(const.getMax())
    
if __name__ == "__main__":
    main()
    
    