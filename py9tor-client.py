# Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.
import argparse
import xmlrpc.client
from py9tor.configuration import Py9torConfig
import json

parser = argparse.ArgumentParser(description='Invoke py9tor.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-t', '--target', help='the target to invoke')
group.add_argument('-s', '--status', action="store_true", help='print py9tor status')
args = parser.parse_args()

s = xmlrpc.client.ServerProxy(Py9torConfig().uri(), allow_none=True)

if (args.status):
    status = s.status()
    start = (str)(status['start'])
    status['start'] = start
    print(json.dumps(status, indent=2))
elif (args.target is not None):
    s.start(args.target)
else:
    parser.print_help()
