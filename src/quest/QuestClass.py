'''
Created on Jun 23, 2015

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, Boolean, Unicode
from sqlalchemy.orm import relationship, backref
import database as db
from pubsub import pub
import ItemClass
from enum import Enum, unique

Base = db.saveDB.getDeclarativeBase()

questEventPrefix = 'event.quest.'

# TODO
# @unique
# class QuestStatus(Enum):
#     NOT_STARTED = 1
#     STARTED = 2
#     COMPLETED = 3

NOT_STARTED = 1
STARTED = 2
COMPLETED = 3

class Quest(Base):
    __tablename__ = "quests"
    __table_args__ = {'extend_existing': True}
    
    questRequirementCompleteEventName = questEventPrefix + 'requirement.complete'
    questCompleteEventName = questEventPrefix + 'complete'

    def __init__(self, **kwargs):
        self.questStatus = NOT_STARTED
        self.startConversation = None
        self.progressConversation = None
        self.completedConversation = None
    
    id = Column(Integer, primary_key=True, unique=True)
    questType = Column(Unicode)
    questStatus = Column(Integer)
    
    questGivers = relationship("Creature", backref=backref("quest", uselist = False), primaryjoin="Quest.id==Creature.givingQuestId")
    questRequirements = relationship("QuestRequirement", backref=backref("quest", uselist = False), primaryjoin="Quest.id==QuestRequirement.questId")
    
    __mapper_args__ = {'polymorphic_on': questType,
                       'polymorphic_identity': u'quest'}
    
    def buildRequirements(self):
        raise NotImplementedError("buildRequirements()")

    def startQuest(self):
        for req in self.questRequirements:
            req.subscribe()

        pub.subscribe(self.handleQuestProgress, QuestRequirement.updatedEventName)
        pub.subscribe(self.handleRequirementCompletion, QuestRequirement.satisfiedEventName)
        
        self.questStatus = STARTED

    def addRequirement(self, req):
        self.questRequirements.append(req)

    def handleQuestProgress(self, req):
        print "Quest progress!"
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

        print "Status:", self.questStatus

    def setCompleted(self):
        if self.questStatus != NOT_STARTED:
            print "Quest complete!"
            self.questStatus = COMPLETED
            pub.sendMessage(self.questCompleteEventName, quest=self)

        print "Status:", self.questStatus

    def handleRequirementCompletion(self, req):
        print "Quest requirement complete!"
        pub.sendMessage(self.questRequirementCompleteEventName, quest=self)

    def placeQuestItems(self):
        pass

    def placeQuestCreatures(self):
        pass

    def addQuestGiver(self, cr):
        self.questGivers.append(cr)
        cr.quest = self

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

class QuestRequirement(Base):
    __tablename__ = "quest_requirements"
    __table_args__ = {'extend_existing': True}

    updatedEventName = questEventPrefix + 'requirement.updated'
    satisfiedEventName = questEventPrefix + 'requirement.satisfied'

    def __init__(self, eventsRemaining, quest):
        self.eventsRemaining = eventsRemaining
        self.quest = quest

    id = Column(Integer, primary_key=True, unique=True)
    questId = Column(Integer, ForeignKey("quests.id"))
    eventsRemaining = Column(Integer)
    requirementType = Column(Unicode)
    
    __mapper_args__ = {
        'polymorphic_on':requirementType,
        'polymorphic_identity':u'quest_requirement'
    }
    
    def completed(self):
        return self.eventsRemaining <= 0

class QuestItemRequirement(QuestRequirement):
    
    def __init__(self, itemType, eventsRemaining, quest):
        super(QuestItemRequirement, self).__init__(eventsRemaining, quest)
        self.itemType = itemType
        self.itemTypeStr = unicode(itemType.__name__)
    
    itemTypeStr = Column(Unicode)
    
    __mapper_args__ = {'polymorphic_identity':u'quest_item_requirement'}
        
    def subscribe(self):
        pub.subscribe(self.handlePickupEvent, self.getItemType().getQuestPickupEvent())
        pub.subscribe(self.handleDropEvent, self.getItemType().getQuestDropEvent())
        
    def handlePickupEvent(self, item):
        print "Picked up quest item"
        self.eventsRemaining -= 1
        self.updateEvents()
        
    def handleDropEvent(self, item):
        print "Dropped quest item"
        self.eventsRemaining += 1
        self.updateEvents()
    
    def updateEvents(self):
        print "Events remaining:", self.eventsRemaining
        pub.sendMessage(self.updatedEventName, req = self)
        if self.completed():
            pub.sendMessage(self.satisfiedEventName, req = self)
            
    def getItemType(self):
        if self.__dict__.get("itemType"):
            return self.itemType
        
        self.itemType = ItemClass.__dict__.get(self.itemTypeStr)
        return self.itemType

