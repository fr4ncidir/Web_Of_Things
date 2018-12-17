#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hotcold.py
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
from cocktail.Action import *
from cocktail.Event import *

from sepy.SEPA import SEPA
from sepy.SAPObject import SAPObject

from dataschemas import ds_psi, ds_lambda
from time import sleep
from threading import Lock

import yaml
import json
import sys


HotColdURI = "<http://HotCold.swot>"
HotColdTD = "<http://HotCold.swot/TD>"
HotColdActionURI = "<http://HotCold.swot/MainHotColdAction>"
temperatureSensorsList = {}
engine = None
HotColdLock = Lock()
CurrentStatus = "off"
CurrentTarget = 15

def main(args):
    global engine
    global CurrentStatus
    # opening the sap file, and creating the SEPA instance
    with open("./cocktail_sap.ysap", "r") as sap_file:
        ysap = SAPObject(yaml.load(sap_file))
    engine = SEPA(sapObject=ysap)
    if "clear" in args:
        engine.clear()
        
    # Setup the Hot/Cold Action
    mainHC_Action = Action(
        engine,
        {"thing": HotColdURI,
         "td": HotColdTD,
         "action": HotColdActionURI,
         "newName": "MainHotColdAction",
         "ids": ds_psi},
         mainHotColdActionLogic)
        
    # Setup and post the WebThing
    thermostat = Thing(
        engine,
        {"thing": HotColdURI,
         "newName": "HotCold",
         "newTD": HotColdTD}).post(interaction_patterns=[mainHC_Action])
         
    mainHC_Action.enable()
    
    # adding context triples
    engine.sparql_update("""
prefix sosa: <http://www.w3.org/ns/sosa/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix ns: <http://wot.arces.unibo.it/localNamespace#>
insert data {{ {} rdf:type sosa:Actuator.
{} sosa:actsOnProperty ns:Temperature }}""".format(HotColdURI,HotColdURI))

    # main hotcold event search logic
    engine.sparql_subscribe("""
prefix sosa: <http://www.w3.org/ns/sosa/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix ns: <http://wot.arces.unibo.it/localNamespace#>
prefix swot: <http://wot.arces.unibo.it/ontology/web_of_things#>
select ?event where {{
    ?thing  rdf:type swot:Thing, sosa:Sensor;
            sosa:observes ns:Temperature;
            swot:hasThingDescription/swot:hasEvent ?event.
    ?action swot:hasOutputDataSchema {} }}""".format(ds_lambda), "hotcold_subscription", handler=available_sensors)
    
    while True:
        try:
            sleep(10)
            print("Device status is currently {}".format(CurrentStatus))
        except KeyboardInterrupt:
            print("Got KeyboardInterrupt!")
            mainHC_Action.disable()
            break
    return 0
    

def mainHotColdActionLogic(added, removed):
    global CurrentStatus
    global CurrentTarget
    for item in added:
        parameter = json.loads(item["iValue"]["value"])
        author = item["author"]["value"]
        if parameter["now"] == CurrentStatus:
            print("Ignoring {}'s request: already doing it".format(author))
        else:
            print("{} requested execution of {} at {} with parameter {}".format(
                author, HotColdActionURI, item["aTS"]["value"], parameter))
            HotColdLock.acquire()
            CurrentStatus = parameter["now"]
            CurrentTarget = parameter["target"]
            HotColdLock.release()
    

def available_sensors(added, removed):
    # elaborate the list
    for item in added:
        event = item["event"]["value"]
        if event not in temperatureSensorsList.keys():
            sensorEvent = Event.buildFromQuery(engine, event)
            temperatureSensorsList[event] = sensorEvent
        print("Available sensor found: {}".format(event))
        temperatureSensorsList[event].observe(temperature_handler)
    for item in removed:
        temperatureSensorsList[item["event"]["value"]].stop_observing()
    
    
def temperature_handler(added, removed):
    global CurrentStatus
    for item in added:
        temperature = float(item["oValue"]["value"])
        print("Received new temperature: {}°C".format(temperature))
        if ((CurrentStatus=="warming") and (temperature > CurrentTarget)) or ((CurrentStatus=="cooling") and (temperature < CurrentTarget)):
            print("Switching off the heating/cooling device")
            HotColdLock.acquire()
            CurrentStatus = "off"
            HotColdLock.release()
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
