import os

import pandas as pd
import numpy as np

from output_handler import output_handler as oh

def write_complete_data_to_sim_data(self, index):
    """ Writes full data to data frame """

    # This works but is very slow
    if (True):
        for f in list(self.data.keys()):
            if (f not in ['p', 'v', 's', 'compliance', 'resistance',
                          'inertance', 'f']):
                self.sim_data.at[self.write_counter, f] = self.data[f]
        for f in list(self.hr.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.hr.data[f]
        for f in list(self.hs.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.hs.data[f]
        for f in list(self.hs.memb.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.hs.memb.data[f]
        if (hasattr(self.hs, 'ener')):
            for f in list(self.hs.ener.data.keys()):
                self.sim_data.at[self.write_counter, f] = self.hs.ener.data[f]
        for f in list(self.hs.myof.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.hs.myof.data[f]
        if (self.br):
            for f in list(self.br.data.keys()):
                self.sim_data.at[self.write_counter, f] = self.br.data[f]
        if (self.gr):
            for f in list(self.gr.data.keys()):
                self.sim_data.at[self.write_counter, f] = self.gr.data[f]
        self.sim_data.at[self.write_counter, 'write_mode'] = 1
        self.write_counter = self.write_counter + 1

    if (False):
        # Trying different ways to speed up. The code below seems ~10% slower
        # than first version
        keys=[]
        x=[]
        for f in list(self.data.keys()):
            if (f not in ['p', 'v', 's', 'compliance', 'resistance',
                          'inertance', 'f']):
                keys.append(f)
                x.append(self.data[f])
        for f in list(self.hr.data.keys()):
            keys.append(f)
            x.append(self.hr.data[f])
        for f in list(self.hs.data.keys()):
            keys.append(f)
            x.append(self.hs.data[f])
        for f in list(self.hs.memb.data.keys()):
            keys.append(f)
            x.append(self.hs.memb.data[f])
        for f in list(self.hs.ener.data.keys()):
            keys.append(f)
            x.append(self.hs.memb.data[f])
        for f in list(self.hs.myof.data.keys()):
            keys.append(f)
            x.append(self.hs.myof.data[f])
        if (self.br):
            for f in list(self.br.data.keys()):
                keys.append(f)
                x.append(self.br.data[f])
        if (self.gr):
            for f in list(self.gr.data.keys()):
                keys.append(f)
                x.append(self.gr.data[f])
        keys.append('write_mode')
        x.append(1)

        # Convert x to array
        x = np.asarray(x)
        self.sim_data.loc[self.write_counter, keys] = x

        # Update counter
        self.write_counter = self.write_counter + 1


def write_complete_data_to_envelope_data(self, index):
    """ Writes full data to envelope frame """

    for f in list(self.data.keys()):
        if (f not in ['p', 'v', 's', 'compliance', 'resistance',
                      'inertance', 'f']):
            self.envelope_data.at[self.envelope_counter, f] = self.data[f]
    for f in list(self.hr.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hr.data[f]
    for f in list(self.hs.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.data[f]
    for f in list(self.hs.memb.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.memb.data[f]
    for f in list(self.hs.ener.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.ener.data[f]
    for f in list(self.hs.myof.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.myof.data[f]
    if (self.br):
        for f in list(self.br.data.keys()):
            self.envelope_data.at[self.envelope_counter, f] = self.br.data[f]
    if (self.gr):
        for f in list(self.gr.data.keys()):
            self.envelope_data.at[self.envelope_counter, f] = self.gr.data[f]
    self.envelope_data.at[self.envelope_counter, 'write_mode'] = 1
    self.envelope_counter = self.envelope_counter + 1
    # Reset counter at limit
    if (self.envelope_counter == self.so.data['n_envelope_points']):
        self.envelope_counter = 0


def write_envelope_data_to_sim_data(self, index):
    """ Writes envelope data to data frame """

    # Cycle through picking off min and max values in envelope
    for f in list(self.data.keys()):
        if (f not in ['p', 'v', 's', 'compliance', 'resistance',
                      'inertance', 'f']):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hr.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.memb.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.ener.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.myof.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    if (self.br):
        for f in list(self.br.data.keys()):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    if (self.gr):
        for f in list(self.gr.data.keys()):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    self.sim_data.at[self.write_counter, 'write_mode'] = 2
    self.sim_data.at[self.write_counter+1, 'write_mode'] = 2
    self.write_counter = self.write_counter + 2

def write_output_files(self):
    """ Write sim to data file and run output hander """
    
    if (not self.sim_results_file_string == []):
        self.write_sim_results_to_file()
        
        if (not self.output_handler_file_string == []):
            self.run_output_handler()

def write_sim_results_to_file(self):
    """ Write sim results to specified file """

    # Save the simulation results to file
    if (not self.sim_results_file_string == []):
        output_file_string = os.path.abspath(self.sim_results_file_string)
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

def run_output_handler(self):
    """ Launches output handler """

    # Check the output file
    if (self.output_handler_file_string == []):
        print("No output_structure_file_string. Exiting")
        return

    cb_dump_file_string = []
    if self.so:
        if ('cb_dump_file_string' in self.so.data):
            cb_dump_file_string = self.so.data['cb_dump_file_string']

    self.oh = oh.output_handler(self.output_handler_file_string,
                                sim_data=self.sim_data,
                                cb_dump_file_string=cb_dump_file_string)
