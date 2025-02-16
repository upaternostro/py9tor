# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import logging
from threading import Lock
from py9tor.worker import AcceptError, Py9torWorker, ReleaseError

_mutex = Lock()

with _mutex:
    _instances = {}

def accept(target):
    logging.debug('accept {}'.format(target))
    logging.debug('accept: instances {}'.format(_instances))
    retval = False

    logging.debug('accept: max instances {}'.format(target['instances']))
    with _mutex:
        try:
            running_instances = _instances[target['_name']]
            if (running_instances is None):
                running_instances = 0
        except KeyError:
            running_instances = 0
        if (running_instances < target['instances']):
            retval = True
            running_instances += 1
            _instances[target['_name']] = running_instances

    if (not retval):
        logging.warning('accept: target not accepted, already serving {} instance(s)'.format(running_instances))
        raise AcceptError('Target not accepted, already serving {} instance(s)'.format(running_instances))

    logging.debug('accept: instances {}'.format(_instances))
    return retval

def release(target):
    logging.debug('release {}'.format(target))
    logging.debug('release: instances {}'.format(_instances))

    with _mutex:
        running_instances = _instances[target['_name']]
        if (running_instances > 0):
            running_instances -= 1
            _instances[target['_name']] = running_instances

    logging.debug('release: instances {}'.format(_instances))
