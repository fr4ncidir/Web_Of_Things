#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  temperature.py
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
import json

from dataschemas import YSAPEngine

from sepy.SEPA import SEPA
from sepy.SAPObject import SAPObject

from cocktail.Property import *


def simulator(engine, current_temperature, seconds):
    try:
        result = Property.discover(engine, prop="<http://HotCold.swot/MainHotColdProperty>")
        now = json.loads(result["results"]["bindings"][0]["pValue"]["value"])["now"]
    except Exception:
        return current_temperature
    if now == "off":
        return current_temperature
    elif now == "warming":
        return current_temperature+seconds
    else:
        return current_temperature-seconds
    

def main(args):
    engine = YSAPEngine("./example.ysap")
    engine.update("ADD_CONTEXT_TRIPLES")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
