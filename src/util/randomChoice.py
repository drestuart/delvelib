import random

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = random.randint(0, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
 
def weightedChoice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    choices = chances_dict.keys()
 
    return choices[random_choice_index(chances)]
 
def from_dungeon_level(dungeon_level, table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0
