# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 22:41:31 2020

@author: ken
"""

import numpy as np

class growth():
    """ Class for growth """

    def __init__(self, growth_structure,
                 parent_circulation):

        # Set the parent circulation
        self.parent_circulation = parent_circulation

        # Create data fields which change during simulation
        self.data = dict()
        self.growth_data_fields = ['G_prop', 'G_deriv', 'G_total',
                                   'G_result', 'setpoint', 'G_energy']
        
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
        
        # Set up shrinkage
        if ('shrinkage' in growth_structure):
            self.shrink_model = growth_structure['shrinkage']
            self.data['G_shrink'] = 0
            self.data['G_shrink_result'] = 0

    def implement_time_step(self, time_step, growth_active=False):
        
        # Set up shrink_buffer
        if ('shrink_model' in self.__dict__):
            if not ('shrink_buffer' in self.__dict__):
                self.shrink_buffer_n = round(self.shrink_model['buffer_time_s'] / time_step)
                self.shrink_buffer = np.zeros(self.shrink_buffer_n)
                self.shrink_buffer_counter = 0

            # Increment the counter
            self.shrink_buffer_counter = self.shrink_buffer_counter + 1
        
            # Roll the y_buffer to keep track of trailing average of input
            self.shrink_buffer = np.roll(self.shrink_buffer, -1)
            self.shrink_buffer[-1] = self.parent_circulation.hs.ener.data['ener_flux_total_ATP_consumed']

            if (self.shrink_buffer_counter > self.shrink_buffer_n):
                self.data['G_shrink'] = np.mean(self.shrink_buffer) * \
                        self.parent_circulation.data['ventricle_wall_volume']
                    
                self.data['G_shrink_result'] = \
                    self.shrink_model['shrink_factor'] * \
                        self.data['G_shrink']
  
            self.parent_circulation.data['shrink_dm'] = 0
            self.parent_circulation.data['shrink_dn'] = 0
            if (growth_active):
                self.parent_circulation.data['shrink_dm'] = \
                    self.parent_circulation.data['ventricle_wall_volume'] * \
                        time_step * self.data['G_shrink_result']
                self.parent_circulation.data['shrink_dn'] = \
                    self.parent_circulation.data['n_hs'] * \
                        time_step * self.data['G_shrink_result']

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
        self.data['G_prop'] = 0.0
        self.data['G_deriv'] = 0.0
        self.data['G_total'] = 0.0
        self.data['G_result'] = 0
        self.data['setpoint'] = gc_struct['setpoint']
        self.data['G_energy'] = 0
        
        # And model fields, which are fixed
        self.model = dict()
        model_fields = ['type', 'level', 'signal',
                        'rel_S', 'buffer_time_s', 'deriv_gain',
                        'growth_factor', 'energy_factor']
        for k in list(model_fields):
            self.model[k] = gc_struct[k]
            
        # Create a buffer
        self.buffer_n = 0
        self.t_buffer = []
        self.y_buffer = []
        self.G_prop_buffer = []
        self.ATP_consumed_buffer = []
        self.buffer_counter = 0


    def implement_time_step(self, time_step, growth_active=0):
        """ Updates the feedback signals used for growth """
        
        # Now work out which signal to put in the buffer
        if (self.model['level'] == 'half_sarcomere'):
            y = self.parent_circulation.hs.data[self.model['signal']]
        elif(self.model['level'] == 'energetics'):
            y = self.parent_circulation.hs.ener.data[self.model['signal']]
        elif (self.model['level'] == 'circulation'):
            y = self.parent_circulation.data[self.model['signal']]

        # Prep the buffer for the G_prop signal if required
        if (self.buffer_counter == 0):
            self.buffer_n = round(self.model['buffer_time_s'] / time_step)
            self.t_buffer = np.linspace(0, self.model['buffer_time_s'], self.buffer_n)
            self.y_buffer = y * np.ones(self.buffer_n)
            self.G_prop_buffer = np.zeros(self.buffer_n)
            self.ATP_consumed_buffer = np.zeros(self.buffer_n)
            
        # Increment the counter
        self.buffer_counter = self.buffer_counter + 1
        
        # Roll the y_buffer to keep track of trailing average of input
        self.y_buffer = np.roll(self.y_buffer, -1)
        self.y_buffer[-1] = y

        # First update G_prop
        self.data['G_prop'] = self.return_G_prop(np.mean(self.y_buffer))

        # Now roll the G_prop buffer to calculate deriv control
        self.G_prop_buffer = np.roll(self.G_prop_buffer, -1)
        self.G_prop_buffer[-1] = self.data['G_prop']

        # Now deriv control
        self.data['G_deriv'] = self.model['deriv_gain'] * \
                      np.polyfit(self.t_buffer, self.G_prop_buffer, 1)[0]                
        
        # Add in energy consumed
        self.ATP_consumed_buffer = np.roll(self.ATP_consumed_buffer, -1)
        self.ATP_consumed_buffer[-1] = \
            self.parent_circulation.hs.ener.data['ener_flux_total_ATP_consumed']
        
        self.data['G_energy'] = self.model['energy_factor'] * np.mean(self.ATP_consumed_buffer)
        
        # Now calculate G_total
        self.data['G_total'] = self.data['G_prop'] + self.data['G_deriv'] + \
                                self.data['G_energy']

        # And finally G_result, which needs a full buffer and growth active
        # to produce an output
        if (growth_active and (self.buffer_counter > self.buffer_n)):
            self.data['G_result'] = self.model['growth_factor'] * \
                                            self.data['G_total']
        else:
            self.data['G_result'] = 0

        # if (self.model['type'] == 'concentric'):
        #     print('\n_y_buffer')
        #     print(self.y_buffer)
        #     print('G_prop_buffer')
        #     print(self.G_prop_buffer)
        #     print('G_prop: %g' % self.data['G_prop'])
        #     print('G_deriv: %g' % self.data['G_deriv'])
        #     print('G_total: %g' % self.data['G_total'])
        #     print('G_result: %g' % self.data['G_result'])
            
        # if (self.buffer_counter == 10):
        #     exit(1)
        

        
            
    def return_G_prop(self, y):
        """ Return the G_a signal, which is a sigmoid scaled between -1 and 1
            with mid-value of 0 """
        
        G_prop = -1 + 2 / (1 + np.exp(-self.model['rel_S'] * 
                              (y - self.data['setpoint']) /
                                  self.data['setpoint']))
        
        return G_prop
