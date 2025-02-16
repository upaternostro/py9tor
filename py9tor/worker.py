# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import logging
from py9tor.configuration import Py9torConfig
from py9tor.status import Py9torStatus
import time
import threading
import utils
import subprocess
from importlib import import_module

class AcceptError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class ReleaseError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Py9torWorker(threading.Thread):
    def __init__(self, target):
        super().__init__()
        self.target = target
    
    def run(self):
        logging.debug('running {}'.format(self.target))

        try:
            targetObj = Py9torConfig().getTarget(self.target)
            # inject name for later usage (see py9tor.rsnapshot.release())
            targetObj['_name'] = self.target
            logging.debug('target {}'.format(targetObj))

            if ('handler' in targetObj):
                handler_module = import_module(targetObj['handler'])
                execute_it = handler_module.accept(targetObj)
            else:
                handler_module = None
                execute_it = True
            
            if (execute_it):
                x = utils.import_class_from_string(targetObj['class'])(targetObj['attrs'])
                Py9torStatus().running += 1
                Py9torStatus().executing.append(targetObj)
                logging.info('Running {}'.format(self.target))
                x.exec()
                logging.info('{} terminated'.format(self.target))
                Py9torStatus().executing.remove(targetObj)
                Py9torStatus().running -= 1
                if (handler_module is not None):
                    handler_module.release(targetObj)
        except KeyError:
            logging.error('key {} not found'.format(self.target))
        except AcceptError:
            logging.warning('target {} not accepted'.format(self.target))
        except ModuleNotFoundError:
            logging.error('handler module {} not found'.format(targetObj['handler']))

class Py9torExecutor:
    def __init__(self, attrs):
        self.attrs = attrs
    
    def exec(self):
        pass

class DummyExecutor(Py9torExecutor):
    def exec(self):
        logging.debug('DummyExecutor.exec(): starting')
        logging.debug('DummyExecutor.exec(): self.attrs: {}'.format(self.attrs))
        time.sleep(self.attrs['time'])
        logging.debug('DummyExecutor.exec(): terminating')

class LocalExecutor(Py9torExecutor):
    def exec(self):
        logging.debug('LocalExecutor.exec(): starting')
        logging.debug('LocalExecutor.exec(): self.attrs: {}'.format(self.attrs))
        process = subprocess.run(self.attrs['args'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                user=self.attrs['user'] if 'user' in self.attrs else None, 
                                universal_newlines=True)
        if process.returncode != 0:
            logging.error('LocalExecutor.exec(): process: {}'.format(process))
        else:
            logging.debug('LocalExecutor.exec(): completed successfully, process: {}'.format(process))

        logging.debug('LocalExecutor.exec(): terminating')

class SSHExecutor(Py9torExecutor):
    def exec(self):
        logging.debug('SSHExecutor.exec(): starting')
        logging.debug('SSHExecutor.exec(): self.attrs: {}'.format(self.attrs))
        ssh = subprocess.Popen([
                                    'ssh', 
                                    '-F', '/dev/null', 
                                    '-i', self.attrs['key'], 
                                    '-l', self.attrs['user'], 
                                    '-o', 'UserKnownHostsFile=/dev/null',
                                    '-o', 'StrictHostKeyChecking=no',
                                    self.attrs['host'],
                                    '-p', self.attrs['port'] if 'port' in self.attrs else '22'
                                ],
                                stdin =subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                bufsize=0)
        
        # Send ssh commands to stdin
        for cmd in self.attrs['cmds']:
            ssh.stdin.write('{}\n'.format(cmd))

        ssh.stdin.close()
        ssh.wait()

        for output in ssh.stdout.readlines():
            logging.debug(output.strip())

        for output in ssh.stderr.readlines():
            logging.debug(output.strip())

        if ssh.returncode != 0:
            logging.error('SSHExecutor.exec(): self.attrs: {}'.format(ssh))
        else:
            logging.debug('SSHExecutor.exec(): completed successfully')

        logging.debug('SSHExecutor.exec(): terminating')
