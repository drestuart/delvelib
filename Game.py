'''
Created on Mar 10, 2013

@author: dstu
'''

from pubsub import pub

defaultNames = 0

def message(msg):
    game.message(msg)
    
def startConversation(conv):
    game.startConversation(conv)

class Game(object):
    
    fontsize = None

    def initialize(self, **kwargs):
        raise NotImplementedError()
        
    def start(self):
        raise NotImplementedError()
        
    def debugListener(self,topic=pub.AUTO_TOPIC, **args):
        print 'Got an event of type: ' + topic.getName()
        print '  with data: ' + str(args)
        
    def message(self, msg):
        if self.debug: print msg
        self.ui.message(msg)
        
    def startConversation(self, conv):
        self.ui.conversationMenu(conv)

    def waitForInput(self):
        return self.ui.waitForInput()
        
    def getPlayer(self):
        return self.player
    
    def quit(self):
        self.ui.quit()
    
game = Game()

