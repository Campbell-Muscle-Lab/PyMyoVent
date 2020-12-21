# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 22:31:36 2020

@author: ken
"""

import json
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def create_summary_figure_from_json_template(json_template_file_string='c:/temp/test_layout.json'):
    
    with open(json_template_file_string, 'r') as f:
        template_data = json.load(f)

    results_file_string = template_data['simulation_data']['results_file_string']
    
    sim_data = pd.read_excel(results_file_string, sheet_name='Data')
    
    panel_data = template_data['panels']
    
    # Scan through panels working out how many panel rows to create
    no_of_columns = template_data['layout']['no_of_columns']
    row_counters = np.zeros(no_of_columns, dtype=int)
    
    for i,p_data in enumerate(panel_data):
        # Update row counters
        row_counters[p_data['column']-1] += 1
    
    no_of_rows = np.amax(row_counters)
    
    # Now create figure
    fig = plt.figure(constrained_layout=True)
    fig.set_size_inches([template_data['layout']['fig_width'],
                         template_data['layout']['fig_height']])
    spec = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_columns, figure=fig)

    # Now return to panel data, scan through adding plots as you go
    row_counters = np.zeros(no_of_columns, dtype=int)
    for i,p_data in enumerate(panel_data):
        # Update row counters and add axis
        row_counters[p_data['column']-1] += 1
        c = p_data['column']-1
        r = row_counters[c]-1
        ax = fig.add_subplot(spec[r,c])
        # Cycle through the y_data
        for j,y_d in enumerate(p_data['y_info']['series']):
            if (y_d['style']=='line'):
                sim_data.plot(kind='line', x=p_data['x_field'], y=y_d['field'],
                        ax=ax)
        # Tidy up axes and legends
        ax.set_xlabel(p_data['x_field'])
        ax.set_ylabel(p_data['y_info']['label'])
        if "ticks" in p_data['y_info']:
            ax.set_ylim(p_data['y_info']['ticks'][0], p_data['y_info']['ticks'][-1])
        ax.legend(loc='upper right',fontsize=7)
        
if __name__ == "__main__":
    create_summary_figure_from_json_template()       
    