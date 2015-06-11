'''
Created on Jun 9, 2015

@author: dstuart
'''

import AIClass as AI
import colors
import CreatureClass as Cr
import Game
import ConversationClass

class NPC(Cr.Creature):
    
    blockSight = False
    description = "NPC"
    color = colors.white
    species = 'player'
    
    def __init__(self, **kwargs):
        super(NPC, self).__init__(symbol = u'@', AIClass = AI.SedentaryAI, maxHP=10, **kwargs)
        self.conversationTree = ConversationClass.testConversationTree
    
    __mapper_args__ = {'polymorphic_identity': u'NPC'}
    
    def handleBump(self, bumper):
        # Start a conversation
        Game.startConversation(self.conversationTree)
        return False
    
