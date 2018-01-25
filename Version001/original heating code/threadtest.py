import threading
import ow
import time
import Queue

def foo(q):
    #print 'here'
    t =(ow.Sensor('/uncached/28.0F7AD1010000').temperature)
    q.put (t)
    
#ow.init('localhost:4304')
ow.init('/dev/i2c-1')
q = Queue.Queue()
foo(q)

while 1 :

    time.sleep (1)
    print 'wait'

    if not q.empty () : 
        print q.get ()
        threading.Timer (5, foo, args = (q,)).start()
