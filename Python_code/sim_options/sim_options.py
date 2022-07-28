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
            
            if (so['rates_dump']['relative_to'] == 'this_file'):
                base_dir = Path(sim_options_file_string).parent.absolute()
                self.data['rates_file_string'] = os.path.join(
                    base_dir, self.data['rates_file_string'])


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
        
        
