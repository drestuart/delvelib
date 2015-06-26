'''
Created on Jun 23, 2015

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, Boolean, Unicode
from sqlalchemy.orm import relationship, backref
import database as db
from pubsub import pub

Base = db.saveDB.getDeclarativeBase()

questEventPrefix = 'event.quest.'

class Quest(Base):
    __tablename__ = "quests"
    __table_args__ = {'extend_existing': True}
    
    questCompleteEventName = questEventPrefix + 'complete'

    def __init__(self, **kwargs):
        pass
    
    id = Column(Integer, primary_key=True, unique=True)
    questType = Column(Unicode)
    
    questGivers = relationship("Creature", backref=backref("quest", uselist = False), primaryjoin="Quest.id==Creature.givingQuestId")
    questRequirements = relationship("QuestRequirement", backref=backref("quest", uselist = False), primaryjoin="Quest.id==QuestRequirement.questId")
    
    __mapper_args__ = {'polymorphic_on': questType,
                       'polymorphic_identity': u'quest'}
    
    def buildRequirements(self):
        raise NotImplementedError("buildRequirements()")

    def startQuest(self):
        for req in self.questRequirements:
            req.subscribe()

        pub.subscribe(self.questProgress, QuestRequirement.updatedEventName)
        pub.subscribe(self.handleRequirementCompletion, QuestRequirement.satisfiedEventName)

    def questProgress(self, req):
        pass

    def handleRequirementCompletion(self, req):
        pub.sendMessage(self.questCompleteEventName, self)
        
    def placeQuestItems(self):
        pass
    
    def placeQuestCreatures(self):
        pass
    
    def attachToQuestgiver(self):
        pass
    

class QuestRequirement(Base):
    __tablename__ = "quest_requirements"
    __table_args__ = {'extend_existing': True}

    updatedEventName = questEventPrefix + 'requirement.updated'
    satisfiedEventName = questEventPrefix + 'requirement.satisfied'

    def __init__(self, eventName, eventsRemaining, quest):
        self.eventName = eventName
        self.eventsRemaining = eventsRemaining
        self.quest = quest

    id = Column(Integer, primary_key=True, unique=True)
    questId = Column(Integer, ForeignKey("quests.id"))
    eventName = Column(Unicode)
    eventsRemaining = Column(Integer)

    def subscribe(self):
        pub.subscribe(self.handleEvent, self.questEventPrefix + self.eventName)

    def handleEvent(self):
        self.eventsRemaining -= 1
        pub.sendMessage(self.updatedEventName, req = self)
        if self.completed():
            pub.sendMessage(self.satisfiedEventName, req = self)
    
    def completed(self):
        return self.eventsRemaining <= 0

