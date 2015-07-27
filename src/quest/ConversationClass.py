'''
Created on Jun 4, 2015

@author: dstuart
'''

class ConversationTree(object):
    def __init__(self, nodes):
        self.nodes = nodes
        
    def addNode(self, node):
        self.nodes.append(node)
        
    def getFirstNode(self):
        return self.nodes[0]
        
class ConversationNode(object):
    def __init__(self, text):
        self.text = text
        self.options = []
        
    def addOption(self, option):
        self.options.append(option)
        
    def createOption(self, text, nextNode=None, callback=None):
        ConversationOption(self, text, nextNode, callback)
        
    def setText(self, text):
        self.text = text
        
    def getTextAndOptions(self):
        optionText = []
        for opt in self.options:
            optionText.append(opt.text)
        
        return self.text, optionText
        
class ConversationOption(object):
    def __init__(self, myNode = None, text=None, nextNode=None, callback=None):
        self.text = text
        self.myNode = myNode
        self.nextNode = nextNode
        self.callback = callback
        
        self.myNode.addOption(self)
        
    def setText(self, text):
        self.text = text
    
    def setNextNode(self, node):
        self.nextNode = node


# Initialize test object

firstNode = ConversationNode("This is the first conversation node")
secondNode = ConversationNode("This is the second node. It's much better than the first")
thirdNode = ConversationNode("This is the last node. It's been fun, hasn't it?")

option1 = ConversationOption(firstNode, "Go on...", secondNode)
option2 = ConversationOption(secondNode, "That's true", thirdNode)
option3 = ConversationOption(thirdNode, "Yes", None)
option4 = ConversationOption(thirdNode, "No", None)
option5 = ConversationOption(thirdNode, "Maybe", None)

testConversationTree = ConversationTree([firstNode, secondNode, thirdNode])