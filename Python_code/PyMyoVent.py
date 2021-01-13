# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import sys
import json

from single_ventricle_circulation import single_ventricle_circulation as svc


def PyMyoVent_main():
    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    # Switch depending on number of arguments
    if (no_of_arguments == 3):
        # Demos
        if (sys.argv[1] == 'demo'):
            if (sys.argv[2] == '3state_with_SRX_base'):
                run_batch('../demo_files/3state_with_SRX_base/batch.json')

        if (sys.argv[1] == 'run_batch'):
            run_batch(sys.argv[2])


def run_batch(batch_json_file_string):
    if (batch_json_file_string == []):
        print('No batch file specified. Exiting')
        return

    with open(batch_json_file_string, 'r') as bf:
        batch_data = json.load(bf)
        jobs = batch_data['job']
        for job in jobs:
            if ('sim_options_file_string' in job):
                sim_options_file_string = job['sim_options_file_string']
            else:
                sim_options_file_string = []
            svc_object = svc.single_ventricle_circulation(
                job['model_file_string'])
            svc_object.run_simulation(
                protocol_file_string=job['protocol_file_string'],
                output_handler_file_string=job['output_handler_file_string'],
                sim_options_file_string=sim_options_file_string)

if __name__ == "__main__":
    PyMyoVent_main()
