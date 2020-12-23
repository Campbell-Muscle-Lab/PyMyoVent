# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 22:31:36 2020

@author: ken
"""

import json
import pandas as pd
import numpy as np

from scipy.signal import find_peaks

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib import patches as pat
from matplotlib.patches import Polygon, Patch
from matplotlib.collections import PatchCollection

def default_formatting():
    formatting = dict()
    formatting['data_linewidth'] = 1.5
    formatting['fontname'] = 'Arial'
    formatting['axis_linewidth'] = 1.5
    formatting['x_label_fontsize'] = 12
    formatting['x_label_pad'] = 0
    formatting['y_label_rotation'] = 0
    formatting['y_label_fontsize'] = 12
    formatting['y_label_pad'] = 30
    formatting['legend_location'] = 'upper left'
    formatting['legend_bbox_to_anchor'] = [1.05, 1]
    formatting['legend_fontsize'] = 9
    formatting['legend_handlelength'] = 1
    formatting['tick_fontsize'] = 11
    formatting['patch_alpha'] = 0.3
    formatting['max_rows_per_legend'] = 4
    
    return formatting

def default_layout():
    layout = dict()
    layout['fig_width'] = 3.5
    layout['panel_height'] = 1
    layout['top_margin'] = 0.1
    layout['bottom_margin'] = 0.1
    layout['left_margin'] = 0.1
    layout['right_margin'] = 0.1
    layout['grid_wspace'] = 0.1
    layout['grid_hspace'] = 0.1
    
    return layout

def default_processing():
    processing = dict()
    processing['envelope_peak_prominence'] = 0.2
    
    return processing

def multi_panel_from_flat_data(
        data_file_string = [],
        excel_sheet = 'Sheet1',
        pandas_data = [],       
        template_file_string=[],
        output_image_file_string = [],
        dpi = 300):
    
    # Check for template file, make an empty dict if absent
    if (template_file_string):
        with open(template_file_string, 'r') as f:
            template_data = json.load(f)
    else:
        template_data=dict()

    # Pull default formatting, then overwite any values from the template
    formatting = default_formatting()
    if ('formatting' in template_data):
        for entry in template_data['formatting']:
            print(entry)
            formatting[entry] = template_data['formatting'][entry]
    print(formatting)
    
    # Pull default processing
    processing = default_processing()
    if 'processing' in template_data:
        for entry in template_data['processing']:
            processing[entry] = template_data['processing'][entry]

    # Read in the data
    if (not data_file_string==[]):
        file_type = data_file_string.split('.')[-1]
        if file_type == 'xlsx':
            pandas_data = pd.read_excel(data_file_string,
                                        sheet_name=excel_sheet)
        if file_type == 'csv':
            pandas_data = pd.read_csv(data_file_string)
        
    
    # Try to work out x data
    if 'x_display' in template_data:
        x_display = template_data['x_display']
    else:
        x_display = dict()
    # Set plausible values if fields are missing
    if 'global_x_field' not in x_display:
        x_display['global_x_field'] = pandas_data.columns[0]
    if 'global_x_ticks' not in x_display:
        x_lim = (pandas_data[x_display['global_x_field']].iloc[0],
                 pandas_data[x_display['global_x_field']].iloc[-1])
        x_display['global_x_ticks'] = \
            np.asarray(deduce_axis_limits(x_lim, 'autoscaling'))
        x_ticks_defined=False
    else:
        x_ticks_defined=True    
    if 'label' not in x_display:
        x_display['label'] = x_display['global_x_field']
            
    # Try to pull off the panel data and cycle through the panels one by one to
    # get the number of columns
    
    # Check for panels tag. If it doesn't exist
    # make up panel data
    if 'panels' in template_data:
        panel_data = template_data['panels']
    else:
        panel_data=dict()
        panel_data['column'] = 1
        panel_data['y_info'] = dict()
        panel_data['y_info']['label'] = pandas_data.columns[0]
        y_data = dict()
        y_data['field'] = pandas_data.columns[0]
        panel_data['y_info']['series'] = [y_data]
        panel_data = [panel_data]
            
    no_of_columns = 0
    for p_data in panel_data:
        test_column = p_data['column']
        if (test_column > no_of_columns):
            no_of_columns = test_column
    
    # Now scan through panels working out how many panel rows to create
    row_counters = np.zeros(no_of_columns, dtype=int)
    
    for i,p_data in enumerate(panel_data):
        # Update row counters
        row_counters[p_data['column']-1] += 1
    rows_per_column = row_counters
    no_of_rows = np.amax(row_counters)
    no_of_panels = np.sum(rows_per_column)
    ax=[]
    
    # Now you know how many panels, create a figure of the right size
    layout = default_layout()
    if 'layout' in template_data:
        for entry in template_data['layout']:
            layout[entry] = template_data['layout'][entry]
            
    fig_height = layout['top_margin'] + \
                (no_of_rows * layout['panel_height']) + \
                 layout['bottom_margin']
    
    # Now create figure
    fig = plt.figure(constrained_layout=False)
    fig.set_size_inches([layout['fig_width'], fig_height])
    spec = gridspec.GridSpec(nrows=no_of_rows,
                             ncols=no_of_columns,
                             figure=fig,
                             wspace=layout['grid_wspace'],
                             hspace=layout['grid_hspace'])

    # Now return to panel data, scan through adding plots as you go
    row_counters = np.zeros(no_of_columns, dtype=int)
    for i,p_data in enumerate(panel_data):
        
        # Update row counters and add axis
        row_counters[p_data['column']-1] += 1
        c = p_data['column']-1
        r = row_counters[c]-1
        ax.append(fig.add_subplot(spec[r,c]))
        
        legend_symbols = []
        legend_strings = []
        
        # Set up your colors
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        line_counter = 0
        patch_counter = 0
        
        # Cycle through the y_data
        for j,y_d in enumerate(p_data['y_info']['series']):
            # Set the plot style to line if it is missing
            if 'style' not in y_d:
                y_d['style'] = 'line'
            # Fill in a blank label if it is missing
            if 'field_label' not in y_d:
                y_d['field_label'] = []
                
            # Pull off the data
            if 'x_field' not in p_data:
                p_data['x_field'] = x_display['global_x_field']
            if 'x_ticks' not in p_data:
                p_data['x_ticks'] = x_display['global_x_ticks']
            
            x = pandas_data[p_data['x_field']].to_numpy()
            vi = np.nonzero((x >= p_data['x_ticks'][0]) & 
                            (x <= p_data['x_ticks'][-1]))
            x = x[vi]
            y = pandas_data[y_d['field']].to_numpy()[vi]
            
            if 'scaling_factor' in y_d:
                y = y * y_d['scaling_factor']
                
            if 'log_display' in y_d:
                if y_d['log_display']=='on':
                    y = np.log10(y)
            
            # Track min and max y
            if (j==0):
                min_x = x[0]
                max_x = x[0]
                min_y = y[0]
                max_y = y[0]
            min_x = np.amin([min_x, np.amin(x)])
            max_x = np.amax([max_x, np.amax(x)])
            min_y = np.amin([min_y, np.amin(y)])
            max_y = np.amax([max_y, np.amax(y)])
            
            # Plot line depending on style
            if (y_d['style'] == 'line'):
                if 'field_color' in y_d:
                    col = colors[y_d['field_color']]
                else:
                    col = colors[line_counter]
                ax[i].plot(x, y,
                        linewidth = formatting['data_linewidth'],
                        color=col,
                        clip_on=True)
                line_counter +=1
                if y_d['field_label']:
                    legend_symbols.append(
                        Line2D([0], [0],
                               color=ax[i].lines[-1].get_color(),
                               lw=formatting['data_linewidth']))
                    legend_strings.append(y_d['field_label'])
                    
            if (y_d['style'] == 'envelope'):
                # y_top = pd.Series(y).rolling(nn, min_periods=1).max().to_numpy()
                # y_bottom = pd.Series(y).rolling(nn, min_periods=1).min().to_numpy()
                top_ind,_ = find_peaks(y, prominence =
                                       processing['envelope_peak_prominence']*np.amax(y))
                x_top = x[top_ind]
                y_top = y[top_ind]
                bot_ind,_ = find_peaks(-y, prominence = 
                                       processing['envelope_peak_prominence']*np.amax(-y))
                x_bot = x[bot_ind]
                y_bot = y[bot_ind]
                y = np.concatenate((y_top, y_bot[-1:0:-1]))
                x = np.concatenate((x_top, x_bot[-1:0:-1]))
                xy = [x,y]
                xy = np.array(np.array(xy).transpose())
                if 'field_color' in y_d:
                    col = colors[y_d['field_counter']]
                else:
                    col = colors[patch_counter]
                polygon = pat.Polygon(xy, True, clip_on=False,
                                      fc=col,
                                      alpha=formatting['patch_alpha'])
                ax[i].add_patch(polygon)
                
                if y_d['field_label']:
                    legend_symbols.append(
                        Patch(facecolor=col,
                            alpha=formatting['patch_alpha']))
                    legend_strings.append(y_d['field_label'])

                patch_counter = patch_counter+1
                
        # Tidy up axes and legends
        
        # Set x limits
        xlim = (min_x, max_x)
        if x_ticks_defined==False:
            xlim = deduce_axis_limits(xlim,'autoscaled')
        ax[i].set_xlim(xlim)
        ax[i].set_xticks(x_display['global_x_ticks'])
       
        # Set y limits
        if ('ticks' in p_data['y_info']):
            ylim=tuple(p_data['y_info']['ticks'])
        else:
            ylim=(min_y, max_y)
            scaling_type = []
            if ('scaling_type' in p_data['y_info']):
                scaling_type = p_data['y_info']['scaling_type']
            ylim = deduce_axis_limits(ylim, mode_string=scaling_type)
        
        ax[i].set_ylim(ylim)
        ax[i].set_yticks(ylim)
        
        # Update axes, tick font and size
        for a in ['left','bottom']:
            ax[i].spines[a].set_linewidth(formatting['axis_linewidth'])
        ax[i].tick_params('both',
                width = formatting['axis_linewidth'])

        for tick_label in ax[i].get_xticklabels():
            tick_label.set_fontname(formatting['fontname'])
            tick_label.set_fontsize(formatting['tick_fontsize'])
        for tick_label in ax[i].get_yticklabels():
            tick_label.set_fontname(formatting['fontname'])
            tick_label.set_fontsize(formatting['tick_fontsize'])            
       
        # Remove top and right-hand size of box
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['right'].set_visible(False)
       
        # Display x axis if bottom
        if (r==(rows_per_column[c]-1)):
            ax[i].set_xlabel(x_display['label'],
                          labelpad = formatting['x_label_pad'],
                          fontfamily = formatting['fontname'],
                          fontsize = formatting['x_label_fontsize'])
        else:
            ax[i].spines['bottom'].set_visible(False)
            ax[i].tick_params(labelbottom=False, bottom=False)
                
        # Set y label
        ax[i].set_ylabel(p_data['y_info']['label'],
                      loc='center',
                      verticalalignment='center',
                      labelpad = formatting['y_label_pad'],
                      fontfamily = formatting['fontname'],
                      fontsize = formatting['y_label_fontsize'],
                      rotation = formatting['y_label_rotation'])
        
        # Add legend if it exists
        if legend_symbols:
            ax[i].legend(legend_symbols, legend_strings,
                         loc=formatting['legend_location'],
                         handlelength = formatting['legend_handlelength'],
                         bbox_to_anchor=(formatting['legend_bbox_to_anchor'][0],
                                         formatting['legend_bbox_to_anchor'][1]),
                         prop={'family': formatting['fontname'],
                               'size': formatting['legend_fontsize']},
                         ncol = int(np.ceil(len(legend_symbols)/
                                            formatting['max_rows_per_legend'])))
   
    # Tidy overall figure
    # Move plots inside margins
    lhs = layout['left_margin']/layout['fig_width']
    bot = layout['bottom_margin']/fig_height
    wid = (layout['fig_width']-0*layout['left_margin']-layout['right_margin'])/layout['fig_width']
    hei = (fig_height-0*layout['bottom_margin']-layout['top_margin'])/fig_height
    r = [lhs, bot, wid, hei]
    spec.tight_layout(fig, rect=r)

    fig.align_labels()
    
    # Save if required
    if output_image_file_string:
        print('Saving figure to %s' % output_image_file_string)
        fig.savefig(output_image_file_string, dpi=dpi)
        
    return (fig,ax)
    
def deduce_axis_limits(lim, mode_string=[]):
    
    # Start simply
    lim = np.asarray(lim)
    lim[0] = multiple_less_than(lim[0])
    lim[1] = multiple_greater_than(lim[1])
    
    if (mode_string != 'close_fit'):
        if (lim[0]>0):
            lim[0]=0
        else:
            if (lim[1]<0):
                lim[1]=0
              
    return ((lim[0],lim[1]))

def multiple_greater_than(v, multiple=0.2):
    if (v>0):
        n = np.floor(np.log10(v))
        m = multiple*np.power(10,n)
        v = m*np.ceil(v/m)
    if (v<0):
        n = np.floor(np.log10(-v))
        m = multiple*np.power(10,n)
        v = m*np.ceil(v/m)
        
    return v

def multiple_less_than(v, multiple=0.2):
    if (v>0):
        n = np.floor(np.log10(v))
        m = multiple*np.power(10,n)
        v = m*np.floor(v/m)
    if (v<0):
        n = np.floor(np.log10(-v))
        m = multiple*np.power(10,n)
        v = m*np.floor(v/m)
        
    return v
            
if __name__ == "__main__":
    (fig,ax) = multi_panel_from_flat_data()
    plt.close(fig)
    