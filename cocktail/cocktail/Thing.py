#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  Thing.py
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

from rdflib import Graph, Literal, BNode, URIRef
from sepy.tablaze import tablify
from io import TextIOBase

import logging


logger = logging.getLogger("cocktail_log")


def graphNodeBuilder(binding):
    if binding["type"] == "uri":
        return URIRef(binding["value"])
    elif binding["type"] == "literal":
        return Literal(binding["value"])
    return BNode()
    

class Thing:
    """
    wot:Thing python implementation
    """
    def __init__(self, sepa, bindings, superthing=None):
        """
        Constructor of Thing Item.
        'sepa' is the blazegraph/sepa instance.
        'bindings' is a dictionary formatted as required by the new-action yaml
        'superthing' is the uri of the superthing that may be required
        """
        self._bindings = bindings
        self._sepa = sepa
        self._superthing = superthing
        
    def post(self, interaction_patterns=[]):
        """
        Posting the wot:Thing (and its connection to a superthing) with
        all its interaction patterns. Note that putting interaction patterns
        here is *not* the only way to proceed.
        """
        self._sepa.update("NEW_THING", forcedBindings=self._bindings)
        logger.debug("Posting thing {}: {}".format(self.name, self.uri))
        
        if self._superthing is not None:
            self._sepa.update("NEW_SUBTHING",
                              forcedBindings={"superthing": self._superthing,
                                              "subthing": self.uri})
            logger.debug("Connecting superthing {} to {}".format(self._superthing, self.uri))
        for ip in interaction_patterns:
            logger.debug("Appending interaction pattern {} to {}".format(ip.uri, self.uri))
            ip.post()
        return self
            
    def delete(self):
        """Deletes the thing from the rdf store"""
        self._sepa.update("DELETE_THING", self._bindings)
        logger.debug("Deleting "+self.uri)
        
    @staticmethod
    def discover(sepa, bindings={}, nice_output=False):
        """
        Thing discovery. It can be more selective when we use 'bindings',
        while 'nice_output' prints the results to console in a friendly
        manner.
        """
        d_output = sepa.query("DISCOVER_THINGS", bindings)
        if nice_output:
            tablify(d_output, prefix_file=sepa.sap.get_namespaces(stringList=True))
        return d_output
        
    @property
    def bindings(self):
        return self._bindings
        
    @property
    def uri(self):
        return self._bindings["thing"]
        
    @property
    def name(self):
        return self._bindings["newName"]
        
    @property
    def td(self):
        return self._bindings["newTD"]
        
    @property
    def superthing(self):
        return self._superthing
    
    @classmethod
    def getBindingList(self):
        """
        Utility function to know how you have to format the bindings for
        the constructor.
        """
        return self._sepa.sap.updates["NEW_THING"]["forcedBindings"].keys()
        
    def jsonLDexport(self, destination):
        """
        Method to export the current WebThing object descriptor in a JSON-LD
        format into the file pointed to by 'destination'.
        Wraps the static method Thing.toJsonLD().
        """
        Thing.toJsonLD(self._sepa, self.uri, destination=destination)
    
    @staticmethod
    def toJsonLD(sepa, thingURI, destination=None, nice_output=False):
        """
        Static method that exports the descriptor of a WebThing having URI
        'thingURI' in a JSON-LD file pointed to by 'destination', if available.
        The output can be also seen as table on stdout, if 'nice_output' is True.
        """
        result = sepa.query(
            "JSONLD_CONSTRUCT", forcedBindings={"thing": thingURI},
            destination=destination)
        
        if nice_output:
            tablify(result, prefix_file=sepa.sap.get_namespaces(stringList=True))
        
        thingGraph = Graph()
        for binding in result["results"]["bindings"]:
            # subject
            s = graphNodeBuilder(binding["subject"])
            # predicate
            p = graphNodeBuilder(binding["predicate"])
            # object
            o = graphNodeBuilder(binding["object"])
            thingGraph.add((s, p, o))
        
        jld_result = thingGraph.serialize(format="json-ld").decode("utf-8")
        if destination is not None:
            try:
                if isinstance(destination, TextIOBase):
                    print(jld_result, file=destination)
                else:
                    with open(destination, "w") as jld_output:
                        print(jld_result, file=jld_output)
            except Exception as e:
                logger.error("Unable to export json-ld file: {}".format(e))
        
        return jld_result
