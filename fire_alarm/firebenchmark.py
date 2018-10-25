#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  firebenchmark.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
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

from sepy.Sepa import Sepa as Engine

from cocktail.DataSchema import DataSchema

import argparse

def dataschema_builder(engine):
    bindings = dict.fromkeys(DataSchema.getBindingList(),"")
    bindings["fs_types"] = "xsd:_"
    
    # smoke sensor and gas emitter actuator share the same dataschema
    bindings["ds_uri"] = "<http://dataschema.wot/xsd_boolean>"
    bindings["fs_uri"] = "xsd:boolean"
    smoke_gas_DS = DataSchema(engine,bindings)
    smoke_gas_DS.post()
    
    bindings["ds_uri"] = "<http://dataschema.wot/xsd_double>"
    bindings["fs_uri"] = "xsd:double"
    # bindings["fs_types"] = "xsd:_" # unchanged from above
    temperature_DS = DataSchema(engine,bindings)
    temperature_DS.post()
    
    bindings["ds_uri"] = "<http://dataschema.wot/acoustic_signal>"
    bindings["fs_uri"] = "<http://fieldschema.wot/acoustic_signal_jsonschema>" 
# {
#   "$schema": "http://wot.unibo.it/acoustic_signal_schema",
#   "type": "object",
#   "properties":{
#       "db":{
#           "type":"number"
#       },
#       "len":{
#           "type":"integer"
#       }
#   }
# }
    alarm_DS = DataSchema(engine,bindings)
    alarm_DS.post()
    
    bindings["ds_uri"] = "<http://dataschema.wot/light_signal>"
    bindings["fs_uri"] = "<http://fieldschema.wot/light_signal_jsonschema>"
    light_DS = DataSchema(engine,bindings)
    light_DS.post()

def main(args):
    sepa = Engine(  ip = args["ip"],
                http_port = args["query_port"],
                ws_port = args["sub_port"],
                security = {"secure": args["security"], 
                            "tokenURI": args["token_uri"], 
                            "registerURI": args["registration_uri"]})
    
    try:
        # Checking if SEPA is online, erasing content before test
        sepa.clear()
    except Exception as e:
        print(str(e))
        return 1
    
    dataschema_builder(sepa)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Fire Alarm Benchmark")
    parser.add_argument("-ip", default="localhost", help="Sepa ip")
    parser.add_argument("-query_port", default=8000, help="Sepa query/update port")
    parser.add_argument("-sub_port", default=9000, help="Sepa subscription port")
    parser.add_argument("-token_uri", default=None, help="Sepa token uri")
    parser.add_argument("-registration_uri", default=None, help="Sepa registration uri")
    parser.add_argument("rooms",help="Number of rooms for the benchmark")
    arguments = vars(parser.parse_args())
    if ((arguments["token_uri"] is not None) and (arguments["registration_uri"] is not None)):
        arguments["security"] = True
    else:
        arguments["security"] = False
    sys.exit(main(arguments))
