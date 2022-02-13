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

        # Create data fields which change during simulation
        self.data = dict()
        self.growth_data_fields = ['G_a', 'G_b', 'G_c', 'G_result', 'setpoint']
        
        # And model fields that don't
        self.model = dict()
        self.growth_model_fields = ['type']
        

        # Pull off the components
        self.components = []
        if ('components' in growth_structure):
            growth_comp = growth_structure['components']
            for gc in growth_comp:
                print(gc)
                self.components.append(
                    growth_component(gc,
                                     self.parent_circulation))
                g_obj= self.components[-1]
                
                # Store some key fields for the main system
                for k in self.growth_data_fields:
                    self.data['growth_%s_%s' % (gc['type'][0:3], k)] = \
                        g_obj.data[k]
                
                for k in self.growth_model_fields:
                    self.model['growth_%s_%s' % (gc['type'][0:3], k)] = \
                        gc[k]

    def implement_time_step(self, time_step, growth_active=False):

        for gc in self.components:

            gc.implement_time_step(time_step, growth_active)

            # Update the data holders for reporting
            for k in self.growth_data_fields:
                self.data['growth_%s_%s' % (gc.model['type'][0:3], k)] = \
                    gc.data[k]
                
            # Implement change
            if (gc.model['type'] == 'eccentric'):
                self.parent_circulation.data['growth_dn'] = \
                    self.parent_circulation.data['n_hs'] * \
                        time_step * gc.data['G_result']

            if (gc.model['type'] == 'concentric'):
                self.parent_circulation.data['growth_dm'] = \
                    self.parent_circulation.data['ventricle_wall_volume'] * \
                        time_step * gc.data['G_result']



class growth_component():
    """ Class for a growth component """

    def __init__(self, gc_struct, parent_circulation):

        self.parent_circulation = parent_circulation

        # Set data fields, which can change during the simulation
        self.data = dict()
        self.data['G_a'] = 0.5
        self.data['G_b'] = 0.5
        self.data['G_c'] = 0.5
        self.data['G_result'] = 0
        self.data['setpoint'] = gc_struct['setpoint']
        
        # And model fields, which are fixed
        self.model = dict()
        model_fields = ['type', 'level', 'signal', 'rel_S',
                        'g_B_k_drive', 'g_B_k_recov',
                        'g_C_k_drive', 'g_C_k_recov',
                        'growth_factor', 'antigrowth_factor']
        for k in list(model_fields):
            self.model[k] = gc_struct[k]


    def implement_time_step(self, time_step, growth_active=0):

        # First update G_a
        
        self.data['G_a'] = self.return_G_a()
        
        # then G_b
        sol = odeint(self.diff_G_b, self.data['G_b'], [0, time_step],
                     args=((growth_active,)))
        self.data['G_b'] = sol[-1].item()
        
        # # then G_c
        # sol = odeint(self.diff_G_c, self.data['G_c'], [0, time_step],
        #              args=((growth_active,)))
        # self.data['G_c'] = sol[-1].item()

        # And finally G_result        
        self.data['G_result'] = self.return_G_result(self.data['G_b'])
        
            
    def return_G_a(self):
        """ Return the G_a signal """
        
        if (self.model['level'] == 'half_sarcomere'):
            y = self.parent_circulation.hs.data[self.model['signal']]
        elif(self.model['level'] == 'energetics'):
            y = self.parent_circulation.hs.ener.data[self.model['signal']]
        elif (self.model['level'] == 'circulation'):
            y = self.parent_circulation.data[self.model['signal']]
        
        
        G_a = 1 / (1 + np.exp(-self.model['rel_S'] * 
                              (y - self.data['setpoint']) /
                                  self.data['setpoint']))
        
        return G_a


    def diff_G_b(self, G_b, t, growth_active=False):
        """ Returns the rate of change of the G_b signal
            where G_b tends towards 1 when G_a is high and
            towards 0 when G_a is low """
        
        if (growth_active):
            if (self.data['G_a'] >= 0.5):
                dG_b_dt = -self.model['g_B_k_drive'] * \
                    (self.data['G_a'] - 0.5) * G_b
            else:
                dG_b_dt = -self.model['g_B_k_drive'] * \
                    (self.data['G_a'] - 0.5) * (1 - G_b)
        else:
            dG_b_dt = -self.model['g_B_k_recov'] * (G_b - 0.5)

        return dG_b_dt

    def diff_G_c(self, G_c, t, growth_active=False):
        """ Returns the rate of change of the G_c signal
            where G_c tends towards 0.5 when G_b is equal to 0.5
            but goes towards 1 when G_b is high and
            towards 0 when G_b is low """
        
        if (growth_active):
            if (self.data['G_b'] >= 0.5):
                dG_c_dt = self.model['g_C_k_drive'] * \
                    (self.data['G_b'] - 0.5) * (1 - G_c)
            else:
                dG_c_dt = self.model['g_C_k_drive'] * \
                    (self.data['G_b'] - 0.5) * G_c
        else:
            dG_c_dt = -1 * self.model['g_C_k_recov'] * (G_c - 0.5)

        return dG_c_dt
                     
            

    def return_G_result(self, G_c):

        if (G_c >= 0.5):
            m = self.model['growth_factor'] / 0.5
            G_result = m * (G_c-0.5)
        else:
            m = self.model['antigrowth_factor'] / 0.5
            G_result = m * (0.5 - G_c)

        return G_result
