# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import sys
import json
from modules.SingleVentricle.driver import return_sim_struct_from_xml_file, \
    run_simulation_from_xml_file, run_simulation_from_json_file
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

    if (no_of_arguments == 3):
        if (sys.argv[1] == 'run_defined_model'):
#            if (hasattr(sys.argv[2], 'json')):
            print('Running model %s' % sys.argv[2])
#            run_simulation_from_json_file(sys.argv[2])
            json_file_strings = sys.argv[2]
            with open(json_file_strings,'r') as f:
                json_input_data = json.load(f)

            sim_object = sc(json_input_data)
            sim_object.run_simulation()
#            """else:
#                print('Running model %s' % sys.argv[2])
#                run_simulation_from_xml_file(sys.argv[2])"""
