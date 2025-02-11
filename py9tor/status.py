# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import datetime
import logging

class Py9torStatus:
    START = datetime.datetime.now()

    def __init__(self):
        self.__class__.__new__ = lambda _: self
        self.__class__.__init__ = lambda *_, **__: None
        self.start = Py9torStatus.START
        self.requests = 0
        self.running = 0
        self.executing = list()
        logging.debug('{} created'.format(__name__))
    
    def getStatus(self):
        return self
