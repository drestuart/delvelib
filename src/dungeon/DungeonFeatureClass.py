###############################################################
#
# OLD STUFF
#
###############################################################


from GetSetClass import *

class DungeonFeature(GetSet):
    # Dummy class right now.  Will eventually represent dungeon features like traps, altars and stairs
    
    def __init__(self, blockSight = False, blockMove = False, baseSymbol = '}'):
        self.blockSight = blockSight
        self.blockMove = blockMove
        self.baseSymbol = baseSymbol