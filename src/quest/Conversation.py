'''
Created on Jun 4, 2015

@author: dstuart
'''

class ConversationTree(object):
    def __init__(self, nodes = []):
        self.nodes = nodes
        
    def addNode(self, node):
        self.nodes.append(node)
        
class ConversationNode(object):
    def __init__(self, text, options):
        self.text = text
        self.options = options
        
    def addOption(self, option):
        self.options.append(option)
        
    def display(self):
        #TODO
        print self.text
        print
        
        for opt in self.options:
            print opt
        
class ConversationOption(object):
    def __init__(self, text, nextNode, callback=None):
        self.text = text
        self.nextNode = nextNode
        self.callback = callback
        
    def setText(self, text):
        self.text = text
    
    def setNextNode(self, node):
        self.nextNode = node

    def select(self):
        if self.callback:
            self.callback()
        else:
            return self.nextNode

# Initialize test object
testConversationTree = ConversationTree()