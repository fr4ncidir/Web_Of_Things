#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  benchmark_dataschemas.py
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

from cocktail.DataSchema import DataSchema

BOOLEAN_DS_URI = "ct:BooleanDataSchema"
BOOLEAN_FS_URI = "_:BNBooleanDS"

DOUBLE_DS_URI = "ct:DoubleDataSchema"
DOUBLE_FS_URI = "_:BNDoubleDS"

LBLINK_DS_URI = "ct:LightBlinkDataSchema"
LBLINK_FS_URI = "ct:LightBlinkJSONFieldSchema"


def boolean_dataschema(engine):
    # smoke sensors, gas actuator
    return DataSchema(
        engine,
        {"ds_uri": BOOLEAN_DS_URI,
         "fs_uri": BOOLEAN_FS_URI,
         "fs_types": "xsd:boolean, wot:FieldSchema"}).post()


def double_dataschema(engine):
    # temperature sensor, sound volume
    return DataSchema(
        engine,
        {"ds_uri": DOUBLE_DS_URI,
         "fs_uri": DOUBLE_FS_URI,
         "fs_types": "xsd:double, wot:FieldSchema"}).post()


def light_blink_dataschema(engine):
    # light blinking frequency, plus on/off
    return DataSchema(
        engine,
        {"ds_uri": LBLINK_DS_URI,
         "fs_uri": LBLINK_FS_URI,
         "fs_types": "xsd:Literal, wot:FieldSchema"}).post()
