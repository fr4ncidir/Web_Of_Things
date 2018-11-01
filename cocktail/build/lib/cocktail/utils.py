#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
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

from sepy.SAPObject import generate, defaultdict_to_dict, YsapTemplate
from sepy.tablaze import tablify
from os import listdir
from os.path import splitext, isfile, split
from pkg_resources import resource_filename
from collections import defaultdict

import logging
import yaml
import json

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)
logger = logging.getLogger("cocktailLogger")

COCKTAIL_NAMESPACES = { "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "owl": "http://www.w3.org/2002/07/owl#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "dul": "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#",
                        "wot": "http://wot.arces.unibo.it/ontology/web_of_things#"}
    
def sparqlFolderToSap(queryfolder,file_filter=None):
    """
    This function explores 'queryfolder' for .sparql files, loads them as
    yaml dictionaries, and returns the full dictionary.
    By defining the 'file_filter' parameter, you can get as output a specific
    file of the 'queryfolder', instead of the entire content.
    """
    sapDict = {}
    for item in listdir(queryfolder):
        if (file_filter == item) or (file_filter is None):
            filepath = queryfolder+"/"+item
            if (isfile(filepath) and (splitext(item)[1] == ".sparql")):
                with open(filepath,"r") as csa:
                    y = yaml.load(csa)
                sapDict.update(y)
            if file_filter == item:
                break
    return sapDict

def generate_cocktail_sap(destination,jinjaTemplate=YsapTemplate):
    nested_dict = lambda: defaultdict(nested_dict)
    
    sparql11 = nested_dict()
    sparql11["protocol"] = "http"
    sparql11["port"] = 8000
    sparql11["query"]["path"] = "/query"
    sparql11["query"]["method"] = "POST"
    sparql11["query"]["format"] = "JSON"
    sparql11["update"]["path"] = "/update"
    sparql11["update"]["method"] = "POST"
    sparql11["update"]["format"] = "JSON"
    
    sparql11se = nested_dict()
    sparql11se["protocol"] = "ws"
    sparql11se["availableProtocols"]["ws"]["port"] = 9000
    sparql11se["availableProtocols"]["ws"]["path"] = "/subscribe"
    sparql11se["availableProtocols"]["wss"]["port"] = 9443
    sparql11se["availableProtocols"]["wss"]["path"] = "/secure/subscribe"
    sparql11se = defaultdict_to_dict(sparql11se)
    
    queries = sparqlFolderToSap(resource_filename(__name__, "queries"))
    queries.update(sparqlFolderToSap(resource_filename(__name__, "subscribes")))
    
    updates = sparqlFolderToSap(resource_filename(__name__, "updates"))
    updates.update(sparqlFolderToSap(resource_filename(__name__, "deletes")))
    
    if destination is not None:
        logger.info("Writing sap file to {}: please customize it from there".format(destination))
    return generate(jinjaTemplate,
                    "localhost",
                    sparql11,
                    sparql11se,
                    queries=queries,
                    updates=updates,
                    namespaces=COCKTAIL_NAMESPACES,
                    destination_file=destination)

def forPropertySparqlBuilder(sap,ip,properties):
    sparql = sap.getSparql(sap.updates,"ADD_FORPROPERTY",forcedBindings={"ip":ip},bindingCheck=False)
    pFirstBind = [ p.bindings["property"] for p in properties ]
    pSecondBind = [ "{} a wot:Property".format(p) for p in pFirstBind ]
    sparql = sparql.replace("?property", ", ".join(pFirstBind), 1)
    sparql = sparql.replace("?property a wot:Property",". ".join(pSecondBind))
    return sparql

def cfr_bindings(bA,bB,ignorance):
    """
    bA is a list of bindings
    bB is another list of bindings
    ignorance is a list of keys which you want to ignore in the bindings
    returns True if bindings are equal, False otherwise
    """
    for key in bA:
        if ((not (key in bB)) or ((bA[key]["type"] != bB[key]["type"]) or 
            ((not (key in ignorance)) and (bA[key]["value"] != bB[key]["value"])))):
            return False
    return True

def diff_JsonQuery(jA,jB,ignore_val=[],show_diff=False,log_message=""):
    """
    Compares outputs of query json jA towards jB. You can ignore specific
    bindings values in 'ignore_val'. When 'show_diff' is true, tablaze.py 
    is called for nicer visualization of differences.
    'log_message' can be used for verbose notification.
    Returns True or False as comparison result.
    """
    result = True
    diff = []
    for bindingA in jA["results"]["bindings"]:
        eq_binding = False
        for bindingB in jB["results"]["bindings"]:
            eq_binding = cfr_bindings(bindingA,bindingB,ignore_val)
            if eq_binding:
                break
        if not eq_binding:
            diff.append(bindingA)
            result = False
    if show_diff and len(diff)>0: 
        jdiff=json.loads('{}')
        jdiff["head"]={"vars": jA["head"]["vars"]}
        jdiff["results"]={"bindings": diff}
        logger.info("{} Differences".format(log_message))
        print(tablify(jdiff))
    return result
    
# def compare_query_to_json(sepa,query_file_path,json_expected_result):
    # path,fileName = split(query_file_path)
    # sapDict = sparqlFolderToSap(path,file_filter=fileName)
    # sapKey = list(sapDict.keys())[0]
    # query_result = sepa.query(sapKey)
    # return compare_queries(query_result,json_expected_result,show_diff=True)

def compare_queries(i_jA,i_jB,show_diff=False,ignore_val=[]):
    """
    This function compares two json outputs of a SPARQL query.
    jA, jB params are the two json objects containing the results of the query.
    They may also be paths to json files.
    show_diff param, usually false, when set to true will show the entries that
    A has, but not B;
    B has, but not A.
    A boolean is returned, to notify whether jA==jB or not.
    You can ignore the binding value by specifying its name in the ignore_val list. 
    Ignoring the value means that the binding must be there, but that you don't care about its
    actual value.
    """
    # Dealing with paths vs json objects as arguments
    if isinstance(i_jA,str) and isfile(i_jA):
        with open(i_jA,"r") as fA:
            jA = json.load(fA)
    elif isinstance(i_jA,dict):
        jA = i_jA
    else:
        jA = json.loads(i_jA)
    if isinstance(i_jB,str) and isfile(str(i_jB)):
        with open(i_jB,"r") as fB:
            jB = json.load(fB)
    elif isinstance(i_jB,dict):
        jB = i_jB
    else:
        jB = json.loads(i_jB)
        
    # Checking if every variable in jA is also present in jB and vice versa
    setVarA = set(jA["head"]["vars"])
    setVarB = set(jB["head"]["vars"])
    if setVarA != setVarB:
        for item in (setVarA-setVarB):
            logging.error("A->B Variable '{}'  not found!".format(item))
        for item in (setVarB-setVarA):
            logging.error("B->A Variable '{}'  not found!".format(item))
        return False
            
    # A->B
    # Check if every binding in A exists also in B
    result = diff_JsonQuery(jA,jB,show_diff=show_diff,ignore_val=ignore_val,log_message="A->B")
    # B->A
    result = result and diff_JsonQuery(jB,jA,show_diff=show_diff,ignore_val=ignore_val,log_message="B->A")
    return result