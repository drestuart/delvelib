'''
Created on Jun 23, 2015

@author: dstuart
'''

from __future__ import unicode_literals

from pubsub import pub
import ItemClass
import Game

questEventPrefix = 'event.quest.'

# TODO:
# @unique
# class QuestStatus(Enum):
#     NOT_STARTED = 1
#     STARTED = 2
#     COMPLETED = 3

NOT_STARTED = 1
STARTED = 2
COMPLETED = 3
RETURNED = 4

class Quest(object):

    questRequirementCompleteEventName = questEventPrefix + 'requirement.complete'
    questCompleteEventName = questEventPrefix + 'complete'
    questReturnedEventName = questEventPrefix + 'returned'

    def __init__(self, **kwargs):
        self.questStatus = NOT_STARTED
        self.questName = None
        self.startConversation = None
        self.progressConversation = None
        self.completedConversation = None

        self.questGivingNPC = None
        self.questReturnNPC = None
        self.questRequirements = set()
        
        Game.addQuest(self)
    
    def buildRequirements(self):
        raise NotImplementedError("buildRequirements()")
    
    def setUpQuest(self):
        raise NotImplementedError("setUpQuest()")

    def startQuest(self):
        for req in self.questRequirements:
            req.subscribe()

        pub.subscribe(self.handleQuestProgress, QuestRequirement.updatedEventName)
        pub.subscribe(self.handleRequirementCompletion, QuestRequirement.satisfiedEventName)
        
        self.questStatus = STARTED

    def getRequirements(self):
        return self.questRequirements

    def addRequirement(self, req):
        self.questRequirements.add(req)
        if req.getQuest is not self:
            req.setQuest(self)

    def handleQuestProgress(self, req):
        self.checkQuestRequirements()

    def checkQuestRequirements(self):
        for req in self.questRequirements:
            if not req.completed():
                self.setUncompleted()
                return False

        self.setCompleted()
        return True

    def setUncompleted(self):
        if self.questStatus != NOT_STARTED:
            self.questStatus = STARTED

    def setCompleted(self):
        if self.questStatus != NOT_STARTED:
            self.questStatus = COMPLETED
            pub.sendMessage(self.questCompleteEventName, quest=self)
        
    def setReturned(self):
        if self.questStatus != NOT_STARTED:
            self.questStatus = RETURNED
            pub.sendMessage(self.questReturnedEventName, quest=self)
        
    def isReturned(self):
        return self.questStatus == RETURNED

    def handleRequirementCompletion(self, req):
        pub.sendMessage(self.questRequirementCompleteEventName, quest=self)

    def placeQuestItems(self):
        pass

    def placeQuestCreatures(self):
        pass

    def getQuestGivingNPC(self):
        return self.questGivingNPC

    def setQuestGivingNPC(self, npc):
        self.questGivingNPC = npc
        if self is not npc.getGivingQuest():
            npc.setGivingQuest(self)

    def getQuestReturnNPC(self):
        return self.questReturnNPC

    def setQuestReturnNPC(self, npc):
        self.questReturnNPC = npc
        if self is not npc.getReturnQuest(): # TODO: Wipe out existing quest?
            npc.setReturnQuest(self)

    def getConversation(self):
        if self.questStatus == NOT_STARTED:
            return self.getStartConversation()
        elif self.questStatus == STARTED:
            return self.getProgressConversation()
        elif self.questStatus == COMPLETED:
            return self.getCompletedConversation()

    def getStartConversation(self):
        pass

    def getProgressConversation(self):
        pass

    def getCompletedConversation(self):
        pass
    
    def getName(self):
        return self.questName
    
    def getStatus(self):
        return self.questStatus
    
    def getStatusString(self):
        st = self.getStatus()
        if st == NOT_STARTED:
            return "Not started"
        elif st == STARTED:
            return "Started"
        elif st == COMPLETED:
            return "Completed"
        elif st == RETURNED:
            return "Returned"

class ItemQuest(Quest):

    def __init__(self, itemTypes):
        super(ItemQuest, self).__init__()
        self.itemTypes = itemTypes

    def buildRequirements(self):
        for (type_, quantity) in self.itemTypes:
            QuestItemRequirement(type_, quantity, self)

    def placeQuestItems(self):
        pass

    def startQuest(self):
        self.placeQuestItems()
        super(ItemQuest, self).startQuest()

    def setReturned(self):
        player = Game.getPlayer()

        # Move item from player's inventory to quest NPC's
        for req in self.questRequirements:
            itemType = req.getItemType()
            if itemType:
                for dummy in range(req.getEventsRequired()):
                    item = player.getQuestItemOfType(itemType)
                    if item:
                        npc = self.getQuestReturnNPC()
                        player.giveItemToCreature(item, npc)
                    else:
                        print "Couldn't find a", req.itemTypeStr, "for some reason"

        super(ItemQuest, self).setReturned()

    __mapper_args__ = {'polymorphic_identity': u'item_quest'}

class QuestRequirement(object):
    updatedEventName = questEventPrefix + 'requirement.updated'
    satisfiedEventName = questEventPrefix + 'requirement.satisfied'

    def __init__(self, eventsRequired, quest):
        self.eventsRequired = eventsRequired
        self.eventsRemaining = eventsRequired
        self.setQuest(quest)

# TODO:
#     questId = Column(Integer, ForeignKey("quests.id"))
    
    def completed(self):
        return self.eventsRemaining <= 0

    # For subclasses to override
    def getItemType(self):
        return None

    def getEventsRequired(self):
        return self.eventsRequired

    def getEventsRemaining(self):
        return self.eventsRemaining

    def getQuest(self):
        return self.quest

    def setQuest(self, quest):
        self.quest = quest
        if self not in quest.getRequirements():
            quest.addRequirement(self)

class QuestItemRequirement(QuestRequirement):
    
    def __init__(self, itemType, eventsRemaining, quest):
        super(QuestItemRequirement, self).__init__(eventsRemaining, quest)
        self.itemType = itemType
        self.itemTypeStr = unicode(itemType.__name__)
    
    def subscribe(self):
        pub.subscribe(self.handlePickupEvent, self.getItemType().getQuestPickupEvent())
        pub.subscribe(self.handleDropEvent, self.getItemType().getQuestDropEvent())
        
    def handlePickupEvent(self, item):
        self.eventsRemaining -= 1
        self.updateEvents()
        
    def handleDropEvent(self, item):
        self.eventsRemaining += 1
        self.updateEvents()
    
    def updateEvents(self):
        pub.sendMessage(self.updatedEventName, req = self)
        if self.completed():
            pub.sendMessage(self.satisfiedEventName, req = self)
            
    def getItemType(self):
        if self.__dict__.get("itemType"):
            return self.itemType
        
        self.itemType = ItemClass.__dict__.get(self.itemTypeStr)
        return self.itemType
    
