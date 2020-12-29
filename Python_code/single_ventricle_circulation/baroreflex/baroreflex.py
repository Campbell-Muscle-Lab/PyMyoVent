# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 13:41:59 2020

@author: ken
"""

import numpy as np

from scipy.integrate import odeint

class baroreflex():
    """ Class for the baroreflex """
    
    def __init__(self, baro_structure,
                 parent_circulation,
                 pressure=0):
        
        # Set the parent circulation
        self.parent_circulation = parent_circulation
        
        # Initialise the model dict
        self.model = dict()
        self.model['baro_b_slope'] = baro_structure['b_slope']
        self.model['baro_k_drive'] = baro_structure['k_drive']
        self.model['baro_k_recov'] = baro_structure['k_recov']
        
        # Initialise the data dict
        self.data = dict()
        self.data['baro_b_setpoint'] = baro_structure['b_setpoint']
        self.data['baro_b'] = self.return_b(pressure)
        self.data['baro_c'] = 0.5
        
        # Pull off the controls
        self.controls = []
        if ('controls' in baro_structure):
            baro_cont = baro_structure['controls']['control']
            for bc in baro_cont:
                self.controls.append(
                        reflex_control(bc,
                                       self.parent_circulation))
                
        
    def implement_time_step(self, pressure, time_step,
                            reflex_active=0):
        """ implements time-step """
        
        # First update baro c
        self.data['baro_b'] = self.return_b(pressure)
        sol = odeint(self.diff_c, self.data['baro_c'],
                     [0, time_step],
                     args=((reflex_active,)))
        self.data['baro_c'] = sol[-1].item()
        
        # Now cycle through the controls and update the variables
        for bc in self.controls:
            y = bc.return_output(self.data['baro_c'])
            # Now implement the change
            if (bc.data['level']=='heart_rate'):
                self.parent_circulation.hr.data[bc.data['variable']] = y
            if (bc.data['level']=='membranes'):
                self.parent_circulation.hs.memb.data[bc.data['variable']] = y
            if (bc.data['level']=='myofilaments'):
                self.parent_circulation.hs.myof.data[bc.data['variable']] = y
            if (bc.data['level']=='circulation'):
                self.parent_circulation.data[bc.data['variable']] = y


    def return_b(self, pressure):
        b = 1 / (1 + np.exp(-self.model['baro_b_slope']*
                            (pressure - self.data['baro_b_setpoint'])))
        return b    

    def diff_c(self, c, t, reflex_active=False):
        dcdt = 0
        if (reflex_active):
            if (self.data['baro_b'] >= 0.5):
                dcdt += -self.model['baro_k_drive'] * \
                        (self.data['baro_b']-0.5)*c
            if (self.data['baro_b'] < 0.5):
                dcdt += -self.model['baro_k_drive'] * \
                        (self.data['baro_b']-0.5) * (1-c)
        else:
            dcdt = -self.model['baro_k_recov'] * (c-0.5)

        return dcdt

        
class reflex_control():
    """ Class for a reflex control """
    
    def __init__(self, control_struct, parent_circulation):
        self.data = dict()
        for k in list(control_struct.keys()):
            self.data[k] = control_struct[k]
        self.data['basal_value'] = 0
            
        # Now try to find the base value linking to the
        # other components through the parent circulation
        if (self.data['level']=='heart_rate'):
            self.data['basal_value'] = \
                parent_circulation.hr.data[self.data['variable']]
        if (self.data['level']=='membranes'):
            self.data['basal_value'] = \
                parent_circulation.hs.memb.data[self.data['variable']]
        if (self.data['level']=='myofilaments'):
            self.data['basal_value'] = \
                parent_circulation.hs.myof.data[self.data['variable']]
        if (self.data['level']=='circulation'):
            self.data['basal_value'] = \
                parent_circulation.data[self.data['variable']]                
                
        # Now set the values at maximum parasympathetic and
        # sympathetic drive respectively
        self.data['para_value'] = self.data['para_factor'] * \
                                    self.data['basal_value']
        self.data['symp_value'] = self.data['symp_factor'] * \
                                    self.data['basal_value']

    def return_output(self, c):
        if (c>=0.5):
            m = (self.data['symp_value'] - self.data['basal_value'])/0.5
            y = self.data['basal_value'] + m*(c-0.5)
        else:
            m = (self.data['basal_value'] - self.data['para_value'])/0.5
            y = self.data['basal_value'] + m*(c-0.5)

        return y