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
                
                
            pert_struct = s['perturbations']
            self.perturbations=[]
            for i,p in enumerate(pert_struct['perturbation']):
                self.perturbations.append(perturbation(p, self.data['time_step']))


class perturbation():
    """ Class for perturbations """
    
    def __init__(self, perturbation_struct, time_step):
        self.data = dict()
        self.data['variable'] = perturbation_struct['variable']
        self.data['t_start_s'] = perturbation_struct['t_start_s']
        self.data['t_stop_s'] = perturbation_struct['t_stop_s']
        self.data['total_change'] = perturbation_struct['total_change']
        n_steps = (self.data['t_stop_s'] - self.data['t_start_s']) / time_step
        self.data['t_start_ind'] = int(self.data['t_start_s'] / time_step)
        self.data['t_stop_ind'] = int(self.data['t_stop_s'] / time_step)
        self.data['increment'] = self.data['total_change'] / n_steps
        