#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  action_request.py
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

import argparse
import sys
import yaml
import importlib.util as iutil

from uuid import uuid4
from cocktail.Action import *
from sepy.SAPObject import SAPObject, uriFormat
from sepy.SEPA import SEPA

ACTION_REQUESTOR_URI = "<http://wot.action.requestor.it>"


def actionRequestor(sap_file, action_uri, aInput="",
                    dataschema="", handler=None):
    return main({"sap_file": sap_file,
                 "action_uri": action_uri,
                 "input": aInput,
                 "dataschema": dataschema,
                 "handler": handler})


def input_getter(path_to_input):
    with open(path_to_input, "r") as myInput:
        content = myInput.read()
    return content


def main(args):
    ysap = SAPObject(yaml.load(args["sap_file"]))
    engine = SEPA(sapObject=ysap, logLevel=logging.ERROR)
    
    def confirm_handler(added, removed):
        print("--------------CONFIRM HANDLER--------------")
        print("Added: {}\nRemoved: {}".format(added, removed))
        print("------------CONFIRM HANDLER END------------")
        if added:
            engine.unsubscribe(subids["confirm"])

    def complete_handler(added, removed):
        print("-------------COMPLETE HANDLER--------------")
        print("Added: {}\nRemoved: {}".format(added, removed))
        print("-----------COMPLETE HANDLER END------------")
        if added:
            engine.unsubscribe(subids["completion"])
    
    action = Action.buildFromQuery(self.engine, uriFormat(args["action_uri"]))
    if (action.type is AType.IO_ACTION) or (action.type is AType.OUTPUT_ACTION):
        if args["handler"] is None:
            def out_handler(added, removed):
                print("-------------_OUTPUT HANDLER--------------")
                print("Added: {}\nRemoved: {}".format(added, removed))
                print("-----------_OUTPUT HANDLER END------------")
                if added:
                    self.engine.unsubscribe(subids["output"])
        else:
            spec = iutil.spec_from_file_location("module.name",args["handler"])
            module = iutil.module_from_spec(spec)
            spec.loader.exec_module(module)
            out_handler = module.handler
    else:
        out_handler = None
    
    instance_uuid = action.uri.replace(">", "/instance{}>".format(uuid4()))
    bindings = {"thing": action.thing,
                "action": action.uri,
                "newAInstance": instance_uuid,
                "newAuthor": ACTION_REQUESTOR_URI,
                "newIData": instance_uuid.replace(">", "/InputData>"),
                "newIValue": input_getter(args["input"]),
                "newIDS": args["dataschema"]}
            
    instance, subids = action.newRequest(
        bindings, confirm_handler=confirm_handler,
        completion_handler=complete_handler,
        output_handler=out_handler)
        
    try:
        print("CTRL-C to stop observing...")
        while True:
            sleep(10)
    except KeyboardInterrupt:
        print("Bye Bye!")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Action requestor")
    parser.add_argument("sap_file", help="Path to sap file")
    parser.add_argument("action_uri", help="Uri of the action to be requested")
    parser.add_argument("--input", default="", help="Path to text file containing input value")
    parser.add_argument("--dataschema", default="", help="Input corresponding dataschema")
    parser.add_argument("--handler", default=None, help="Custom output handler")
    arguments = vars(parser.parse_args())
    sys.exit(main(arguments))
