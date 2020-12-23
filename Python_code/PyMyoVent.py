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
        
    if (no_of_arguments == 2):
        import output_handler.output_handler as oh
        import pandas as pd
        sim_data = pd.read_csv('C:/ken/GitHub/CampbellMuscleLab/models/PyMyoVent/temp/output_ken.csv')
        oh.output_handler('c:/ken/github/campbellmusclelab/models/pymyovent/demo_files/ken/output_handler_image_only.json',
                          sim_data)

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
