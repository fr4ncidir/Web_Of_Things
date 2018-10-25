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
from cocktail import __name__ as cName

import sys
import argparse
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)
logger = logging.getLogger("cocktailLogger")

def setUp(engine):
    engine.clear()
    engine.sparql_update(read_all_file("insert_thing_1.sparql"))
    engine.sparql_update(read_all_file("insert_thing_2.sparql"))
    engine.sparql_update(read_all_file("insert_thing_3.sparql"))

def main(args):
    logger.info("Setting up SAP objects and SEPA engine object...")
    sap_file = generate_cocktail_sap(None)
    ysap = SAPObject(yaml.load(sap_file))
    engine = SEPA(sapObject=self.ysap,logLevel=logging.INFO)
    
    logger.info("Setting up initial knowledge base...")
    setUp(engine)
    
    target = resource_filename(__name__,"res_query_all.json")
    logger.info("Rebuilding {}".format(target))
    engine.query_all(destination=target)
    
    dir_path = resource_filename(cName,"queries")
    for fileName in listdir(dir_path):
        filePath = dir_path + "/" + fileName
        if (isfile(filePath) and (splitext(filePath)[1] == ".sparql")):
            sapKey = list(sparqlFolderToSap(dir_path,file_filter=fileName).keys())[0]
            target = resource_filename(__name__,splitext("res_"+fileName)[0]+".json")
            logger.info("Rebuilding {}".format(target))
            self.engine.query(sapKey,destination=target)
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
