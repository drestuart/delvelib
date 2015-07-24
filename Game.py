'''
Created on Mar 10, 2013

@author: dstu
'''

from pubsub import pub

defaultNames = 0

def message(msg):
    game.message(msg)
    
def startConversation(cr, conv):
    game.startConversation(cr, conv)

def getDebug():
    return game.debug

def getDebugOptions():
    return game.getDebugOptions()

def setDebugOptions(options):
    game.setDebugOptions(options)

def getDebugValue(name):
    return game.getDebugValue(name)

def getCurrentLevel():
    return game.ui.getCurrentLevel()

def getCurrentMapTile():
    pass

def getWorldMap():
    return game.worldMap

def getPlayer():
    return game.getPlayer()

def getQuests():
    return game.getQuests()

def addQuest(q):
    game.addQuest(q)

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
        
    def startConversation(self, cr, conv):
        self.ui.conversationMenu(cr, conv)

    def waitForInput(self):
        return self.ui.waitForInput()
        
    def getPlayer(self):
        return self.player
    
    def getDebugOptions(self):
        return self.debugOptions

    def setDebugOptions(self, options):
        self.debugOptions = options

    def getDebugValue(self, name):
        for opt in self.debugOptions:
            if opt.name == name:
                return opt.value
        return None

    def quit(self):
        self.ui.quit()
        
    def getQuests(self):
        return self.quests
    
    def addQuest(self, q):
        self.quests.append(q)
    
game = Game()

