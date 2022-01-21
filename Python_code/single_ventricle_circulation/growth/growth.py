# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 22:41:31 2020

@author: ken
"""

import numpy as np

from scipy.integrate import odeint

class growth():
    """ Class for growth """

    def __init__(self, growth_structure,
                 parent_circulation):

        # Set the parent circulation
        self.parent_circulation = parent_circulation

        # Create a data dictionary
        self.data = dict()

        # Pull off the components
        self.components = []
        if ('components' in growth_structure):
            growth_comp = growth_structure['components']
            for gc in growth_comp:
                self.components.append(
                    growth_component(gc,
                                     self.parent_circulation))
                g_obj= self.components[-1]
                if (g_obj.data['type'] == 'eccentric'):
                    self.data['growth_eccentric_g'] = g_obj.data['growth_g']
                    self.data['growth_eccentric_c'] = g_obj.data['growth_c']
                    self.data['gr_eccentric_set'] = g_obj.data['setpoint']
                else:
                    self.data['growth_concentric_g'] = g_obj.data['growth_g']
                    self.data['growth_concentric_c'] = g_obj.data['growth_c']
                    self.data['gr_concentric_set'] = g_obj.data['setpoint']


    def implement_time_step(self, time_step, growth_active=False):

        if (growth_active):
            for gc in self.components:

                gc.implement_time_step(time_step, True)

                # Update the data holders for reporting
                if (gc.data['type'] == 'eccentric'):
                    self.data['growth_eccentric_g'] = gc.data['growth_g']
                    self.data['growth_eccentric_c'] = gc.data['growth_c']
                    gc.data['setpoint'] = self.data['gr_eccentric_set']

                else:
                    self.data['growth_concentric_g'] = gc.data['growth_g']
                    self.data['growth_concentric_c'] = gc.data['growth_c']
                    gc.data['setpoint'] = self.data['gr_concentric_set']


class growth_component():
    """ Class for a growth component """

    def __init__(self,gc_struct, parent_circulation):

        self.parent_circulation = parent_circulation

        self.data = dict()
        for k in list(gc_struct.keys()):
            self.data[k] = gc_struct[k]
        # Add in growth and controller signals
        self.data['growth_g'] = 0.5
        self.data['growth_c'] = 0


    def implement_time_step(self, time_step, growth_active=0):

        if growth_active is False:
            self.data[self.growth_label_string] = 0
            return

        # Update the growth g and c signals
        sol = odeint(self.diff_g, self.data['growth_g'],
                     [0, time_step],
                     args=((growth_active,)))
        self.data['growth_g'] = sol[-1].item()
        self.data['growth_c'] = self.return_growth_c(self.data['growth_g'])

        if (self.data['type'] == 'eccentric'):
            self.parent_circulation.data['growth_dn'] = \
                self.parent_circulation.data['n_hs'] * \
                    time_step * self.data['growth_c']

        if (self.data['type'] == 'concentric'):
            self.parent_circulation.data['growth_dm'] = \
                self.parent_circulation.data['ventricle_wall_volume'] * \
                    time_step * self.data['growth_c']


    def diff_g(self, g, t, growth_active=False):
        
        if (growth_active):
            y=[]
            if (self.data['level'] == 'half_sarcomere'):
                y = self.parent_circulation.hs.data[self.data['signal']]
            elif(self.data['level'] == 'energetics'):
                y = self.parent_circulation.hs.ener.data[self.data['signal']]
            elif (self.data['level'] == 'circulation'):
                y = self.parent_circulation.data[self.data['signal']]
            
            if (np.abs(self.data['setpoint']) < np.finfo(float).eps):
                print('Growth setpoint is too close to zero')
                return
            
            if (y >= self.data['setpoint']):
                dgdt = self.data['k_drive'] * \
                    ((y - self.data['setpoint']) / \
                        self.data['setpoint']) * (1.0 - g)
            else:
                dgdt = self.data['k_drive'] * \
                    ((y - self.data['setpoint']) / \
                        self.data['setpoint']) * g
        else:
            dgdt = -1 * self.data['k_recov'] * (g - 0.5)

        return dgdt

    def return_growth_c(self, g):

        if (g >= 0.5):
            m = self.data['growth_factor'] / 0.5
            y = m*(g-0.5)
        else:
            m = self.data['antigrowth_factor'] / 0.5
            y = m*(0.5-g)

        return y
