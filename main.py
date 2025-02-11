# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import logging
import logging.config
from py9tor.status import Py9torStatus
from py9tor.server import serve

NAME  = 'py9tor'
LOGGING_CONF = 'logging.conf'

try:
    logging.config.fileConfig(LOGGING_CONF)
except FileNotFoundError:
    logging.warning('Using default log configuration, {} not found'.format(LOGGING_CONF))

logging.info('{} starting'.format(NAME))

Py9torStatus()
serve()
