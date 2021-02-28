# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:04:38 2019

@author: kscamp3
"""

import os
import sys
import json

import multiprocessing

from pathlib import Path

from single_ventricle_circulation import single_ventricle_circulation as svc
from output_handler import output_handler as oh
from display.display import create_summary


def PyMyoVent_main():
    # Get the number of arguments
    no_of_arguments = len(sys.argv)

    # Switch depending on number of arguments
    if (no_of_arguments == 3):
        # Demos
        if (sys.argv[1] == 'demo'):
            if (sys.argv[2] == '3state_with_SRX_base'):
                run_batch('../demo_files/3state_with_SRX_base/batch.json')
            if (sys.argv[2] == '3state_with_SRX_growth'):
                run_batch('../demo_files/3state_with_SRX_growth/batch.json')

            elif (sys.argv[2] == 'test'):
                run_batch('../demo_files/test/batch.json')

        if (sys.argv[1] == 'run_batch'):
            run_batch(sys.argv[2])

    if (no_of_arguments == 4):
        if (sys.argv[1] == 'create_figures'):
            oh.output_handler(sys.argv[2],
                              sim_results_file_string=sys.argv[3])

        if (sys.argv[1] == 'create_summary'):
            create_summary(sys.argv[2],
                           output_file_string=sys.argv[3])


def run_batch(batch_json_file_string):
    if (batch_json_file_string == []):
        print('No batch file specified. Exiting')
        return

    # Create thread_jobs to hold job information that
    # will be passed to worker thread
    thread_jobs = []

    with open(batch_json_file_string, 'r') as bf:
        batch_data = json.load(bf)
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
            thread_jobs.append(job)

    # Now that we have parsed the job data, run the batch
    # using multiprocessing and all cores but 1
    num_processes = multiprocessing.cpu_count()
    print("num_processes: %i" % num_processes)

    pool = multiprocessing.Pool(processes=(num_processes-1))
    for i in range(len(thread_jobs)):
        pool.apply_async(worker, args=(thread_jobs[i], i))
    pool.close()
    pool.join()


def worker(job, thread_id=[]):
    """ Runs a job in a batch """

    svc_object = svc.single_ventricle_circulation(
        job['model_file_string'], thread_id)
    svc_object.run_simulation(
        protocol_file_string=job['protocol_file_string'],
        output_handler_file_string=job['output_handler_file_string'],
        sim_options_file_string=job['sim_options_file_string'],
        sim_results_file_string=job['sim_results_file_string'])


if __name__ == "__main__":
    PyMyoVent_main()
