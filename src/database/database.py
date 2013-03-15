'''
Created on Apr 17, 2012

@author: dstu

Provides easy access to sqlalchemy functionality.

'''

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os.path
import re

__all__ = ["Database", "DATA_DIR", "static", "SAVE_DIR", "saveDB"]

DATA_DIR = os.path.abspath("data")
SAVE_DIR = os.path.abspath("save")
DB_STR = 'sqlite:///'

class NotInitializedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Database(object):
    
    __engine = None
    session = None
    Base = declarative_base()
    
    def __init__(self, filename, echo = True):
        self.filename = filename
        self.echo = echo
        
    @staticmethod
    def factory(filename, echo = True):
        db = Database(filename, echo)
        return db

    def start(self, clear = False):
        
        if clear and os.path.exists(self.filename):
            os.remove(self.filename)
            print "Deleted", self.filename
        if not self.__engine or not self.session:
            # Initialize the Database engine
            self.__engine = create_engine(DB_STR + self.filename, echo=self.echo)
            Session = sessionmaker(bind=self.__engine)
            self.session = Session()
            print "Gentledwarves, start your engines!"

        self.createAll()
        return self
    
    def checkInit(self):
        if not self.session:
            raise NotInitializedException("Database session not initialized!")
        self.createAll()
        return self
    
    def save(self, obj):
        self.checkInit()

        self.session.add(obj)
        self.session.commit()
        return self
    
    def saveAll(self, listIn):
        self.checkInit()
        
        self.session.add_all(listIn)
        self.session.commit()
        return self
        
    def delete(self, obj):
        self.checkInit()
        
        self.session.delete(obj)
        self.session.commit()
        return self
        
    def createAll(self):
        self.Base.metadata.create_all(self.__engine)
        return self
        
    def getDeclarativeBase(self):
        return self.Base
    
    def getSession(self):
        return self.session
    
    def getFilename(self):
        return self.filename
    
    def setFilename(self, instr):
        self.filename = instr
        return self
    
    def getEcho(self):
        return self.echo
    
    def setEcho(self, inval):
        self.echo = inval
        return self
    
    def getRecordById(self, clazz, id):
        self.session.commit()
        query = self.session.query(clazz)
        return query.filter(clazz.id == id).one()
    
    def getAllRecords(self, clazz):
        self.session.commit()
        query = self.session.query(clazz)
        return query.all()
    
    def getRecordsByFilter(self, clazz, filter_):
        self.session.commit()
        query = self.session.query(clazz)
        return query.filter(filter_).all()
    
    def getOneRecordByFilter(self, clazz, filter_):
        self.session.commit()
        query = self.session.query(clazz)
        return query.filter(filter_).one()
    
    def getQueryObj(self, clazz):
        return self.session.query(clazz)
    
    def runQueryGetOneRecord(self, query):
        self.session.commit()
        return query.one()
    
    def runQuery(self, query):
        self.session.commit()
        return query.all()
    
    def fillInObjectList(self, clazz, nameCol, dataDict, targetColumnName):
        nameList = re.split(r' *, *', dataDict[targetColumnName])
        objList = self.getRecordsByFilter(clazz, nameCol.in_(nameList))
        dataDict[targetColumnName] = objList
        
    def fillInObject(self, clazz, nameCol, dataDict, targetColumnName):
        name = dataDict[targetColumnName]
        obj = self.getOneRecordByFilter(clazz, nameCol == name)
        dataDict[targetColumnName] = obj
        

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
    
staticDBFile = os.path.join(DATA_DIR, "data.db")
static = Database(staticDBFile)

if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

saveDBFile = os.path.join(SAVE_DIR, "save.db")
saveDB = Database(saveDBFile, echo=False)  # Test saving db



def main():
    test = Database("test.db")
    test.start()
    test.checkInit()
    
if __name__ == "__main__":
    main()