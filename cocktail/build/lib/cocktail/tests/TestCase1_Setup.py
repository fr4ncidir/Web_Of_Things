#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  TestCase1_Setup.py
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

import unittest
import yaml

from pkg_resources import resource_filename

from sepy.SEPA import SEPA
from sepy.SAPObject import SAPObject

from cocktail.Thing import Thing
from cocktail.DataSchema import DataSchema
from cocktail.Property import Property
from cocktail.Action import *
from cocktail.Event import *
from cocktail.utils import generate_cocktail_sap, compare_queries
    
xsd_string = "xsd:string"
xsd_integer = "xsd:integer"
xsd_dateTimeStamp = "xsd:dateTimeStamp"
xsd_ = "xsd:_"
xsd_literal = "xsd:Literal"
wot_FieldSchema = "wot:FieldSchema"

def read_all_file(filename):
    path = resource_filename(__name__,filename)
    with open(path,"r") as myFile:
        content = myFile.read()
    return content

class TestCase1_Setup(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sap_file = generate_cocktail_sap(None)
        self.ysap = SAPObject(yaml.load(sap_file))
        self.engine = SEPA(sapObject=self.ysap,logLevel=logging.ERROR)
        
    def setUp(self):
        self.engine.clear()
        
    def test_0(self):
        """
        This test checks if the sparql insert of Thing1 and the sum of 
        cocktail sparqls have the same effect in the rdf store.
        """
        
        self.engine.sparql_update(read_all_file("insert_thing_1.sparql"))
        
        thing_descriptor = "<http://MyFirstWebThingDescription.com>"
        query_all_sparql = self.engine.query_all()
        self.engine.clear()
        
        ds1 = DataSchema(self.engine, 
            { "ds_uri": "<http://MyFirstWebThing.com/Action1/DataSchema/input>",
            "fs_uri": xsd_string,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds2 = DataSchema(self.engine, 
                { "ds_uri": "<http://MyFirstWebThing.com/Action1/DataSchema/output>",
                "fs_uri": "<http://www.wikipedia.it>",
                "fs_types": "wot:ResourceURI, "+wot_FieldSchema}).post()
        ds3 = DataSchema(self.engine, 
            { "ds_uri": "<http://MyFirstWebThing.com/Action2/DataSchema/output>",
            "fs_uri": xsd_integer,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds4 = DataSchema(self.engine, 
            { "ds_uri": "<http://MyFirstWebThing.com/Event1/DataSchema/output>",
            "fs_uri": xsd_dateTimeStamp,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds5 = DataSchema(self.engine, 
            { "ds_uri": "<http://MyFirstWebThing.com/Property1/DataSchema/property>",
            "fs_uri": xsd_string,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
                            
        thing1_uri = "<http://MyFirstWebThing.com>"

        property1 = Property(self.engine,
            { "td": thing_descriptor,
            "property": "<http://MyFirstWebThing.com/Property1>",
            "newName": "Thing1_Property1",
            "newStability": "1000",
            "newWritability": "true",
            "newDS": ds5.uri,
            "newPD": "<http://MyFirstWebThing.com/Property1/PropertyData>",
            "newValue": "Hello World!"})

        action1 = Action(self.engine,
            {"thing": thing1_uri,
            "td": thing_descriptor,
            "action": "<http://MyFirstWebThing.com/Action1>",
            "newName": "Thing1_Action1",
            "ids": ds1.uri,
            "ods": ds2.uri},
            lambda: print("ACTION 1 HANDLER RUN"))

        action2 = Action(self.engine,
            {"thing": thing1_uri,
            "td": thing_descriptor,
            "action": "<http://MyFirstWebThing.com/Action2>",
            "newName": "Thing1_Action2",
            "ods": ds3.uri},
            lambda: print("ACTION 2 HANDLER RUN"),
            forProperties=[property1])

        event1 = Event(self.engine,
            { "td": thing_descriptor,
            "event": "<http://MyFirstWebThing.com/Event1>",
            "eName": "Thing1_Event1",
            "ods": ds4.uri})
        
        thing1 = Thing(self.engine,
            { "thing": thing1_uri,
            "newName": "Thing1",
            "newTD": thing_descriptor }).post(interaction_patterns=[property1,action1,action2,event1])
        
        self.assertTrue(compare_queries(self.engine.query_all(),
                                        query_all_sparql,
                                        show_diff=True))
        
    def test_1(self):
        """
        This test checks if the sparql insert of Thing2 and the sum of 
        cocktail sparqls have the same effect in the rdf store.
        """
        thing_descriptor = "<http://MySecondWebThingDescription.com>"
        self.engine.sap.update_namespaces("foaf","http://xmlns.com/foaf/0.1/")
        self.engine.sparql_update(read_all_file("insert_thing_2.sparql"))
        query_all_sparql = self.engine.query_all()
        self.engine.clear()
        
        ds1 = DataSchema( self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Action1/DataSchema/input>",
            "fs_uri": "foaf:",
            "fs_types": "wot:OntologyURI, "+wot_FieldSchema}).post()
        ds2 = DataSchema(self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Action1/DataSchema/output>",
            "fs_uri": xsd_string,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds3 = DataSchema(self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Event1/DataSchema/output>",
            "fs_uri": xsd_integer,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds4 = DataSchema(self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Event2/DataSchema/output>",
            "fs_uri": "<http://www.google.it>",
            "fs_types": "wot:ResourceURI, "+wot_FieldSchema}).post()
        ds5 = DataSchema(self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Property1/DataSchema/property>",
            "fs_uri": xsd_literal,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
        ds6 = DataSchema(self.engine, 
            { "ds_uri": "<http://MySecondWebThing.com/Property2/DataSchema/property>",
            "fs_uri": xsd_literal,
            "fs_types": xsd_+", "+wot_FieldSchema}).post()
                            
        thing1 = Thing(self.engine,
            { "thing": "<http://MySecondWebThing.com>",
            "newName": "Thing2",
            "newTD": thing_descriptor }).post()
        
        property1 = Property(self.engine,
            { "td": thing_descriptor,
            "property": "<http://MySecondWebThing.com/Property1>",
            "newName": "Thing2_Property1",
            "newStability": "0",
            "newWritability": "false",
            "newDS": ds5.uri,
            "newPD": "<http://MySecondWebThing.com/Property1/PropertyData>",
            "newValue": '{"json":"content"}'}).post()
        
        property2 = Property(self.engine,
            { "td": thing_descriptor,
            "property": "<http://MySecondWebThing.com/Property2>",
            "newName": "Thing2_Property2",
            "newStability": "75",
            "newWritability": "true",
            "newDS": ds6.uri,
            "newPD": "<http://MySecondWebThing.com/Property2/PropertyData>",
            "newValue": "Whatever kind of binary content"}).post()
        
        action1 = Action(self.engine,
            { "thing": thing1.uri,
            "td": thing_descriptor,
            "action": "<http://MySecondWebThing.com/Action1>",
            "newName": "Thing2_Action1",
            "ids": ds1.uri,
            "ods": ds2.uri},
            lambda: print("ACTION 1 HANDLER RUN"),
            forProperties=[property1,property2]).post()
        
        event1 = Event(self.engine,
            { "td": thing_descriptor,
            "event": "<http://MySecondWebThing.com/Event1>",
            "eName": "Thing2_Event1",
            "ods": ds3.uri},
            forProperties=[property2]).post()
              
        event2 = Event(self.engine,
            { "td": thing_descriptor,
            "event": "<http://MySecondWebThing.com/Event2>",
            "eName": "Thing2_Event2",
            "ods": ds4.uri}).post()
        
        query_all_cocktail = self.engine.query_all()
        self.assertTrue(compare_queries(query_all_cocktail,query_all_sparql,show_diff=True))
        
    def test_2(self):
        """
        This test checks if the sparql insert of Thing3 and the sum of cocktail sparqls 
        have the same effect in the rdf store.
        """
        thing_descriptor = "<http://MyThirdWebThingDescription.com>"
        self.engine.sparql_update(read_all_file("insert_thing_3.sparql"))
        query_all_sparql = self.engine.query_all()
        self.engine.clear()

        thing1 = Thing(self.engine,
            { "thing": "<http://MyThirdWebThing.com>",
            "newName": "Thing3",
            "newTD": thing_descriptor }).post()
                        
        action1 = Action(self.engine,
            { "thing": thing1.uri,
            "td": thing_descriptor,
            "action": "<http://MyThirdWebThing.com/Action1>",
            "newName": "Thing3_Action1"},
            lambda: print("ACTION 1 HANDLER RUN")).post()
                                
        event1 = Event(self.engine,
            { "td": thing_descriptor,
            "event": "<http://MyThirdWebThing.com/Event1>",
            "eName": "Thing3_Event1"}).post()

        query_all_cocktail = self.engine.query_all()
        self.assertTrue(compare_queries(query_all_cocktail,query_all_sparql,show_diff=True))

if __name__ == '__main__':
    unittest.main(failfast=True)
