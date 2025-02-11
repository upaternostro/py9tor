# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import json
import logging
import copy

CONFIG_NAME = 'config.json'

class Py9torConfig:
    _host = 'localhost'
    _port = 8000
    _targets = {}

    def __init__(self):
        self.__class__.__new__ = lambda _: self
        self.__class__.__init__ = lambda *_, **__: None
        try:
            with open(CONFIG_NAME) as f:
                config = json.load(f)
                if ('host' in config):
                    self._host = config['host']
                if ('port' in config):
                    self._port = config['port']
                if ('targets' in config):
                    self._targets = config['targets']
        except FileNotFoundError:
            logging.error('Configuratiuon file {} not found, using defaults'.format(CONFIG_NAME))
        logging.debug('host: {}'.format(self._host))
        logging.debug('port: {}'.format(self._port))
        logging.debug('targets: {}'.format(self._targets))
        logging.debug('{} created'.format(__name__))
    
    def addr(self):
        return ( self._host, self._port )
    
    def uri(self):
        return f'http://{self._host}:{self._port}'
    
    def getTarget(self, target):
        targetObj = copy.deepcopy(self._targets[target])
        return targetObj
