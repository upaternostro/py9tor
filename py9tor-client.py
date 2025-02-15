# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import argparse
import xmlrpc.client
from py9tor.configuration import Py9torConfig

parser = argparse.ArgumentParser(description='Invoke py9tor.')
parser.add_argument('target', type=str, 
                    help='the target to invoke')
args = parser.parse_args()

s = xmlrpc.client.ServerProxy(Py9torConfig().uri(), allow_none=True)

s.start(args.target)
