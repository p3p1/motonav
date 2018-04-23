from threading import Thread
from random import randint

class navThread(Thread):
    def __init__(self, title, target, *args):
        Thread.__init__(self)
        self._title  = title
        self._target = target
        self._args   = args
    def run(self):
        pass


