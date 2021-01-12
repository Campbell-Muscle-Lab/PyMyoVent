# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 15:03:44 2020

@author: ken
"""

import json

class protocol():
    
    def __init__(self, protocol_file_string):
        
        self.data = dict()
        
        with open(protocol_file_string,'r') as f:
            s = json.load(f)

        prot = s['protocol']
        for p in list(prot.keys()):
            self.data[p] = prot[p]

        self.perturbations = []
        if ('perturbations' in s):
            pert_struct = s['perturbations']
            for i, p in enumerate(pert_struct['perturbation']):
                self.perturbations.append(perturbation(p,
                                                       self.data['time_step']))

        self.baro_activations = []
        if ('baroreflex' in s):
            baro_struct = s['baroreflex']
            for i, b in enumerate(baro_struct['activations']):
                self.baro_activations.append(baro_activation(
                    b, self.data['time_step']))

        self.growth_activations = []
        if ('growth' in s):
            growth_struct = s['growth']
            for i,g in enumerate(growth_struct['activations']):
                self.growth_activations.append(growth_activation(g, self.data['time_step']))


class perturbation():
    """ Class for perturbations """
    
    def __init__(self, perturbation_struct, time_step):
        self.data = dict()
        self.data['variable'] = perturbation_struct['variable']
        self.data['t_start_s'] = perturbation_struct['t_start_s']
        self.data['t_start_ind'] = int(self.data['t_start_s'] / time_step)
        if ('new_value' in perturbation_struct):
            self.data['new_value'] = perturbation_struct['new_value']
        else:
            self.data['t_stop_s'] = perturbation_struct['t_stop_s']
            self.data['total_change'] = perturbation_struct['total_change']
            n_steps = (self.data['t_stop_s'] - self.data['t_start_s']) / time_step
            self.data['t_stop_ind'] = int(self.data['t_stop_s'] / time_step)
            self.data['increment'] = self.data['total_change'] / n_steps

class baro_activation():
    """ Class for baro-activation """
    
    def __init__(self, baro_struct, time_step):
        self.data = dict()
        self.data['t_start_s'] = baro_struct['t_start_s']
        self.data['t_stop_s'] = baro_struct['t_stop_s']
        self.data['t_start_ind'] = int(self.data['t_start_s'] / time_step)
        self.data['t_stop_ind'] = int(self.data['t_stop_s'] / time_step)
        
class growth_activation():
    """ Class for growth-activation """

    def __init__(self, growth_struct, time_step):
        self.data = dict()
        self.data['t_start_s'] = growth_struct['t_start_s']
        self.data['t_stop_s'] = growth_struct['t_stop_s']
        self.data['t_start_ind'] = int(self.data['t_start_s'] / time_step)
        self.data['t_stop_ind'] = int(self.data['t_stop_s'] / time_step)
    