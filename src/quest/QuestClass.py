'''
Created on Jun 23, 2015

@author: dstuart
'''

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, Boolean, Unicode
from sqlalchemy.orm import relationship, backref

class Quest(object):
    __tablename__ = "quests"
    __table_args__ = {'extend_existing': True}
    
    def __init__(self, **kwargs):
        pass
    
    id = Column(Integer, primary_key=True, unique=True)
    questType = Column(Unicode)
    
    fetchItems = relationship("Item", backref=backref("quest", uselist = False), primaryjoin="Quest.id==Item.questId")
    questGivers = relationship("Creature", backref=backref("quest", uselist = False), primaryjoin="Quest.id==Creature.givingQuestId")
    
    # Might not be necessary to do it this way. Maybe subscribe to a creature kill event?
#     questTargets = relationship("Creature", backref=backref("quest", uselist = False), primaryjoin="Quest.id==Creature.targetOfQuestId")
    
    __mapper_args__ = {'polymorphic_on': questType,
                       'polymorphic_identity': u'quest'}
    
    def startQuest(self):
        pass
    
class FetchQuest(Quest):
    pass

class AssassinationQuest(Quest):
    pass