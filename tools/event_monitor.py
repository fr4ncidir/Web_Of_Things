#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event_monitor.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import argparse
import importlib.util as iutil

from sepy.SAPObject import SAPObject, uriFormat
from sepy.SEPA import SEPA

def event_monitor(sap_file, event_uri, handler=None):
    return main({"sap_file": sap_file,
                 "event_uri": event_uri,
                 "handler": handler})


def main(args):
    ysap = SAPObject(yaml.load(args["sap_file"]))
    engine = SEPA(sapObject=ysap, logLevel=logging.ERROR)
    
    observed = Event.buildFromQuery(sepa, uriFormat(args["event_uri"]))
    
    if args["handler"] is None:
        def event_handler(added,removed):
            print("--------------EVENT HANDLER--------------")
            print("Added: {}\nRemoved: {}".format(added, removed))
            print("------------EVENT HANDLER END------------")
    else:
        spec = iutil.spec_from_file_location("module.name",args["handler"])
        module = iutil.module_from_spec(spec)
        spec.loader.exec_module(module)
        event_handler = module.handler
    
    observed.observe(event_handler)
    try:
        print("CTRL-C to stop observing...")
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observed.stop_observing()
        print("Bye Bye!")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Event monitor")
    parser.add_argument("sap_file", help="Path to sap file")
    parser.add_argument("event_uri", help="Uri of the action to be requested")
    parser.add_argument("--handler", default=None, help="Custom handler")
    arguments = vars(parser.parse_args())
    sys.exit(main(arguments))
