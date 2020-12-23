import sys
import os
import numpy as np
import pandas as pd
# import cProfile
# import timeit
# from openpyxl import Workbook
# from scipy import signal
# from scipy.integrate import solve_ivp
# from scipy.constants import mmHg as mmHg_in_pascals


from .half_sarcomere import half_sarcomere as hs
from .heart_rate import heart_rate as hr

from protocol import protocol as prot
from output_handler import output_handler as oh

# from modules.SystemControl import system_control as syscon
# from modules.Perturbation import perturbation as pert
# from modules.Growth import growth as gr

import json

class single_ventricle_circulation():

    """Class for a single ventricle circulation"""
    from .implement import update_data_holders, analyze_data
    from .display import display_simulation, display_flows, display_pv_loop

    def __init__(self, model_json_file_string):

        # Check for file
        if (model_json_file_string==[]):
            print('No model file specified. Cannot create model')
            return
        
        # Load the model as a dict
        with open(model_json_file_string,'r') as f:
            sc_model = json.load(f)

        # Initialize the circulation object using data from the json file
        circ_model = sc_model["circulation"]

        # Define vessel list
        vessels_list = ['aorta','arteries','arterioles','capillaries',
                        'venules','veins']

        self.data = dict()
        self.data['time'] = 0
        self.data['no_of_compartments'] = int(circ_model['no_of_compartments'])
        self.data['blood_volume'] = circ_model['blood_volume']
        self.data['body_surface_area'] = circ_model['body_surface_area']
        
        for v in vessels_list:
            for t in ['resistance','compliance']:
                n = ('%s_%s') % (v,t)
                self.data[n]=circ_model[v][t]
                
        for t in circ_model['ventricle'].keys():
            self.data[('%s_%s') % ('ventricle',t)] = \
                circ_model['ventricle'][t]

        self.data['lv_mass'] = self.data['ventricle_wall_volume'] * \
            self.data['ventricle_wall_density']
            
        # Build the compliance and resistance arrays
        self.data['compliance'] = []
        for v in vessels_list:
            c = self.data[('%s_compliance' % v)]
            self.data['compliance'].append(c)
        # Add in 0 for ventricular compliance
        self.data['compliance'].append(0)
        # Convert to numpy array
        self.data['compliance'] = np.array(self.data['compliance'])
        
        self.data['resistance'] = []
        v_list = vessels_list
        v_list.append('ventricle')
        for v in v_list:
            r = self.data[('%s_resistance' % v)]
            self.data['resistance'].append(r)
        self.data['resistance'] = np.array(self.data['resistance'])
        
        # Create a heart-rate object
        self.hr = hr.heart_rate(sc_model['heart_rate'])

        # Pull off the half_sarcomere parameters and make a half-sarcomere
        self.hs = hs.half_sarcomere(sc_model['half_sarcomere'])

        # Deduce the hsl where force is zero and set the hsl to that length
        self.hs.data['slack_hsl'] = self.hs.myof.return_hs_length_for_force(0.0)
        delta_hsl = self.hs.data['slack_hsl'] - self.hs.data['hs_length']
        self.hs.update_simulation(0.0,delta_hsl, 0.0)

        # Deduce the slack circumference of the ventricle and deduce
        # the number of sarcomeres by dividing the slack_hsl
        self.data['lv_circumference'] = \
            self.return_lv_circumference(self.data['ventricle_slack_volume'])
        self.data['n_hs'] = 1e9*self.data['lv_circumference'] / self.hs.data['slack_hsl']
        
        # Create the volume and pressure
        self.data['v'] = np.zeros(self.data['no_of_compartments'])
        # Put most of the blood in the veins
        initial_ventricular_volume = 1.5 * self.data['ventricle_slack_volume']
        self.data['v'][-2] = self.data['blood_volume'] - initial_ventricular_volume
        self.data['v'][-1] = initial_ventricular_volume
        
        self.data['p'] = np.zeros(self.data['no_of_compartments'])
        for i in np.arange(0, self.data['no_of_compartments']-1):
            self.data['p'][i] = self.data['v'][i] / self.data['compliance'][i]
        self.data['p'][-1] = self.return_lv_pressure(self.data['v'][-1])

        # Set the wall thickness
        self.data['wall_thickness'] = \
            self.return_wall_thickness(self.data['v'][-1])

        # Set the t_counter
        self.t_counter = 0
   
    def create_data_structure(self):
        
        # ,
        #           'pressure_aorta','pressure_arteries','pressure_arterioles',
        #           'pressure_capillaries','pressure_venules','pressure_veins',
        #           'presure_ventricle',
        #           'volume_aorta','volume_arteries','volume_arterioles',
        #           'volume_capillaries','volume_venules','volume_veins',
        #           'volume_ventricle',
        #           'ventricle_wall_thickness', 'ventricle_wall_volume',
        #           'aorta_resistance','arteries_resistance','arterioles_resistance',
        #           'capillaries_resistance','venules_resistance','veins_resistance',
        #           'ventricle_resistance',
        #           'aorta_compliance','arteries_compliance','arterioles_compliance',
        #           'capillaries_compliance','venules_compliance','veins_compliance',
        #           'ventricle_resistance',
        #           'flow_ventricle_to_aorta', 'flow_aorta_to_arteries',
        #           'flow_arteries_to_arterioles', 'flow_arterioles_to_capillaries',
        #           'flow_capillaries_to_venules', 'flow_venules_to_veins',
        #           'flow_veins_to_ventricle',
        #           'flow_ventricle_to_veins', 'flow_veins_to_venules',
        #           'flow_venules_to_capillaries', 'flow_capillaries_to_arterioles',
        #           'flow_arterioles_to_arteries', 'flow_arteries_to_aorta',
        #           'flow_aorta_to_ventricle']
        
        self.sim_data = pd.DataFrame()
        z = np.zeros(self.prot.data['no_of_time_steps'])
        
        data_fields = list(self.data.keys()) + \
                        list(self.hr.data.keys()) + \
                        list(self.hs.data.keys()) + \
                        list(self.hs.memb.data.keys()) + \
                        list(self.hs.myof.data.keys())
        
        for f in data_fields: 
            s = pd.Series(data=z, name=f)
            self.sim_data = pd.concat([self.sim_data, s], axis=1)
       
        print(data_fields)
        return

    def run_simulation(self,
                       protocol_file_string=[],
                       output_handler_file_string=[]):
        """ Run the simulation """

        # Load the protocol
        if (protocol_file_string==[]):
            print("No protocol_file_string. Exiting")
            return
        self.prot = prot.protocol(protocol_file_string)
        
        # Now that you know how many time-points there are,
        # create the data structure
        self.create_data_structure()
       
        # Step through the simulation
        self.t_counter = 0
        for i in np.arange(self.prot.data['no_of_time_steps']):
            self.implement_time_step(self.prot.data['time_step'])
        
         # Load the output_handler and process
        if (output_handler_file_string==[]):
            print("No output_structure_file_string. Exiting")
            return
        # 
        self.oh = oh.output_handler(output_handler_file_string,
                                    self.sim_data)
       
        print(self.sim_data)        
        
        return
    
    def implement_time_step(self, time_step):
        """ Implements time step """
        
        self.data['time'] = self.data['time'] + time_step
       
        # Display progress
        if ((self.data['time'] % 1) < 1e-4):
            print('Sim time: %.0f' % (self.t_counter * time_step))
        
        # Run the hr module
        activation = self.hr.implement_time_step(time_step)
        for f in list(self.hr.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hr.data[f]
       
        # Advance half_sarcomere forward in time
        # First update the kinetic steps
        self.hs.update_simulation(time_step, 0, activation)
        
        # Update the object data
        self.hs.update_data()
        
        # Now update the sim_data
        for f in list(self.data.keys()):
            if (f not in ['p','v','compliance','resistance']):
                self.sim_data.at[self.t_counter, f] = self.data[f]
        for f in list(self.hs.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.data[f]
        for f in list(self.hs.memb.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.memb.data[f]
        for f in list(self.hs.myof.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.myof.data[f]

        # Update the t counter for the next step
        self.t_counter = self.t_counter + 1

        
    def return_lv_pressure(self, lv_volume):
        """ return pressure for a given volume """ 
        from scipy.constants import mmHg as mmHg_in_pascals
        
        # Estimate the force produced at the new length
        new_lv_circumference = self.return_lv_circumference(lv_volume)
        new_hs_length = 1e9 * new_lv_circumference / self.data['n_hs']
        delta_hsl = new_hs_length - self.hs.data['hs_length']
        f = self.hs.myof.check_myofilament_forces(delta_hsl)
        total_force = f['total_force']
        
        internal_r = self.return_radius_for_volume(lv_volume)
        wall_thickness = self.return_wall_thickness(lv_volume)
        
        # Pressure from Laplaces law
        P_in_pascals = 2.0 * total_force * wall_thickness / internal_r
        P_in_mmHg = P_in_pascals / mmHg_in_pascals
        
        return P_in_mmHg
    
    
    def return_lv_circumference(self, lv_volume):
        # 0.001 below is to do with liters to meters conversion
        if (lv_volume > 0.0):
            lv_circum = (2.0 * np.pi *
                         self.return_radius_for_volume(lv_volume +
                                                  self.data['ventricle_wall_volume']))
        else:
            lv_circum = (2.0 * np.pi * 
                         self.return_radius_for_volume(self.data['ventricle_wall_volume']))
    
        return lv_circum

    def return_wall_thickness(self, chamber_volume):
        internal_r = self.return_radius_for_volume(chamber_volume)
        external_r = self.return_radius_for_volume(chamber_volume +
                                              self.data['ventricle_wall_volume'])
        
        return (external_r - internal_r)

    def return_radius_for_volume(self, volume):
        r = np.power((3.0 * 0.001 * volume) / (2.0 * np.pi), (1.0/3.0))
        return r
