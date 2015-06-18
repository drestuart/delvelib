'''
Created on Jun 18, 2015

@author: dstuart
'''

from enum import Enum, unique

@unique
class OptionType(Enum):
    TOGGLE = 1
    INTEGER = 2
    STRING = 3

class Option(object):
    def __init__(self, name, text, optionType, value, **kwargs):
        self.name = name
        self.text = text
        self.optionType = optionType
        
        if self.optionType == OptionType.INTEGER:
            self.min = kwargs["min"]
            self.max = kwargs["max"]
            
        elif self.optionType == OptionType.TOGGLE:
            self.trueText = kwargs["trueText"]
            self.falseText = kwargs["falseText"]
            
        self.setValue(value)
            
    def setValue(self, val):
        if self.optionType == OptionType.TOGGLE and not isinstance(val, bool):
            raise ValueError("Option " + self.name + " requires a boolean value")

        elif self.optionType == OptionType.INTEGER:
            if not isinstance(val, int):
                raise ValueError("Option " + self.name + " requires an integer value")

            if val < self.min or val > self.max:
                val = max(val, self.min)
                val = min(val, self.max)

        elif self.optionType == OptionType.STRING and not isinstance(val, str):
            raise ValueError("Option " + self.name + " requires a string value")

        self.value = val


