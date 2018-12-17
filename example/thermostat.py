#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  thermostat.py
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
import yaml

from cocktail.Thing import Thing
from cocktail.Action import *
from cocktail.Event import *

from sepy.SEPA import SEPA
from sepy.SAPObject import SAPObject

from time import sleep
from uuid import uuid4
from random import uniform
from threading import Lock

from dataschemas import ds_threshold, ds_lambda, ds_psi


ThermostatURI = "<http://MyThermostat.swot>"
ThermostatTD = "<http://MyThermostat.swot/TD>"
T_low = 15
T_high = 27
T_start = 3

thresholdLock = Lock()
actuatorListLock = Lock()
actuatorList = []
engine = None


def main(args):
    global engine
    # opening the sap file, and creating the SEPA instance
    with open("./cocktail_sap.ysap", "r") as sap_file:
        ysap = SAPObject(yaml.load(sap_file))
    engine = SEPA(sapObject=ysap)
    if "clear" in args:
        engine.clear()
    
    # Setup the Threshold Action
    threshold_Action = Action(
        engine,
        {"thing": ThermostatURI,
         "td": ThermostatTD,
         "action": "<http://MyThermostat.swot/ThresholdAction>",
         "newName": "ThresholdAction",
         "ids": ds_threshold},
         threshold_update)
    
    # Setup the Event
    temperature_Event = Event(
        engine,
        {"td": ThermostatTD,
         "event": "<http://MyThermostat.swot/TemperatureEvent>",
         "eName": "TemperatureEvent",
         "ods": ds_lambda})
    
    # Setup and post the WebThing
    thermostat = Thing(
        engine,
        {"thing": ThermostatURI,
         "newName": "SmartThermostat",
         "newTD": ThermostatTD}).post(
            interaction_patterns=[threshold_Action, temperature_Event])
            
    # adding context triples
    engine.sparql_update("""
prefix sosa: <http://www.w3.org/ns/sosa/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix ns: <http://wot.arces.unibo.it/localNamespace#>
insert data {{ {} rdf:type sosa:Sensor.
{} sosa:observes ns:Temperature }}""".format(ThermostatURI,ThermostatURI))
    
    # enabling threshold Action
    threshold_Action.enable()
    
    # main thermostat triggering logic
    engine.sparql_subscribe("""
prefix sosa: <http://www.w3.org/ns/sosa/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix ns: <http://wot.arces.unibo.it/localNamespace#>
prefix swot: <http://wot.arces.unibo.it/ontology/web_of_things#>
select ?action where {{
    ?thing  rdf:type swot:Thing, sosa:Actuator;
            sosa:actsOnProperty ns:Temperature;
            swot:hasThingDescription/swot:hasAction ?action.
    ?action swot:hasInputDataSchema {} }}""".format(ds_psi), "thermostat_subscription", handler=available_actuators)
    
    # temperature Event triggering logic
    event_bindings = {"event": temperature_Event.uri, "newDS": ds_lambda}
    while True:
        try:
            sleep(5)
            unique_id = uuid4()
            event_bindings["newEInstance"] = "<http://MyThermostat.swot/TemperatureEvent/Instance_{}>".format(unique_id)
            event_bindings["newOData"] = "<http://MyThermostat.swot/TemperatureEvent/Instance_{}>".format(unique_id)
            event_bindings["newValue"] = str(T_start+uniform(-1,1))
            temperature_Event.notify(event_bindings)
            thresholdLock.acquire()
            if float(event_bindings["newValue"]) < T_low:
                message = '{{"target": {}, "now": "warming"}}'.format(T_low)
                trigger_action(message)
            elif float(event_bindings["newValue"]) > T_high:
                message = '{"target": {}, "now": "cooling"}'.format(T_high)
                trigger_action(message)
            thresholdLock.release()
        except KeyboardInterrupt:
            print("Got KeyboardInterrupt!")
            threshold_Action.disable()
            break
    return 0


def threshold_update(added, removed):
    thresholdLock.acquire()
    print("threshold_update added: {}".format(added))
    print("threshold_update removed: {}".format(removed))
    thresholdLock.release()
    
def available_actuators(added, removed):
    actuatorListLock.acquire()
    for item in added:
        print("Available actuator found: {}".format(item["action"]["value"]))
        actuatorList.append(item["action"]["value"])
    for item in removed:
        actuatorList.remove(item["action"]["value"])
    actuatorListLock.release()
    
def trigger_action(message):
    actuatorListLock.acquire()
    if actuatorList == []:
        print("No trigger targets!")
    else: 
        print("Triggering {}".format(actuatorList))
        bindings = {"newAuthor": ThermostatURI, "newIValue": message, "newIDS": ds_psi}
        for action in actuatorList:
            action_object = Action.buildFromQuery(engine, action)
            unique_id = uuid4()
            bindings["action"] = action
            bindings["newAInstance"] = "<http://MyThermostat.swot/Request/Instance_{}>".format(unique_id)
            bindings["newIData"] = "<http://MyThermostat.swot/Request/Data_{}>".format(unique_id)
            instance, subids = action_object.newRequest(bindings)
    actuatorListLock.release()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
