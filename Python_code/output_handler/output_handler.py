# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 17:17:59 2020

@author: ken
"""

import json
import pandas as pd
import os

import matplotlib.pyplot as plt

from display.multi_panel import multi_panel_from_flat_data


class output_handler():
    ### Class for handling simulation output ###
    
    def __init__(self, output_handler_file_string,
                 sim_data):
        
        # Check for file
        if (output_handler_file_string==[]):
            print('No output handler file specified. Cannot write output')
            return
        
        # Load the structure as a dict
        with open(output_handler_file_string,'r') as f:
            self.oh_data = json.load(f)
            
        # Write sim_data to file
        if ('simulation_output_file_string' in self.oh_data.keys()):
            output_file_string = self.oh_data['simulation_output_file_string']
            if not os.path.isabs(output_file_string):
                data_file_string = os.path.join(os.getcwd(),
                                                output_file_string)
            ext = data_file_string.split('.')[-1]
            print('Writing sim_data to %s' % output_file_string)
            if (ext=='xlsx'):
                sim_data.to_excel(output_file_string, index=False)
            else:
                sim_data.to_csv(output_file_string)
                
        # Write summary image file
        if ('summary_image_file_string' in self.oh_data.keys()):
            # Deduce the output file string
            output_file_string = self.oh_data['summary_image_file_string']
            if not os.path.isabs(output_file_string):
                output_file_string = os.path.join(os.getcwd(),
                                                output_file_string)
                           
            # Now deduce the template file string
            this_dir = os.path.dirname(os.path.realpath(__file__))
            template_file_string = os.path.join(
                this_dir,'templates/summary_template.json')
            
            self.create_image_from_template(
                        sim_data,
                        template_file_string = template_file_string,
                        output_image_file_string = output_file_string)
            
        # User defined files
        if ('user_defined_images' in self.oh_data):
            user_defined = self.oh_data['user_defined_images']['user_defined']
            for ud in user_defined:
                self.create_image_from_template(
                    sim_data,
                    ud['template_file_string'],
                    ud['output_file_string'])

            
    def create_image_from_template(self,
                                   sim_data,
                                   template_file_string,
                                   output_image_file_string):
        
        if not os.path.isabs(template_file_string):
            template_file_string = os.path.join(os.getcwd(),
                                                template_file_string)
        if not os.path.isabs(output_image_file_string):
            output_image_file_string = os.path.join(os.getcwd(),
                                                    output_image_file_string)
        fig,ax = multi_panel_from_flat_data(
                        pandas_data = sim_data,
                        template_file_string = template_file_string,
                        output_image_file_string = output_image_file_string)
        
        plt.close(fig)
            