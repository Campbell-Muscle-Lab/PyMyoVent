# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 12:37:20 2020

@author: ken
"""

class heart_rate():
    """ Class for heart-rate """
    
    def __init__(self, heart_rate_struct):
        
        # Initialize the data dict
        self.data = dict()
        for f in list(heart_rate_struct.keys()):
            self.data[f] = heart_rate_struct[f]

        self.data['t_active_left'] = 0
        self.data['t_RR'] = self.data['t_first_activation']
    
    def implement_time_step(self, time_step):
        
        # Reduce counters
        self.data['t_RR'] -= time_step
        self.data['t_active_left'] -= time_step
        
        # Reset 
        if (self.data['t_RR'] <= 0):
            self.data['t_active_left'] = self.data['t_active_period']
            self.data['t_RR'] = self.data['t_active_period'] + \
                                self.data['t_quiescent_period']

        # Manage t_active_left
        if (self.data['t_active_left'] > 0):
            activation = 1
        else:
            activation = 0
            self.data['t_active_left'] = 0
        
        return activation
    
    def return_heart_rate(self):
        """ returns heart rate in beats per minute """
        
        return 60 * 1 / (self.data['t_active_period'] +
                             self.data['t_quiescent_period'])
        