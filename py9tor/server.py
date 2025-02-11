# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
from xmlrpc.server import SimpleXMLRPCServer
import threading
from py9tor.facade import Py9torFacade
from py9tor.configuration import Py9torConfig

_server = None

def serve():
    # see https://docs.python.org/3/library/xmlrpc.server.html#simplexmlrpcserver-example
    # Create server
    with SimpleXMLRPCServer(Py9torConfig().addr(), allow_none=True, logRequests=False) as server:
        server.register_introspection_functions()

        # Register an instance; all the methods of the instance are
        # published as XML-RPC methods (in this case, just 'mul').
        server.register_instance(Py9torFacade())

        # Memorize server to use it in shutdown action (see below)
        global _server
        _server = server

        # Run the server's main loop
        server.serve_forever()

def shutdown():
    class ServerKiller(threading.Thread):
        def run(self):
            _server.shutdown()
    
    ServerKiller().start()
