# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import logging
import datetime
from py9tor.status import Py9torStatus
from py9tor.worker import Py9torWorker

class Py9torFacade:
    def __init__(self):
        self.__class__.__new__ = lambda _: self
        self.__class__.__init__ = lambda *_, **__: None
        logging.debug('{} created'.format(__name__))

    def status(self):
        logging.debug('status')
        Py9torStatus().requests += 1
        logging.debug('Uptime: {}'.format(datetime.datetime.now() - Py9torStatus().start))
        return Py9torStatus()

    def start(self, target):
        logging.info('start {}'.format(target))
        Py9torStatus().requests += 1
        Py9torWorker(target).start()
    
    def quit(self):
        from py9tor.server import shutdown
        logging.debug('quit')
        Py9torStatus().requests += 1
        shutdown()
