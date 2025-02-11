# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
from enum import unique
from utils import OrderedEnum
import logging
from threading import Lock
from py9tor.worker import AcceptError, Py9torWorker, ReleaseError

@unique
class Intervals(OrderedEnum):
    HOURLY  = 5
    DAILY   = 4
    WEEKLY  = 3
    MONTHLY = 2
    YEARLY  = 1

_mutex = Lock()

with _mutex:
    _queue = {}
    for member in list(Intervals):
        _queue[member] = None

def accept(target):
    logging.debug('accept {}'.format(target))
    logging.debug('accept: queue {}'.format(_queue))
    retval = False

    try:
        logging.debug('accept {}'.format(target['interval'].upper()))
        interval = Intervals[target['interval'].upper()]
        logging.debug('accept: interval {}'.format(interval))
        qObj = _queue[interval]
        logging.debug('accept: qObj {}'.format(qObj))

        if (qObj is None):
            with _mutex:
                qObj = _queue[interval]
                if (qObj is None):
                    _queue[interval] = target
                    for member in list(Intervals):
                        pivot = _queue[member]
                        if (pivot is not None and '_running' in pivot):
                            break
                    else:
                        retval = True
                        target['_running'] = True
        if (qObj is not None):
            logging.warning('accept: target not accepted, already serving {}'.format(qObj))
            raise AcceptError('Target not accepted, already serving {}'.format(qObj))
    except KeyError as e:
        logging.warning('accept: interval not found in target {}'.format(target))
        raise AcceptError from e
    except ValueError as e:
        logging.warning('accept: unknown interval {}'.format(target['interval'].upper()))
        raise AcceptError from e

    logging.debug('accept: queue {}'.format(_queue))
    return retval

def release(target):
    logging.debug('release {}'.format(target))
    logging.debug('release: queue {}'.format(_queue))
    try:
        logging.debug('release {}'.format(target['interval'].upper()))
        interval = Intervals[target['interval'].upper()]
        logging.debug('release: interval {}'.format(interval))
        qObj = _queue[interval]
        logging.debug('release: qObj {}'.format(qObj))

        if (qObj == target):
            with _mutex:
                qObj = _queue[interval]
                if (qObj == target):
                    _queue[interval] = None
                    for member in reversed(list(Intervals)):
                        pivot = _queue[member]
                        if (pivot is not None):
                            logging.debug('release: starting {}'.format(pivot))
                            _queue[member] = None
                            Py9torWorker(pivot['_name']).start()
                            break
        
        if (qObj != target):
            logging.warning('release: target not released, serving {}'.format(qObj))
            raise ReleaseError('Target not released, serving {}'.format(qObj))
    except KeyError as e:
        logging.warning('release: interval not found in target {}'.format(target))
        raise ReleaseError from e
    except ValueError as e:
        logging.warning('release: unknown interval {}'.format(target['interval'].upper()))
        raise ReleaseError from e

    logging.debug('release: queue {}'.format(_queue))
