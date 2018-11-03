#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  reset_results.py
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

from pkg_resources import resource_filename

from sepy.SEPA import SEPA
from sepy.SAPObject import SAPObject
from sepy.tablaze import tablify

from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import *
from cocktail.Event import *
from cocktail import __name__ as cName
from cocktail.utils import generate_cocktail_sap, sparqlFolderToSap, compare_queries

from os.path import isfile, splitext
from os import listdir

import sys
import argparse
import logging
import yaml

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def read_all_file(filename):
    path = resource_filename(__name__, filename)
    with open(path, "r") as myFile:
        content = myFile.read()
    return content

def setUp(engine):
    engine.clear()
    engine.sparql_update(read_all_file("insert_thing_1.sparql"))
    engine.sparql_update(read_all_file("insert_thing_2.sparql"))
    engine.sparql_update(read_all_file("insert_thing_3.sparql"))
    
def rebuild_test_0(engine):
    setUp(engine)
    target = resource_filename(__name__,"res_query_all.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query_all(destination=target)
    
def rebuild_test_1(engine):
    setUp(engine)
    dir_path = resource_filename(cName,"queries")
    for fileName in listdir(dir_path):
        filePath = dir_path + "/" + fileName
        if (isfile(filePath) and (splitext(filePath)[1] == ".sparql")):
            sapKey = list(sparqlFolderToSap(dir_path,file_filter=fileName).keys())[0]
            target = resource_filename(__name__,splitext("res_"+fileName)[0]+".json")
            logging.warning("Rebuilding {}".format(target))
            engine.query(sapKey,destination=target)
            
def rebuild_test_2(engine):
    setUp(engine)
    target = resource_filename(__name__,"res_new_thing.json")
    logging.warning("Rebuilding {}".format(target))
    SUPERTHING = "<http://MyFirstWebThing.com>"
    THING_URI = "<http://TestThing.com>"
    Thing(engine, 
          {"thing": THING_URI,
           "newName": "TEST-THING",
           "newTD": "<http://TestTD.com>"},
          superthing=SUPERTHING).post()
    query = engine.sap.getQuery("DISCOVER_THINGS").replace("(UNDEF UNDEF UNDEF)",
            "({} UNDEF UNDEF) ({} UNDEF UNDEF)".format(THING_URI,SUPERTHING))
    engine.sparql_query(query,destination=target)
    
def rebuild_test_3(engine):
    setUp(engine)
    THING_URI = "<http://TestThing.com>"
    PROPERTY_URI = "<http://TestProperty.com>"
    NEW_PROPERTY_VALUE = "HIJKLMNOP"
    TEST_TD = "<http://TestTD.com>"
    DataSchema(
        engine,
        {"ds_uri": "<http://TestThing.com/Property1/DataSchema/property>",
         "fs_uri": "xsd:string",
         "fs_types": "xsd:_, wot:FieldSchema"}).post()
    dummyThing = Thing(
        engine,
        {"thing": THING_URI,
         "newName": "TEST-THING",
         "newTD": TEST_TD}).post()
    p_fBindings = {"td": TEST_TD,
                   "property": PROPERTY_URI,
                   "newName": "TEST-PROPERTY",
                   "newStability": "1",
                   "newWritability": "true",
                   "newDS": "<http://TestThing.com/Property1/DataSchema/property>",
                   "newPD": "<http://TestThing.com/Property1/PropertyData>",
                   "newValue": "ABCDEFG"}
    testProperty = Property(engine, p_fBindings).post()
    target = resource_filename(__name__,"res_new_property_create.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query(
        "DESCRIBE_PROPERTY",
        forcedBindings={"property_uri": PROPERTY_URI},
        destination=target)
    # Updating property with a new writability and a new value
    p_fBindings["newWritability"] = "false"
    p_fBindings["newValue"] = NEW_PROPERTY_VALUE
    testProperty.update(p_fBindings)
    target = resource_filename(__name__,"res_new_property_update.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query(
        "DESCRIBE_PROPERTY",
        forcedBindings={"property_uri": PROPERTY_URI},
        destination=target)
    testProperty.delete()
    dummyThing.delete()
    target = resource_filename(__name__,"res_query_all_new_dataschema.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query_all(destination=target)
    
def rebuild_test_4(engine):
    setUp(engine)
    THING_URI = "<http://TestThing.com>"
    DS_URI_INPUT = "<http://TestThing.com/Actions/DataSchema/input>"
    DS_URI_OUTPUT = "<http://TestThing.com/Actions/DataSchema/output>"

    # Adding new Action Dataschemas and its corresponding FieldSchema
    DataSchema(engine,
               {"ds_uri": DS_URI_INPUT,
                "fs_uri": "xsd:string",
                "fs_types": "xsd:_, wot:FieldSchema"}).post()
    DataSchema(engine,
               {"ds_uri": DS_URI_OUTPUT,
                "fs_uri": "xsd:integer",
                "fs_types": "xsd:_, wot:FieldSchema"}).post()

    # Adding the new thing
    dummyThing = Thing(
        engine,
        {"thing": THING_URI,
         "newName": "TEST-THING",
         "newTD": "<http://TestTD.com>"}).post()

    # Adding new Actions and then query the output
    actions = []
    for aType in list(AType):
        actions.append(Action(
            engine,
            {"td": "<http://TestTD.com>",
             "action": "<http://TestAction_{}.com>".format(aType.value.lower()),
             "newName": "TEST-ACTION-{}".format(aType.value.lower()),
             "ids": DS_URI_INPUT,
             "ods": DS_URI_OUTPUT},
            lambda: None,
            force_type=aType).post())

    sparql_query = engine.sap.getQuery("DESCRIBE_ACTION").replace(
        "(UNDEF)",
        "(<http://TestAction_io.com>) (<http://TestAction_i.com>) (<http://TestAction_o.com>) (<http://TestAction_empty.com>)")
    target = resource_filename(__name__, "res_new_actions_create.json")
    logging.warning("Rebuilding {}".format(target))
    query_result = engine.sparql_query(sparql_query,destination=target)

    # Deleting the actions
    for action in actions:
        action.delete()
    # Query all check
    dummyThing.delete()
    target = resource_filename(__name__,"res_query_all_new_dataschema_actions.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query_all(destination=target)

def rebuild_test_5(engine):
    setUp(engine)
    THING_URI = "<http://TestThing.com>"
    DS_URI_OUTPUT = "<http://TestThing.com/Events/DataSchema/output>"

    # Adding new Action Dataschema and its corresponding FieldSchema
    DataSchema(engine,
               {"ds_uri": DS_URI_OUTPUT,
                "fs_uri": "xsd:integer",
                "fs_types": "xsd:_, wot:FieldSchema"}).post()

    # Adding the new thing
    dummyThing = Thing(engine,
                       {"thing": THING_URI,
                        "newName": "TEST-THING",
                        "newTD": "<http://TestTD.com>"}).post()

    # Adding new Actions and then query the output
    events = []
    for eType in list(EType):
        events.append(Event(
            engine,
            {"td": "<http://TestTD.com>",
             "event": "<http://TestEvent_{}.com>".format(eType.value.lower()),
             "eName": "TEST-EVENT-{}".format(eType.value.lower()),
             "ods": DS_URI_OUTPUT}, force_type=eType).post())

    # Querying the events
    sparql_query = engine.sap.getQuery("DESCRIBE_EVENT").replace(
        "(UNDEF)",
        "(<http://TestEvent_o.com>) (<http://TestEvent_empty.com>)")
    target = resource_filename(__name__, "res_new_events_create.json")
    logging.warning("Rebuilding {}".format(target))
    engine.sparql_query(sparql_query,destination=target)

    # Deleting the events
    for event in events:
        event.delete()
    # Query all check
    dummyThing.delete()
    target = resource_filename(__name__, "res_query_all_new_dataschema_events.json")
    logging.warning("Rebuilding {}".format(target))
    engine.query_all(destination=target)
    
def rebuild_test_6(engine):
    setUp(engine)
    # retrieving actions from SEPA: those are inferred
    actions = [
        Action.buildFromQuery(
            engine, "<http://MyFirstWebThing.com/Action1>"),
        Action.buildFromQuery(
            engine, "<http://MyThirdWebThing.com/Action1>")]
    # Adding the instances
    for index, action in enumerate(actions):
        bindings = {"thing": action.thing,
                    "action": action.uri,
                    "newAInstance": action.uri.replace(">", "/instance1>"),
                    "newAuthor": "<http://MySecondWebThing.com>",
                    "newIData": action.uri.replace(">", "/instance1/InputData>"),
                    "newIValue": "This is an input string",
                    "newIDS": action.uri.replace(">", "/DataSchema/input>")}
        # the following line triggers task_iteration==1,
        # confirm_iteration==0, complete_iteration==0
        instance, subids = action.newRequest(bindings)
        target = resource_filename(__name__,"res_new_{}_action_instance.json".format(action.type.value.lower()))
        logging.warning("Rebuilding {}".format(target))
        engine.query("SUBSCRIBE_ACTION_INSTANCE",forcedBindings=action.bindings,destination=target)

        # # Adding and checking Confirmation and Completion timestamps
        # actions_copy[index].post_confirmation(instance)  # triggers confirm_iteration==1
        # actions_copy[index].post_completion(instance)  # triggers complete_iteration==1
        # # Update the instances
        # bindings["newAInstance"] = action.uri.replace(">", "/instance2>")
        # if action.type == AType.INPUT_ACTION:
            # bindings["newIData"] = action.uri.replace(">", "/instance2/InputData>")
            # bindings["newIValue"] = "This is a modified input string"

        # def out_handler(added, removed):
            # self.assertTrue(switch_handler(
                # added, "res_new_instance_output.json"))
            # if added:
                # self.engine.unsubscribe(subids["output"])

        # instance, subids = action.newRequest(
            # bindings, confirm_handler=confirm_handler,
            # completion_handler=complete_handler,
            # output_handler=out_handler)

        # # Adding and checking Confirmation and Completion timestamps
        # actions_copy[index].post_confirmation(instance)  # triggers confirm_iteration==1
        # actions_copy[index].post_completion(instance)  # triggers complete_iteration==1
        # if action.type == AType.IO_ACTION or action.type == AType.OUTPUT_ACTION:
            # # Post output
            # actions_copy[index].post_output(
                # {"instance": instance,
                 # "oData": action.uri.replace(">", "/instance2/OutputData>"),
                 # "oValue": "my output value",
                 # "oDS": action.uri.replace(">", "/DataSchema/output>")})
        # # Remove instances and outputs
        # actions_copy[index].disable()
        # actions_copy[index].deleteInstance(instance)

def main(args):
    logging.info("Setting up SAP objects and SEPA engine object...")
    sap_file = generate_cocktail_sap(None)
    ysap = SAPObject(yaml.load(sap_file))
    engine = SEPA(sapObject=ysap,logLevel=logging.INFO)
    
    rebuild_test_0(engine)
    rebuild_test_1(engine)
    rebuild_test_2(engine)
    rebuild_test_3(engine)
    rebuild_test_4(engine)
    rebuild_test_5(engine)
    rebuild_test_6(engine)
        
    # test 4
    
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
