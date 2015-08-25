'''
Created on Mar 10, 2013

@author: dstu
'''

from pubsub import pub
import WorldMapClass
import shelve

defaultNames = 0
shelf = None
ui = None

def save():
    game.save()

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
    return game.getCurrentLevel()

def setCurrentLevel(lvl):
    game.setCurrentLevel(lvl)

def getCurrentMapTile():
    return game.getCurrentMapTile()

def getWorldMap():
    return game.getWorldMap()

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
        global ui
        if self.debug: print msg
        ui.message(msg)
        
    def startConversation(self, cr, conv):
        global ui
        ui.conversationMenu(cr, conv)

    def waitForInput(self):
        global ui
        return ui.waitForInput()
        
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

    def openShelf(self, filename = 'save/save.eru'):
        global shelf
        if shelf is not None:
            self.closeShelf()

        shelf = shelve.open(filename, writeback=True)
        shelf['game'] = self
        return True

    def loadShelf(self, filename = 'save/save.eru'):
        global shelf
        if shelf is not None:
            self.closeShelf()

        shelf = shelve.open(filename, writeback=True)
        self = shelf['game']
        return True
    
    def closeShelf(self):
        global shelf
        if shelf is not None:
            shelf.close()
            return True
        return False

    def save(self):
        global shelf
        if shelf is not None:
            shelf.sync()
            return True
        return False
        
    def getQuests(self):
        return self.quests
    
    def addQuest(self, q):
        self.quests.append(q)
        
    def getWorldMap(self):
        return self.worldMap

    def getCurrentLevel(self):
        return self.currentLevel

    def setCurrentLevel(self, lvl):
        self.currentLevel = lvl

    def getCurrentMapTile(self):
        global ui
        level = ui.getCurrentLevel()
        if not isinstance(level, WorldMapClass.WorldMap):
            return level.getMapTile()
        return self.getPlayer().getTile()

game = Game()

