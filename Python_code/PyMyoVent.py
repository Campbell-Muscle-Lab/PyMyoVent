# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import os
import sys
import json
import time

import multiprocessing

from pathlib import Path

from single_ventricle_circulation import single_ventricle_circulation as svc
from output_handler import output_handler as oh


def PyMyoVent_main():
    """ Main entry point for code """
    
    
    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    if (no_of_arguments > 0):
        if (sys.argv[1] == 'run_batch'):
            run_batch(sys.argv[2])

        if (sys.argv[1] == 'create_figures'):
            create_figures(sys.argv[2])


def run_batch(batch_json_file_string):
    """ Run simulations as a batch process """
    if (batch_json_file_string == []):
        print('No batch file specified. Exiting')
        return

    # Start timer
    start = time.time()

    # Create batch_jobs to hold job information that
    # will be passed to worker thread
    batch_jobs = []

    with open(batch_json_file_string, 'r') as bf:
        batch_struct = json.load(bf)
        batch_data = batch_struct['PyMyoVent_batch']

        # Set max_threads if available
        requested_max_threads = float("inf")
        if ('max_threads' in batch_data):
            requested_max_threads = batch_data['max_threads']
        

        jobs = batch_data['job']
        for job in jobs:
            if ('sim_options_file_string' not in job):
                job['sim_options_file_string'] = []

            # Adapt for relative paths
            if ('relative_path' in job):
                if (job['relative_path']):
                    base_directory = \
                        Path(batch_json_file_string).parent.absolute()
                    for k in ['model_file_string', 'protocol_file_string',
                              'output_handler_file_string',
                              'sim_options_file_string',
                              'sim_results_file_string']:
                        if (k == 'sim_options_file_string'):
                            if ('sim_options_file_string' not in job):
                                job['sim_options_file_string'] = []
                            else:
                                job[k] = os.path.join(base_directory, job[k])
                        else:
                            job[k] = os.path.join(base_directory, job[k])

            # Append to thread_jobs
            batch_jobs.append(job)

    # Run jobs using multi-processing if there is more than 1 job
    if (len(batch_jobs) == 1):
        worker(batch_jobs[0], 0)
    else:
        # Set processes to minimum of requested and available
        available_threads = multiprocessing.cpu_count()-1

        num_processes = int(min([requested_max_threads, available_threads]))
        print('Running batch using %i threads' % num_processes)

        pool = multiprocessing.Pool(processes=num_processes)
        for i in range(len(batch_jobs)):
            pool.apply_async(worker, args=(batch_jobs[i], i))
        pool.close()
        pool.join()

    # Finish
    stop = time.time()
    print('Batch run time')
    print(stop-start)

def worker(job, thread_id=[]):
    """ Runs a job in a batch """

    svc_object = svc.single_ventricle_circulation(
        job['model_file_string'], thread_id)

    svc_object.run_simulation(
        protocol_file_string=job['protocol_file_string'],
        output_handler_file_string=job['output_handler_file_string'],
        sim_options_file_string=job['sim_options_file_string'],
        sim_results_file_string=job['sim_results_file_string'])

def check_version(model_file_string):
    """ Checks version saved in model file against this version of
        the code, saved in a file in the source directory """

    # Get code string
    version_file_string = os.path.join(Path(__file__).parent, 'version.json')
    with open(version_file_string, 'r') as f:
        v = json.load(f)
    code_v_string = v['PyMyoVent_code']['version'].split('.')
    code_v = []
    for i in range(len(code_v_string)):
        code_v.append(int(code_v_string[i]))
    
    # Get model version
    with open(model_file_string, 'r') as f:
        model = json.lad(f)
    
    # Now get model version
    model_v_string = model['PyMyoVent']['version'].split('.')
    model_v = []
    for i in range(len(model_v_string)):
        model_v.append(int(model_v_string[i]))
    
    # Now compare
    version_problem = False;
    if (code_v[0] > model_v[0]):
        version_problem = True
    elif (code_v[1] < model_v[1]):
        version_problem = True
    if (version_problem):
        print('PyMyoVent version problem')
        print('Code version %s' % code_v_string)
        print('Model version %s' % model_v_string)
        exit(1)



def create_figures(batch_json_file_string):
    """ Create figures from batch file """

    if (batch_json_file_string == []):
        print('No batch file specified. Exiting')
        return
    
    # Loop through data files and output handlers
    with open(batch_json_file_string, 'r') as bf:
        batch_struct = json.load(bf)
        batch_data = batch_struct['PyMyoVent_batch']
        jobs = batch_data['job']
        for job in jobs:
            if ('output_handler_file_string' in job):
                # Adapt for relative path
                if ('relative_path' in job):
                    if (job['relative_path']):
                        base_directory = Path(batch_json_file_string).parent.absolute();
                        output_handler_file_string = \
                            os.path.join(base_directory, job['output_handler_file_string'])
                        results_file_string = \
                            os.path.join(base_directory, job['sim_results_file_string'])
                            
                oh.output_handler(output_handler_file_string,
                    sim_results_file_string = results_file_string)



if __name__ == "__main__":
    PyMyoVent_main()

