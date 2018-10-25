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

import sys
import argparse

def main(args):
    sap_file = generate_cocktail_sap(None)
    ysap = SAPObject(yaml.load(sap_file))
    engine = SEPA(sapObject=self.ysap,logLevel=logging.INFO)
    
    engine.query_all(destination=resource_filename(__name__,"res_query_all.json"))
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
