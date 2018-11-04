#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  TempSensor.py
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
from cocktail.Event import Event
from sepy.SAPObject import expand_prefixed_uri as epu


class TempSensor:
    def __init__(self, engine, thingUri, thingName, thingTD, dataschema):
        nss = engine.sap.get_namespaces()
        self.webThing = Thing(
            engine, {"thing": epu(thingUri, nss),
                     "newName": thingName,
                     "newTD": epu(thingTD, nss)}).post()
        self.webThingEvent = Event(
            engine, {"td": self.webThing.td,
                     "event": epu(thingUri+"/temperatureEvent", nss),
                     "eName": self.webThing.name+"_event",
                     "ods": dataschema["double"]}).post()
                     
    def start(self):
        
        def tempSensorHandler(added, removed):
            pass

        self.webThingEvent.observe(tempSensorHandler)
    
    def stop(self):
        self.webThingEvent.stop_observing()
