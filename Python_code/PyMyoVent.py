# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import sys
import os
import json
import numpy as np

#from modules.SingleVentricle.driver import return_sim_struct_from_xml_file, \
#    run_simulation_from_xml_file, run_simulation_from_json_file
from modules.SingleVentricle.SingleVentricle import single_circulation as sc
#from analysis.multi_threads import run_multi_processing
if __name__ == "__main__":

    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    # Switch depending on number of arguments
    if (no_of_arguments == 1):
        print('PyMyoVent called with no inputs')

    if (no_of_arguments == 2):
        if (sys.argv[1] == 'run_default_model'):
            print('Running default model')

            json_file_strings = '..\demo_files\demo_1\demo_1_model.json'

            with open(json_file_strings,'r') as f:
                json_input_data = json.load(f)

            output_temp =\
             json_input_data['output_parameters']['input_file'][0]

            # Check directory exists and save image file
            dir_path = os.path.dirname(output_temp)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
                print('Saving inputs to to %s' % output_temp)

            with open(json_file_strings,'r') as f,open(output_temp,'w') as fo:
                fo.write(f.read())

            sim_object = sc(json_input_data)
            sim_object.run_simulation()


    if (no_of_arguments == 3):
        if (sys.argv[1] == 'run_defined_model'):

            print('Running model %s' % sys.argv[2])

            json_file_strings = sys.argv[2]
            with open(json_file_strings,'r') as f:
                json_input_data = json.load(f)

            output_temp =\
             json_input_data['output_parameters']['input_file'][0]

            # Check directory exists and save image file
            dir_path = os.path.dirname(output_temp)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
                print('Saving inputs to to %s' % output_temp)

            with open(json_file_strings,'r') as f,open(output_temp,'w') as fo:
                fo.write(f.read())

            sim_object = sc(json_input_data)
            sim_object.run_simulation()

        if (sys.argv[1] == 'run_multi_threads'):
            import nested_lookup as nl

            print('Running mmodel %s' % sys.argv[2])

            json_file_strings = sys.argv[2]
            with open(json_file_strings,'r') as f:
                json_input_data = json.load(f)

            #run_multi_threads(json_input_data)
            #return_input_data(json_input_data)
            run_multi_processing(json_input_data)
