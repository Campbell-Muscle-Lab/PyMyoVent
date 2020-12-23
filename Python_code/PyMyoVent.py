    # -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import sys
import json

from single_ventricle_circulation import single_ventricle_circulation as svc

def PyMyoVent():
    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    # Switch depending on number of arguments
    if (no_of_arguments == 1):
        run_batch('c:/ken/github/campbellmusclelab/models/pymyovent/demo_files/ken/batch.json')

def run_batch(batch_json_file_string):
    
    if (batch_json_file_string==[]):
        print('No batch file specified. Exiting')
        return
    
    with open(batch_json_file_string,'r') as bf:
        batch_data = json.load(bf)
        jobs = batch_data['PyMyoVent_batch']['job']
        for job in jobs:
            svc_object = svc.single_ventricle_circulation(job['model_file_string'])
            svc_object.run_simulation(
                protocol_file_string = job['protocol_file_string'],
                output_handler_file_string = job['output_handler_file_string'])

if __name__ == "__main__":
    PyMyoVent()
    

    # if (no_of_arguments == 2):
    #     if (sys.argv[1] == 'run_default_model'):
    #         print('Running default model')

    #         json_file_strings = '..\demo_files\getting_started\getting_started_model.json'

    #         with open(json_file_strings,'r') as f:
    #             json_input_data = json.load(f)

    #         output_temp =\
    #          json_input_data['output_parameters']['input_file'][0]

    #         # Check directory exists and save image file
    #         dir_path = os.path.dirname(output_temp)
    #         if not os.path.isdir(dir_path):
    #             os.makedirs(dir_path)
    #             print('Saving inputs to to %s' % output_temp)

    #         with open(json_file_strings,'r') as f,open(output_temp,'w') as fo:
    #             fo.write(f.read())

    #         sim_object = sc(json_input_data)
    #         sim_object.run_simulation()


    # if (no_of_arguments == 3):
    #     if (sys.argv[1] == 'run_defined_model'):

    #         print('Running model %s' % sys.argv[2])

    #         json_file_strings = sys.argv[2]
    #         with open(json_file_strings,'r') as f:
    #             json_input_data = json.load(f)

    #         output_temp =\
    #          json_input_data['output_parameters']['input_file'][0]

    #         # Check directory exists and save image file
    #         dir_path = os.path.dirname(output_temp)
    #         if not os.path.isdir(dir_path):
    #             os.makedirs(dir_path)
    #             print('Saving inputs to to %s' % output_temp)

    #         with open(json_file_strings,'r') as f,open(output_temp,'w') as fo:
    #             fo.write(f.read())

    #         sim_object = sc(json_input_data)
    #         sim_object.run_simulation()

    #     if (sys.argv[1] == 'run_multi_threads'):
    #         import nested_lookup as nl

    #         print('Running mmodel %s' % sys.argv[2])

    #         json_file_strings = sys.argv[2]
    #         with open(json_file_strings,'r') as f:
    #             json_input_data = json.load(f)

    #         #run_multi_threads(json_input_data)
    #         #return_input_data(json_input_data)
    #         run_multi_processing(json_input_data)

    #     if (sys.argv[1] == 'run_batch_file'):

    #         print('Running model %s' % sys.argv[2])

    #         batch_file_string = sys.argv[2]
    #         with open(batch_file_string,'r') as f:
    #             batch_input_data = json.load(f)

    #         input_path_array = np.array(list(batch_input_data["input_path"].values()))
    #         number_of_data_points = len(input_path_array)

    #         for i in range(number_of_data_points):

    #             json_file_path = input_path_array[i][0]
    #             print(json_file_path)

    #             with open(json_file_path,'r') as f:
    #                 json_data = json.load(f)

    #             output_temp =\
    #                 json_data['output_parameters']['input_file'][0]

    #             # Check directory exists and save image file
    #             dir_path = os.path.dirname(output_temp)
    #             if not os.path.isdir(dir_path):
    #                 os.makedirs(dir_path)
    #                 print('Saving inputs to to %s' % output_temp)

    #             with open(json_file_path,'r') as f,open(output_temp,'w') as fo:
    #                     fo.write(f.read())

    #             sim_object = sc(json_data)
    #             sim_object.run_simulation()
