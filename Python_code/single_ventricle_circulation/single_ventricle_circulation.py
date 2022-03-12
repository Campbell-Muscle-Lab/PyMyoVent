import os
import json
import numpy as np
import pandas as pd

from pathlib import Path

from .half_sarcomere import half_sarcomere as hs
from .heart_rate import heart_rate as hr
from .baroreflex import baroreflex as br
from .growth import growth as gr
from .vad import vad as va

from protocol import protocol as prot
from sim_options import sim_options as sim_opt

class single_ventricle_circulation():
    """Class for a single ventricle circulation"""

    # Import functions from additional files
    from .calculate_properties import \
        return_wall_thickness, \
        return_lv_circumference, \
        return_internal_radius_for_chamber_volume, \
        return_lv_pressure, \
        return_stroke_work

    from .write_data import \
        write_complete_data_to_sim_data, \
        write_complete_data_to_envelope_data, \
        write_envelope_data_to_sim_data, \
        write_output_files, \
        write_sim_results_to_file,\
        run_output_handler

    def __init__(self, model_json_file_string, thread_id=[]):

        # Check for file
        if (model_json_file_string == []):
            print('No model file specified. Cannot create model')
            return

        # Set thread id
        self.thread_id = thread_id

        # Status
        print('Initialising single_ventricle_circulation from %s on thread_id %i'
              % (model_json_file_string, self.thread_id))

        # Load the model as a dict
        with open(model_json_file_string, 'r') as f:
            sc_model = json.load(f)

        # Create a model dict for things that do not change during a simulation
        self.model = dict()
        # And a data dict for things that might
        self.data = dict()

        # Initialize the circulation object using data from the json file
        circ_model = sc_model["circulation"]

        # Store the number of compartments
        self.model['no_of_compartments'] = len(circ_model['compartments'])

        # Initialise the time
        self.data['time'] = 0

        # Store blood volume
        self.data['blood_volume'] = circ_model['blood_volume']

        vessels_list = []
        for comp in circ_model['compartments']:
            if not (comp['name'] == 'ventricle'):
                n = comp['name']
                vessels_list.append(comp['name'])
                for t in ['resistance', 'compliance', 'slack_volume',
                          'inertance']:
                    n = ('%s_%s') % (comp['name'], t)
                    self.data[n] = comp[t]
            else:
                # Ventricle
                self.data['ventricle_resistance'] = comp['resistance']
                self.data['ventricle_slack_volume'] = comp['slack_volume']
                self.data['ventricle_wall_volume'] = comp['wall_volume']
                self.model['ventricle_wall_density'] = comp['wall_density']
                self.model['ventricle_inertance'] = comp['inertance']

        # Build the compliance, inertance, and resistance arrays
        self.data['compliance'] = []
        for v in vessels_list:
            c = self.data[('%s_compliance' % v)]
            self.data['compliance'].append(c)
        # Add in 0 for ventricular compliance
        self.data['compliance'].append(0)
        # Convert to numpy array
        self.data['compliance'] = np.array(self.data['compliance'])

        self.data['inertance'] = []
        for v in vessels_list:
            i = self.data[('%s_inertance' % v)]
            self.data['inertance'].append(i)
        # Add in 0 for ventricular inertance
        self.data['inertance'].append(0)
        # Convert to numpy array
        self.data['inertance'] = np.array(self.data['inertance'])

        self.data['resistance'] = []
        vessels_list.append('ventricle')
        self.model['compartment_list'] = vessels_list
        for v in self.model['compartment_list']:
            r = self.data[('%s_resistance' % v)]
            self.data['resistance'].append(r)
        self.data['resistance'] = np.array(self.data['resistance'])

        # Add in conductances for valves
        self.data['mitral_insufficiency_conductance'] = 0
        self.data['aortic_insufficiency_conductance'] = 0

        # Create a heart-rate object
        self.hr = hr.heart_rate(sc_model['heart_rate'])

        # Pull off the half_sarcomere parameters and make a half-sarcomere
        self.hs = hs.half_sarcomere(sc_model['half_sarcomere'], self)

        # Deduce the hsl where force is zero and set the hsl to that length
        self.hs.data['slack_hsl'] = \
            self.hs.myof.return_hs_length_for_stress(0.0)
        delta_hsl = self.hs.data['slack_hsl'] - self.hs.data['hs_length']
        self.hs.update_simulation(0.0, delta_hsl, 0.0)

        # Deduce the slack circumference of the ventricle and deduce
        # the number of sarcomeres by dividing the slack_hsl
        self.data['ventricle_circumference'] = \
            self.return_lv_circumference(self.data['ventricle_slack_volume'])
        self.data['n_hs'] = 1e9*self.data['ventricle_circumference'] / \
            self.hs.data['slack_hsl']

        # Create and fill arrays for the volume, slack_volume and pressure
        self.data['v'] = np.zeros(self.model['no_of_compartments'])
        self.data['s'] = np.zeros(self.model['no_of_compartments'])
        # Put most of the blood in the veins
        for i, c in enumerate(self.model['compartment_list']):
            n = ('%s_slack_volume' % c)
            self.data['s'][i] = self.data[n]
            self.data['v'][i] = self.data[n]
        self.data['total_slack_volume'] = sum(self.data['s'])

        # Excess blood goes in veins
        self.data['v'][-2] = self.data['v'][-2] + \
            (self.data['blood_volume'] - self.data['total_slack_volume'])

        # Set the thick wall multiplier
        # 0 for thin_wall, 1 for thick_wall
        self.thick_wall_multiplier = 0
        if (sc_model['half_sarcomere']['myofilaments']['implementation']['thick_wall_approximation']):
            self.thick_wall_multiplier = 1

        self.data['p'] = np.zeros(self.model['no_of_compartments'])
        for i in np.arange(0, self.model['no_of_compartments']-1):
            self.data['p'][i] = (self.data['v'][i] - self.data['s'][i]) / \
                self.data['compliance'][i]
        self.data['p'][-1] = self.return_lv_pressure(self.data['v'][-1])

        # Allocate space for pressure, volume and slack_volume
        for i, v in enumerate(self.model['compartment_list']):
            self.data['pressure_%s' % v] = self.data['p'][i]
            self.data['volume_%s' % v] = self.data['v'][i]
            self.data['slack_volume_%s' % v] = self.data['s'][i]

        # Add in the wall thickness
        self.data['ventricle_wall_thickness'] = self.return_wall_thickness(
            self.data['volume_ventricle'])

        # Allocate space for flows
        self.data['f'] = np.zeros(self.model['no_of_compartments'])
        if (self.model['no_of_compartments'] == 7):
            self.model['flow_list'] = \
                ['flow_ventricle_to_aorta',
                 'flow_aorta_to_arteries',
                 'flow_arteries_to_arterioles',
                 'flow_arterioles_to_capillaries',
                 'flow_capillaries_to_venules',
                 'flow_venules_to_veins',
                 'flow_veins_to_ventricle',
                 'flow_VAD']
            for f in self.model['flow_list']:
                self.data[f] = 0
        else:
            print('Initialisation: Flows need to be rebuilt for model')
            exit(1)

        # Set the heart rate
        self.data['heart_rate'] = self.hr.return_heart_rate()

        # If requried, create the baroreceptor
        self.data['baro_active'] = 0
        if ('baroreflex' in sc_model):
            self.br = br.baroreflex(sc_model['baroreflex'],
                                    self,
                                    self.data['pressure_arteries'])
        else:
            self.br = []

        # Create the growth modules
        self.data['growth_active'] = 0
        self.data['growth_dn'] = 0
        self.data['growth_dm'] = 0

        if ('growth' in sc_model):
            self.gr = gr.growth(sc_model['growth'], self)
        else:
            self.gr = []

        # Add functional fields
        self.data['stroke_volume'] = 0
        self.data['ejection_fraction'] = 0
        self.data['stroke_work'] = 0
        self.data['stroke_cost'] = 0
        self.data['efficiency'] = 0
        self.data['mean_arterial_pressure'] = 0

        # Set the last index for heart_beat initiation
        self.last_heart_beat_time = -1

        # If required create a VAD
        if ('VAD' in sc_model):
            self.va = va.VAD(sc_model['VAD'], self)
        else:
            self.va = []
        
        # Save space for some filenames
        self.sim_results_file_string = []
        self.output_handerl_file_string = []

        # Create a sim_options object
        self.so = []

    def create_data_structure(self, no_of_data_points):
        """ returns a data frame from the data dicts of each component """

        sim_data = pd.DataFrame()
        z = np.zeros(no_of_data_points)

        # Prune some fields from the self_data
        sk = []
        for k in self.data.keys():
            if (k not in ['p','v','s','compliance','resistance',
                          'inertance','f']):
                sk.append(k)

        data_fields = sk + \
            list(self.hr.data.keys()) + \
            list(self.hs.data.keys()) + \
            list(self.hs.memb.data.keys()) + \
            list(self.hs.myof.data.keys())
        if hasattr(self.hs, 'ener'):
            data_fields = data_fields + \
                list(self.hs.ener.data.keys())
        data_fields = data_fields + ['write_mode']

        # Add in fields from optional modules
        if (self.br != []):
            data_fields = data_fields + list(self.br.data.keys())
        if (self.gr != [] ):
            data_fields = data_fields + list(self.gr.data.keys())
        if (self.va != []):
            data_fields = data_fields + list(self.va.data.keys())

        for f in data_fields:
            s = pd.Series(data=z, name=f)
            sim_data = pd.concat([sim_data, s], axis=1)

        return sim_data

    def run_simulation(self,
                       protocol_file_string=[],
                       output_handler_file_string=[],
                       sim_options_file_string=[],
                       sim_results_file_string=[]):
        """ Run the simulation """

        # Load the protocol
        if (protocol_file_string == []):
            print("No protocol_file_string. Exiting")
            return
        self.prot = prot.protocol(protocol_file_string)

        # Check for sim_options
        if (sim_options_file_string):
            self.so = sim_opt.sim_options(sim_options_file_string,
                                          self.prot.data['time_step'],
                                          self)
        else:
            self.so = []

        # Determine the number of data points in the output file
        # If burst mode has been set in the sim_options, we need to create
        # two data structures - one for the main data, and the other that
        # can be used to calculate the min and max values in a given time
        # envelope
        # Otherwise, we just need one structure with a row for every
        # time-point in the simulation
        if ('n_burst_points' in self.so.data):
            self.sim_data = \
                self.create_data_structure(self.so.data['n_burst_points'])
            self.envelope_data = \
                self.create_data_structure(self.so.data['n_envelope_points'])
        else:
            self.sim_data = \
                self.create_data_structure(self.prot.data['no_of_time_steps'])

        # Update the file handles
        self.sim_results_file_string = sim_results_file_string
        self.output_handler_file_string = output_handler_file_string

        # Step through the simulation
        time_step = self.prot.data['time_step']
        self.t_counter = 0
        self.write_counter = 0
        self.envelope_counter = 0
        for i in np.arange(self.prot.data['no_of_time_steps']):
            # Iplmement a step
            self.implement_time_step(time_step)
            # Check whether we should dump the output
            if ('periodic_save_interval_s' in self.so.data):
                if ((i > 0) and 
                    (np.mod(self.data['time'],
                            self.so.data['periodic_save_interval_s'])
                                 < time_step) and
                    (i < (self.prot.data['no_of_time_steps']-1))):
                    # Write sim data to file and run the output handler
                    self.write_output_files()       

        # Tidy up by writing sim data to file and running the output handler
        self.write_output_files()


    def return_system_values(self, time_interval=3):
        d = dict()
        if (self.data['time'] > time_interval):
            self.temp_data = \
                self.sim_data[self.sim_data['time'].between(
                    self.data['time']-time_interval, self.data['time'])]
            d['volume_ventricle_max'] = \
                self.temp_data['volume_ventricle'].max()
            d['stroke_volume'] = d['volume_ventricle_max'] - \
                self.temp_data['volume_ventricle'].min()
            d['ejection_fraction'] = self.temp_data['ejection_fraction'].mean()
            d['heart_rate'] = self.data['heart_rate']
            d['cardiac_output'] = d['stroke_volume'] * d['heart_rate']
            d['hs_length_max'] = self.temp_data['hs_length'].max()
            d['fractional_shortening'] = \
                (d['hs_length_max'] - self.temp_data['hs_length'].min()) / \
                d['hs_length_max']
            d['cpt_int_pas_stress_mean'] = self.temp_data['cpt_int_pas_stress'].mean()
            d['cpt_cb_stress_mean'] = self.temp_data['cpt_cb_stress'].mean()
            d['efficiency'] = self.data['efficiency']
            d['pressure_artery_max'] = \
                self.temp_data['pressure_arteries'].max()
            d['pressure_artery_min'] = \
                self.temp_data['pressure_arteries'].min()
            d['pressure_veins_mean'] = \
                self.temp_data['pressure_veins'].mean()
            d['volume_veins_proportion'] = \
                self.temp_data['volume_veins'].mean() / \
                self.data['blood_volume']
            d['n_hs'] = self.data['n_hs']
            d['dn'] = self.data['growth_dn']
            d['ventricle_wall_volume'] = self.data['ventricle_wall_volume']
            d['dm'] = self.data['growth_dm']

            if ('ener_intracell_ATP_conc' in self.temp_data):
                d['ener_intracell_ATP_conc'] = \
                    self.temp_data['ener_intracell_ATP_conc'].mean()

            if ('baro_B_a' in self.temp_data):
                d['baro_B_a'] = self.temp_data['baro_B_a'].mean()
            if ('baro_B_b' in self.temp_data):
                d['baro_B_b'] = self.temp_data['baro_B_b'].mean()
            if ('baro_B_c_heart_rate_t_quiescent_period' in self.temp_data):
                d['baro_B_c_heart_rate'] = self.temp_data['baro_B_c_heart_rate_t_quiescent_period'].mean()

        return d

    def implement_time_step(self, time_step):
        """ Implements time step """
        self.data['time'] = self.data['time'] + time_step

        # Display progress
        if (self.t_counter % 1000 == 0):
            print('Thread_id[%i]: Sim time (s): %.0f  %.0f%% complete' %
                  (self.thread_id, self.data['time'],
                   100*self.t_counter/self.prot.data['no_of_time_steps']))
            system_values = self.return_system_values()
            print(json.dumps(system_values, indent=4))

        # Check for baroreflex and implement
        if (self.br):
            self.data['baro_active'] = 0
            for b in self.prot.baro_activations:
                if ((self.t_counter >= b.data['t_start_ind']) and
                        (self.t_counter < b.data['t_stop_ind'])):
                    self.data['baro_active'] = 1

            self.br.implement_time_step(self.data['pressure_arteries'],
                                        time_step,
                                        reflex_active=
                                        self.data['baro_active'])

        # Check and implement perturbations
        for p in self.prot.perturbations:

            if((self.t_counter >= p.data['t_start_ind']) and
               (self.t_counter < p.data['t_stop_ind'])):
                if (p.data['level'] == 'myofilaments'):
                    self.hs.myof.data[p.data['variable']] += \
                        p.data['increment']
                elif (p.data['level'] == 'VAD'):
                    self.va.data[p.data['variable']] += \
                        p.data['increment']
                elif (p.data['level'] == 'circulation'):
                    self.data[p.data['variable']] += \
                        p.data['increment']
                elif (p.data['level'] == 'baroreflex'):
                    self.br.data[p.data['variable']] += \
                        p.data['increment']
                elif (p.data['level'] == 'growth'):
                    self.gr.data[p.data['variable']] += \
                        p.data['growth']

                self.check_baroreflex_perturbations(p)

        # Rebuild system arrays
        self.rebuild_from_perturbations()

        # Check for growth module and implement
        if (self.gr):
            self.data['growth_active'] = 0
            for g in self.prot.growth_activations:
                if ((self.t_counter >= g.data['t_start_ind']) and
                        (self.t_counter < g.data['t_stop_ind'])):
                    self.data['growth_active'] = 1

            self.gr.implement_time_step(time_step,
                                        growth_active=
                                        self.data['growth_active'])

        # Run the hr module
        (activation, new_beat) = self.hr.implement_time_step(time_step)

        # Advance half_sarcomere forward in time
        # First update the kinetic steps
        self.hs.update_simulation(time_step, 0, activation)

        # Now evolve volumes
        self.data['v'] = self.evolve_volumes(time_step, self.data['v'])

        # Apply the length change to the half-sarcomere
        new_circumference = self.return_lv_circumference(
                                self.data['v'][-1])
        delta_circumference = new_circumference - \
            self.data['ventricle_circumference']
        delta_hsl = ((1e9*delta_circumference) -
                     (self.hs.data['hs_length'] * self.data['growth_dn'])) / \
            self.data['n_hs']

        # Update model
        self.data['ventricle_circumference'] = new_circumference
        self.data['ventricle_wall_volume'] = \
            self.data['ventricle_wall_volume'] + \
            self.data['growth_dm'] + \
            (self.data['ventricle_wall_volume'] *
             self.data['growth_dn'] / self.data['n_hs'])
        self.data['n_hs'] = self.data['n_hs'] + self.data['growth_dn']

        # Update the half-sarcomere with the new length
        self.hs.update_simulation(0, delta_hsl, 0)

        # Update the pressures
        for i in range(self.model['no_of_compartments']-1):
            self.data['p'][i] = (self.data['v'][i] - self.data['s'][i]) / \
                self.data['compliance'][i]
        self.data['p'][-1] = self.return_lv_pressure(self.data['v'][-1])

        # Update the objects' data
        self.update_data(time_step, new_beat)
        self.hs.update_data(new_beat)

        # Now that ventricular volume is calculated, update the wall thickness
        self.data['ventricle_wall_thickness'] = self.return_wall_thickness(
            self.data['volume_ventricle'])

        # Now update the sim_data if appropriate
        # This requires checking if we are in burst mode and if so,
        # what write mode we are in
        save_mode = 1
        burst_mode = 'complete'
        if ('n_burst_points' in self.so.data):
            # Work out what we want to write to file
            (save_mode, burst_mode) = \
                self.so.return_save_status(self.data['time'])
            # Update the envelope data
            self.write_complete_data_to_envelope_data(self.envelope_counter)

        if (save_mode == 1):
            # Write full data to sim_data
            self.write_complete_data_to_sim_data(self.write_counter)
        if (save_mode == 2):
            # Write envelope data to sim_data
            self.write_envelope_data_to_sim_data(self.write_counter)

        # Dump cb distributions if required
        if self.so:
            if ('cb_dump_file_string' in self.so.data):
                if ((self.t_counter >=
                     self.so.data['cb_dump_t_start_ind']) and
                    (self.t_counter <
                     self.so.data['cb_dump_t_stop_ind'])):
                    self.so.append_cb_distribution(self.data['time'])

        # Update the last heart beat time if required
        if (new_beat > 0):
            self.last_heart_beat_time = self.data['time']

        # Update the t counter for the next step
        self.t_counter = self.t_counter + 1

    def check_baroreflex_perturbations(self, p):
        """ Checks whether a parameter under reflex control has been
            externally perturned and adjusts values accordingly """

        for bc in self.br.controls:
            if (bc.data['variable'] == p.data['variable']):
                bc.data['basal_value'] = bc.data['basal_value'] + \
                    p.data['increment']
                bc.data['para_value'] == bc.data['para_factor'] * \
                    bc.data['basal_value']
                bc.data['symp_value'] == bc.data['symp_factor'] * \
                    bc.data['basal_value']

    def return_min_max(self, data_frame):
        """ returns list of min and max values from a data frame """
        min_value = data_frame.min()
        max_value = data_frame.max()

        return min_value, max_value

    def rebuild_from_perturbations(self):
        """ builds system arrays that could change during simulation """

        for i, v in enumerate(self.model['compartment_list']):
            r = self.data[('%s_resistance' % v)]
            self.data['resistance'][i] = r

        for i, v in enumerate(self.model['compartment_list']):
            if (i < (self.model['no_of_compartments']-1)):
                c = self.data[('%s_compliance' % v)]
                self.data['compliance'][i] = c

    def update_data(self, time_step, new_beat):
        """ Update data after a time step """

        # Update data for the heart-rate
        self.data['heart_rate'] = self.hr.return_heart_rate()

        self.data['f'] = self.return_flows(self.data['v'], time_step)
        for i, f in enumerate(self.model['flow_list']):
            self.data[f] = self.data['f'][i]

        for i, v in enumerate(self.model['compartment_list']):
            self.data['pressure_%s' % v] = self.data['p'][i]
            self.data['volume_%s' % v] = self.data['v'][i]
        
        if (hasattr(self.hs, 'ener')):
            self.data['ener_ATPase_to_myo'] = \
                self.hs.ener.data['ener_flux_ATP_consumed'] / \
                    (0.001 * self.data['ventricle_wall_volume'] *
                     (1.0 - self.hs.myof.data['prop_fibrosis']) * 
                      self.hs.myof.data['prop_myofilaments'])

        # If it is new beat, calculate cycle metrics
        if ((new_beat > 0) and (self.last_heart_beat_time > 0)):
            # Prune data to last cycle
            
            # Deduce the fields that are needed
            cycle_fields = ['time', 'pressure_ventricle',
                            'pressure_arteries', 'volume_ventricle']
            if hasattr(self.hs, 'ener'):
                cycle_fields = cycle_fields + ['ener_flux_ATP_consumed']

            d_cycle = self.sim_data[cycle_fields]
            
            d_cycle = d_cycle[d_cycle['time'].between(
                self.last_heart_beat_time, self.data['time'])]
            
            self.data['stroke_volume'] = d_cycle['volume_ventricle'].max() - \
                d_cycle['volume_ventricle'].min()
            
            self.data['ejection_fraction'] = self.data['stroke_volume'] / \
                d_cycle['volume_ventricle'].max()
            
            self.data['stroke_work'] = self.return_stroke_work(d_cycle)

            self.data['mean_arterial_pressure'] = \
                d_cycle['pressure_arteries'].mean()
    
            if hasattr(self.hs, 'ener'):
                self.data['stroke_cost'] = \
                    -d_cycle['ener_flux_ATP_consumed'].sum() * time_step * \
                        self.hs.myof.implementation['delta_G_ATP']
            
                if (self.data['stroke_cost'] > 0):
                    self.data['efficiency'] = self.data['stroke_work'] / \
                        self.data['stroke_cost']
                else:
                    self.data['efficiency'] = np.nan
            
            

    def return_flows(self, v, time_step):
        """ return flows between compartments """

        # Calculate pressure in each compartment
        p = np.zeros(self.model['no_of_compartments'])
        for i in np.arange(len(p)-1):
            p[i] = (v[i]-self.data['s'][i]) / self.data['compliance'][i]
        p[-1] = self.return_lv_pressure(v[-1])

        # Add 1 for VAD
        f = np.zeros(self.model['no_of_compartments']+1)
        r = self.data['resistance']
        inert = self.data['inertance']
        last_f = self.data['f']
        
        for i in np.arange(len(p)):
            f[i] = (1.0 / (r[i] + inert[i]/time_step)) * \
                (p[i-1] - p[i] + (inert[i] * last_f[i] / time_step))

        # Check for VAD
        if (self.va):
            f[-1] = self.va.data['max_flow'] +\
                (p[-1] - p[0]) * self.va.data['pump_slope']

        # Add in the valves
        # Aortic
        if (p[-1] <= p[0]):
            f[0] = (p[-1] - p[0]) * \
                self.data['aortic_insufficiency_conductance']
        # Mitral
        if (p[-1] >= p[-2]):
            f[-2] = (p[-2]-p[-1]) * \
                self.data['mitral_insufficiency_conductance']

        return f

    def evolve_volumes(self, time_step, initial_v):
        """ Evolves volumes for a time-step """
        from scipy.integrate import solve_ivp

        def derivs(t, v):
            dv = np.zeros(self.model['no_of_compartments'])
            flows = self.return_flows(v, time_step)
            for i in np.arange(self.model['no_of_compartments']):
                if (i == (self.model['no_of_compartments']-1)):
                    dv[i] = flows[i] - flows[0] + flows[-1]
                else:
                    dv[i] = flows[i] - flows[i+1]
            return dv

        sol = solve_ivp(derivs, [0, time_step], initial_v)

        # Tidy up negative values
        y = sol.y[:, -1]
        y[np.nonzero(y < 0)] = 0
        # Rest goes in veins
        y[-2] = y[-2] + (self.data['blood_volume'] - np.sum(y))
        return y
