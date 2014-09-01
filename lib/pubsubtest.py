'''
Created on Jan 25, 2014

@author: dstu
'''

'''
One listener is subscribed to a topic called 'rootTopic'.
One 'rootTopic' message gets sent. 
'''

from pubsub import pub

# ------------ create a listener ------------------

def listener1(arg1, arg2=None):
    print 'Function listener1 received:'
    print '  arg1 =', arg1
    print '  arg2 =', arg2
    
def listener2(arg1):
    print 'Function listener2 received:'
    print '  arg1 =', arg1

def listener3(topic=pub.AUTO_TOPIC, **args):
    print 'Listener3 got an event of type: ' + topic.getName()
    print '  with data: ' + str(args)

# ------------ register listener ------------------

pub.subscribe(listener1, 'root.Topic')
pub.subscribe(listener2, 'root')
pub.subscribe(listener3, 'root')


#---------------- send a message ------------------

print 'Publish something via pubsub'
anObj = dict(a=456, b='abc')
pub.sendMessage('root.Topic', arg1=123, arg2=anObj)
print
pub.sendMessage('root', arg1=456)