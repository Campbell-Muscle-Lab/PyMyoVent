# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:55:34 2022

@author: ken
"""

import os

def write_sim_results_to_file(self, sim_results_file_string):
    """ Write sim results to specified file """

    # Save the simulation results to file
    if ('sim_results_file_string'):
        output_file_string = os.path.abspath(sim_results_file_string)
        ext = output_file_string.split('.')[-1]
        # Make sure the path exists
        output_dir = os.path.dirname(output_file_string)
        print('output_dir %s' % output_dir)
        if not os.path.isdir(output_dir):
            print('Making output dir')
            os.makedirs(output_dir)
        print('Writing sim_data to %s' % output_file_string)
        if (ext == 'xlsx'):
            self.sim_data.to_excel(output_file_string,
                                   index=False)
        else:
            self.sim_data.to_csv(output_file_string,
                                 float_format='%g',
                                 sep='\t',
                                 index=False)
