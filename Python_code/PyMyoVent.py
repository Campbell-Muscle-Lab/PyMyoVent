# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import sys

from modules.SingleVentricle.driver import return_sim_struct_from_xml_file, \
    run_simulation_from_xml_file
from modules.SingleVentricle.SingleVentricle import single_circulation as sc

if __name__ == "__main__":

    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    # Switch depending on number of arguments
    if (no_of_arguments == 1):
        print('PyMyoVent called with no inputs')
    
    if (no_of_arguments == 2):
        if (sys.argv[1] == 'run_default_model'):
            print('Running default model')
            run_simulation_from_xml_file('..\demo_files\demo_1\demo_1_model.xml')
