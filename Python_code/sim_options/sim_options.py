# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 09:43:40 2021

@author: ken
"""

import json

import numpy as np


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
            self.cb_dump_file = open(
                self.data['cb_dump_file_string'], 'w')
            self.cb_dump_file.write('Time_s\t')
            for i, x in enumerate(
                    self.parent_circulation.hs.myof.x):
                self.cb_dump_file.write('x%.1f' % x)
                if (i == (np.size(self.parent_circulation.hs.myof.x)-1)):
                    self.cb_dump_file.write('\n')
                else:
                    self.cb_dump_file.write('\t')
            self.cb_dump_file.close()

    def append_cb_distribution(self, sim_time):
        """ Appends cb distribution to file """

        # Pull off cb distribution
        m = self.parent_circulation.hs.myof
        cb_distribution = m.y[2 + np.arange(m.no_of_x_bins)]

        self.cb_dump_file = open(
            self.data['cb_dump_file_string'], 'a')

        self.cb_dump_file.write('%.4f\t' % sim_time)
        for i, y in enumerate(cb_distribution):
            self.cb_dump_file.write('%g' % y)
            if (i == (np.size(cb_distribution)-1)):
                self.cb_dump_file.write('\n')
            else:
                self.cb_dump_file.write('\t')
        self.cb_dump_file.close()
