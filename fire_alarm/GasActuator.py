#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  GasActuator.py
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

from cocktail.Thing import Thing
from cocktail.Action import Action
from sepy.SAPObject import expand_prefixed_uri as epu


class GasActuator:
    def __init__(self, engine, thingUri, thingName, thingTD, dataschema):
        nss = engine.sap.get_namespaces()
        self.webThing = Thing(
            engine, {"thing": epu(thingUri, nss),
                     "newName": thingName,
                     "newTD": epu(thingTD, nss)}).post()
                     
        self.startAction = Action(
            engine, {"td": self.webThing.td,
                     "action": epu(thingUri+"/start", nss),
                     "newName": self.webThing.name+"_startGas",
                     "ids": dataschema["boolean"]},
            lambda a, r: None).post()
                     
    def enable(self):
        
        def startGas(added, removed):
            pass

        self.startAction.action_task = startGas
        self.startAction.enable()
        
    def disable(self):
        self.startAction.disable()
