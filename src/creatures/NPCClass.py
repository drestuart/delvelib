'''
Created on Jun 9, 2015

@author: dstuart
'''

import AIClass as AI
import colors
import CreatureClass as Cr
import ConversationClass

class NPC(Cr.Creature):
    
    blockSight = False
    description = "NPC"
    color = colors.white
    species = 'NPC'
    
    def __init__(self, **kwargs):
        super(NPC, self).__init__(symbol = u'@', AIClass = AI.SedentaryAI, maxHP=10, **kwargs)
        self.conversationTree = ConversationClass.testConversationTree
        self.quest = None
    
    def handleBump(self, bumper):
        import Game as G

        # Run a quest-related conversation if this NPC is attached to a quest
        if self.getGivingQuest() and not self.getGivingQuest().isReturned():
            conv = self.getGivingQuest().getConversation()
            if conv:
                G.startConversation(self, conv)
        elif self.getReturnQuest() and not self.getReturnQuest().isReturned():
            conv = self.getReturnQuest().getConversation()
            if conv:
                G.startConversation(self, conv)
        else:
            # Run default conversation
            G.startConversation(self, self.conversationTree)

        return False
    
