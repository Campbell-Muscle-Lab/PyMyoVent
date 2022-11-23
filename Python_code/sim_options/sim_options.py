# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 09:43:40 2021

@author: ken
"""

import json
import os

import numpy as np
import pandas as pd

from pathlib import Path

from protocol import protocol as prot

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class sim_options():

    def __init__(self,
                 sim_options_file_string,
                 time_step,
                 parent_circulation):
        """ Constructor for the sim_options object """

        # Store the parent circulation
        self.parent_circulation = parent_circulation

        # Create a dictionary to store data
        self.data = dict()

        # Store the time-step
        self.data['time_step'] = time_step

        with open(sim_options_file_string, 'r') as f:
            so = json.load(f)

        if ('cross_bridge_dump' in so):
            cbd = so['cross_bridge_dump']
            self.data['cb_dump_file_string'] = \
                cbd['file_string']
            self.data['cb_dump_t_start_s'] = cbd['t_start_s']
            self.data['cb_dump_t_stop_s'] = cbd['t_stop_s']
            self.data['cb_dump_t_start_ind'] = \
                int(self.data['cb_dump_t_start_s'] /
                    time_step)
            self.data['cb_dump_t_stop_ind'] = \
                int(self.data['cb_dump_t_stop_s'] /
                    time_step)

            # Open the dump file and write the header

            # First check if the directory exists
            dir_path = os.path.dirname(self.data['cb_dump_file_string'])
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            self.cb_dump_file = open(
                self.data['cb_dump_file_string'], 'w')
            self.cb_dump_file.write('Time_s\t')
            # Header depends on model
            if (self.parent_circulation.hs.myof.implementation['kinetic_scheme'] ==
                    '3_state_with_SRX'):
                r = 1
            else:
                r = 2
            for j in range(0, r):
                for i, x in enumerate(
                        self.parent_circulation.hs.myof.x):
                    self.cb_dump_file.write('x%i_%.1f' % ((j+1), x))
                    if ((j == (r - 1)) and
                        (i == (np.size(self.parent_circulation.hs.myof.x) - 1))):
                        self.cb_dump_file.write('\n')
                    else:
                        self.cb_dump_file.write('\t')
            self.cb_dump_file.close()

        # Check for burst mode
        if ('burst_output' in so):
            bo = so['burst_output']
            self.data['complete_span_s'] = bo['complete_span_s']
            self.data['complete_repeat_s'] = bo['complete_repeat_s']
            self.data['envelope_span_s'] = bo['envelope_span_s']

            # Deduce number of entries in data record
            t = 0
            n = 0
            for i in np.arange(
                    self.parent_circulation.prot.data['no_of_time_steps']):
                t = t + time_step
                (s, write_mode) = self.return_save_status(t)
                if (s != 0):
                    n = n + s
            # Set the number of points in the main sim output
            self.data['n_burst_points'] = int(n)
            # Set the number of points in the rolling window for
            # the envelope data
            self.data['n_envelope_points'] = int(
                self.data['envelope_span_s'] / time_step)
            print('Max sim time (s): %f' % t)
            print('Output points: %i' % self.data['n_burst_points'])
            print('Envelope_points: %i' % self.data['n_envelope_points'])
        else:
            print('Full dump mode, writing %i time-points' %
                  self.parent_circulation.prot.data['no_of_time_steps'])
            
        # Check for period_save
        if ('periodic_save' in so):
            self.data['periodic_save_interval_s'] = \
                so['periodic_save']['save_interval_s']
                
        # Check for rates_dump
        if ('rates_dump' in so):
            self.data['rates_file_string'] = so['rates_dump']['file_string']
            
            if ('output_image_file' in so['rates_dump']):
                self.data['rates_image_file'] = \
                    so['rates_dump']['output_image_file']
                self.data['rates_image_formats'] = \
                    so['rates_dump']['output_image_formats']            
            
            if (so['rates_dump']['relative_to'] == 'this_file'):
                base_dir = Path(sim_options_file_string).parent.absolute()
                self.data['rates_file_string'] = os.path.join(
                    base_dir, self.data['rates_file_string'])
                self.data['rates_image_file'] = os.path.join(
                    base_dir, self.data['rates_image_file'])

        # Check for pas stress dump
        if ('pas_stress_dump' in so):
            self.data['pas_stress_file_string'] = so['pas_stress_dump']['file_string']
            
            if ('output_image_file' in so['pas_stress_dump']):
                self.data['pas_stress_image_file'] = \
                    so['pas_stress_dump']['output_image_file']
                self.data['pas_stress_image_formats'] = \
                    so['pas_stress_dump']['output_image_formats']
            
            if (so['pas_stress_dump']['relative_to'] == 'this_file'):
                base_dir = Path(sim_options_file_string).parent.absolute()
                self.data['pas_stress_file_string'] = os.path.join(
                    base_dir, self.data['pas_stress_file_string'])
                self.data['pas_stress_image_file'] = os.path.join(
                    base_dir, self.data['pas_stress_image_file'])


    def return_save_status(self, t):
        """ Given a time in s, return 1 for full save, 2 for envelope save
            and 0 for don't save """

        t_remain = t % self.data['complete_repeat_s']
        if (t_remain < self.data['complete_span_s']):
            return (1, 'complete')
        else:
            if ((t_remain % self.data['envelope_span_s']) <
                    self.data['time_step']):
                return (2, 'envelope')
            else:
                return (0, 'none')

    def append_cb_distribution(self, sim_time):
        """ Appends cb distribution to file """

        # Pull off cb distribution
        m = self.parent_circulation.hs.myof

        if (self.parent_circulation.hs.myof.implementation['kinetic_scheme'] ==
                    '3_state_with_SRX'):
            cb_distribution = m.y[2 + np.arange(m.no_of_x_bins)]
        if (self.parent_circulation.hs.myof.implementation['kinetic_scheme'] ==
                    '4_state_with_SRX'):
            cb_distribution = m.y[2 + np.arange(2 * m.no_of_x_bins)]

        self.cb_dump_file = open(
            self.data['cb_dump_file_string'], 'a')

        self.cb_dump_file.write('%.4f\t' % sim_time)
        for i, y in enumerate(cb_distribution):
            self.cb_dump_file.write('%.4f' % y)
            if (i == (np.size(cb_distribution)-1)):
                self.cb_dump_file.write('\n')
            else:
                self.cb_dump_file.write('\t')
        self.cb_dump_file.close()
        
    def dump_rates_file(self):
        """ Dumps rate file """
        
        r = self.parent_circulation.hs.myof.return_rates()
        
        # Write rate structure as a pandas dataframe
        d = pd.DataFrame.from_dict(r)
        d['x'] = self.parent_circulation.hs.myof.x
        # Move x to the front
        cols = list(d)
        cols.insert(0, cols.pop(cols.index('x')))
        d = d.loc[:,cols]
        
        # Dump to file
        print('Writing rates to: %s' % self.data['rates_file_string'])
        d.to_csv(self.data['rates_file_string'], sep='\t',
                 index=False,
                 float_format='%g')
        
        if ('rates_image_file' in self.data):
            # Make a figure
            fig = plt.figure(constrained_layout=False)
            fig.set_size_inches([3.5, 6])
            ax = []
            n_rows = round((len(cols)-1) / 2)
            n_cols = 1
            spec = gridspec.GridSpec(nrows=n_rows,
                                     ncols=n_cols,
                                     figure=fig)
            
            c = 0
            for r in range(n_rows):
                ax.append(fig.add_subplot(spec[r,c]))
                
                for i in range(2):
                    ind = 2*r + i + 1
                    lab_string = 'r_%i' % ind
                    x = d['x'].to_numpy()
                    y = d[lab_string].to_numpy()
                    ax[r].plot(x, np.log10(y), '-', label=lab_string)

                ax[r].set_ylim([-1,4])
                ax[r].set_yticks(np.linspace(-1, 4, 6))                  
                ax[r].legend(loc='lower left')

            for imf in self.data['rates_image_formats']:
                image_file_string = self.data['rates_image_file'] + \
                    '.' + imf
                print('Saving rates figure as %s' % image_file_string)
                fig.savefig(image_file_string)
    
    def dump_pas_stress_file(self, min_rel_vol=0.5, max_rel_vol=3):
        
        base_lv_vol = self.parent_circulation.data['volume_ventricle']
        base_hsl = self.parent_circulation.hs.data['hs_length']
        n_hs = self.parent_circulation.data['n_hs']
        
        v_values = np.linspace(min_rel_vol*base_lv_vol, max_rel_vol*base_lv_vol)
        
        # Set up some arrays
        hs_length = np.NaN * np.ones(len(v_values))
        lv_volume = np.NaN * np.ones(len(v_values))
        lv_pressure = np.NaN * np.ones(len(v_values))
        cpt_int_pas_stress = np.NaN * np.ones(len(v_values))
        cpt_ext_pas_stress = np.NaN * np.ones(len(v_values))
        
        for i, lv_vol in enumerate(v_values):
            
            lv_circum = self.parent_circulation.return_lv_circumference(lv_vol)
            
            lv_volume[i] = lv_vol
            hs_length[i] = lv_circum / n_hs
            lv_pressure[i] = self.parent_circulation.return_lv_pressure(lv_vol)
            
            delta_hsl = (1e9*hs_length[i]) - base_hsl
            d = self.parent_circulation.hs.myof.check_myofilament_stresses(delta_hsl)
            cpt_int_pas_stress[i] = d['int_pas_stress']
            cpt_ext_pas_stress[i] = d['ext_pas_stress']
            
        # Save data as a dict and convert to dataframe
        d = dict()
        d['hs_length'] = 1e9 * hs_length
        d['lv_volume'] = lv_volume
        d['lv_pressure'] = lv_pressure
        d['int_pas_stress'] = cpt_int_pas_stress
        d['ext_pas_stress'] = cpt_ext_pas_stress 
       
        d = pd.DataFrame.from_dict(d)
            
    
    
    # def dump_pas_stress_file(self, min_hsl=750, max_hsl=1200):
    #     """ Dumps passive_stress file """
        
    #     base_hsl = self.parent_circulation.hs.data['hs_length']
        
    #     n_hs = self.parent_circulation.data['n_hs']
        
    #     delta_min_hsl = min_hsl - base_hsl
    #     delta_max_hsl = max_hsl - base_hsl
        
    #     delta_hsl = np.linspace(delta_min_hsl, delta_max_hsl, 25)
        
    #     x = np.NaN * np.ones(len(delta_hsl))
    #     cpt_int_pas_stress = np.NaN * np.ones(len(delta_hsl))
    #     cpt_ext_pas_stress = np.NaN * np.ones(len(delta_hsl))
        
    #     for i, dhsl in enumerate(delta_hsl):
    #         x[i] = base_hsl + dhsl
    #         d = self.parent_circulation.hs.myof.check_myofilament_stresses(dhsl)
    #         cpt_int_pas_stress[i] = d['int_pas_stress']
    #         cpt_ext_pas_stress[i] = d['ext_pas_stress']
        
    #     # Save data as a dict and convert to dataframe
    #     d = dict()
    #     d['hs_length'] = x
    #     d['int_pas_stress'] = cpt_int_pas_stress
    #     d['ext_pas_stress'] = cpt_ext_pas_stress
        
    #     d = pd.DataFrame.from_dict(d)
        
        # Dump to file
        print('Writing pas_stress to: %s' % self.data['pas_stress_file_string'])
        d.to_csv(self.data['pas_stress_file_string'], sep='\t',
                 index=False,
                 float_format='%g')
    
        if ('pas_stress_image_file' in self.data):
            # Make a figure
            fig, (ax1, ax2) = plt.subplots(2,1)
            ax1.plot(d['hs_length'], d['int_pas_stress'], 'bo-',
                    label='Int pas stress')
            ax1.plot(d['hs_length'], d['ext_pas_stress'], 'rs-',
                    label='Ext pas stress')
            
            ax2.plot(d['hs_length'], d['lv_pressure'], 'gd-',
                    label='LV pressure')
            
            ax1.set_ylabel('Passive\nstress\n(N m^{-2})')
            
            ax2.set_xlabel('HS length (nm)')
            ax2.set_ylim([-20, 20])
            ax2.set_ylabel('LV pressure (mmHg)')
            
            
            
            for imf in self.data['pas_stress_image_formats']:
                image_file_string = self.data['pas_stress_image_file'] + \
                    '.' + imf
                print('Saving passive stress figure as %s' % image_file_string)
                fig.savefig(image_file_string)
        