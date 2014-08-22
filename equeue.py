try:
    import queue
except:
    import Queue as queue
import datetime, time
from threading import Thread

class TimedItemWrapper:
    def __init__(self, item):
        self.inserttime = datetime.datetime.now()
        self.item = item

    def __repr__(self):
        return "item = %s" % str(self.item)

"""A wrapper around the python queue.Queue class"""
class ExpiringQueue(queue.Queue, object):
    """
        Create a Queue object with maxsize=0
    """
    def __init__(self, maxsize=0, timeout=None, verbose=False, interval = 1):
        if timeout is None:
            self.timeout = datetime.timedelta(days=100)
        else:
            self.timeout = datetime.timedelta(seconds=timeout)
        self.interval = interval
        self.verbose = verbose
        queue.Queue.__init__(self, maxsize);
        expire_thread = Thread(target=self.expire, args=())
        expire_thread.daemon = True
        expire_thread.start()

    def put(self, item, block = True, timeout = None):
        """
            Put an item into the queue
        """
        super(ExpiringQueue, self).put(TimedItemWrapper(item), block, timeout)

    def put_nowait(self, item):
        return self.put(item, False)

    def get(self, block=True, timeout=None):
        return super(ExpiringQueue, self).get(block, timeout).item

    def get_nowait(self):
        return self.get(False)

    def expire(self):
        """Runs forever and purges objects from queue that are older than timeout"""
        while True:
            now = datetime.datetime.now()
            try:
                while self.queue[0].inserttime + self.timeout < now:
                    if self.verbose:
                        print "Evicting item [%s] from queue" % str(self.get())
            except IndexError:
                pass # no more events
            time.sleep(self.interval)