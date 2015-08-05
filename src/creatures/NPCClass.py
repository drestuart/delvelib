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
        # Start a conversation
        if self.quest and not self.quest.isReturned():
            conv = self.quest.getConversation()
            if conv:
                G.startConversation(self, conv)
        else:
            G.startConversation(self, self.conversationTree)

        return False
    
