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
import argparse
import yaml
import logging
import re

from sepy.SAPObject import SAPObject
from sepy.SEPA import SEPA
from cocktail.utils import generate_cocktail_sap
from benchmark_dataschemas import *
from Room import Room
from time import time

PREFIX_COCKTAIL_BENCHMARK = ("ct", "http://Cocktail/Benchmark#")

logger = logging.getLogger("CocktailBenchmarkLogger")
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format='%(filename)s:%(funcName)s:%(levelname)s:%(message)s',
    level=logging.DEBUG)


def benchmark_core(engine, profile, roomArray):
    with open(profile, "w") as benchmark_profile:
        while True:
            line = benchmark_profile.readline()
            if line.startswith("#"):
                continue
            elif line != "":
                pass
            else:
                break


def main(args):
    sap_file = generate_cocktail_sap(None)
    ysap = SAPObject(yaml.load(sap_file))
    ysap.update_namespaces(
        PREFIX_COCKTAIL_BENCHMARK[0], PREFIX_COCKTAIL_BENCHMARK[1])
    engine = SEPA(sapObject=ysap, logLevel=logging.INFO)
    engine.clear()
    
    setupStartTime = time()
    # setting up dataschemas
    dataschemas = {"boolean": boolean_dataschema(engine).uri,
                   "double": double_dataschema(engine).uri,
                   "light_blink": light_blink_dataschema(engine).uri}
    
    room_array = [Room(engine, i, dataschemas).run()
                  for i in range(int(args["rooms"]))]
    logger.info("Setup elapsed time: {}".format(time() - setupStartTime))
    
    triple_total = engine.sparql_query(
        "SELECT (COUNT(?s) AS ?triples) WHERE { ?s ?p ?o }")
    logger.info("Total number of triples: {}".format(
        triple_total["results"]["bindings"][0]["triples"]["value"]))
    
    benchmark_core(engine, args["profile"], room_array)
    
    for room in room_array:
        room.shutdown()
    
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WoT Fire Alarm Benchmark")
    parser.add_argument("rooms", help="Number of rooms")
    parser.add_argument("profile", help="benchmark profile")
    arguments = vars(parser.parse_args())
    sys.exit(main(arguments))
