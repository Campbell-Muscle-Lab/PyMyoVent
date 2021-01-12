
import json
import numpy as np
import pandas as pd

from .half_sarcomere import half_sarcomere as hs
from .heart_rate import heart_rate as hr
from .baroreflex import baroreflex as br
from .growth import growth as gr

from protocol import protocol as prot
from sim_options import sim_options as sim_opt
from output_handler import output_handler as oh


class single_ventricle_circulation():

    """Class for a single ventricle circulation"""

    def __init__(self, model_json_file_string):

        # Check for file
        if (model_json_file_string == []):
            print('No model file specified. Cannot create model')
            return

        # Status
        print('Initialising single_ventricle_circulation from %s' %
              model_json_file_string)

        # Load the model as a dict
        with open(model_json_file_string, 'r') as f:
            sc_model = json.load(f)

        # Create a model dict for things that do not change
        self.model = dict()
        # And a data dict for things that might
        self.data = dict()

        # Initialize the circulation object using data from the json file
        circ_model = sc_model["circulation"]

        # Store the number of compartments
        self.model['no_of_compartments'] = len(circ_model['compartments'])

        # Store blood volume
        self.data['blood_volume'] = circ_model['blood_volume']

        vessels_list = []
        for comp in circ_model['compartments']:
            if not (comp['name'] == 'ventricle'):
                n = comp['name']
                vessels_list.append(comp['name'])
                for t in ['resistance', 'compliance', 'slack_volume']:
                    n = ('%s_%s') % (comp['name'], t)
                    self.data[n] = comp[t]
            else:
                # Ventricle
                self.data['ventricle_resistance'] = comp['resistance']
                self.data['ventricle_slack_volume'] = comp['slack_volume']
                self.data['ventricle_wall_volume'] = comp['wall_volume']
                self.model['ventricle_wall_density'] = comp['wall_density']

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
        vessels_list.append('ventricle')
        self.model['compartment_list'] = vessels_list
        for v in self.model['compartment_list']:
            r = self.data[('%s_resistance' % v)]
            self.data['resistance'].append(r)
        self.data['resistance'] = np.array(self.data['resistance'])

        # Add in mitral insuficient resistance
        self.data['mitral_insufficiency_resistance'] = np.inf

        # Create a heart-rate object
        self.hr = hr.heart_rate(sc_model['heart_rate'])

        # Pull off the half_sarcomere parameters and make a half-sarcomere
        self.hs = hs.half_sarcomere(sc_model['half_sarcomere'])

        # Deduce the hsl where force is zero and set the hsl to that length
        self.hs.data['slack_hsl'] = \
            self.hs.myof.return_hs_length_for_force(0.0)
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

        # Allocate space for flows
        self.data['f'] = np.zeros(self.model['no_of_compartments'])
        if (self.model['no_of_compartments'] == 7):
            self.model['flow_list'] = \
                ['flow_ventricle_to_aorta', 'flow_aorta_to_arteries',
                 'flow_arteries_to_arterioles', 'flow_arterioles_to_capillaries',
                 'flow_capillaries_to_venules', 'flow_venules_to_veins',
                 'flow_veins_to_ventricle']
            for f in self.model['flow_list']:
                self.data[f] = 0

        # Set the heart rate
        self.data['heart_rate'] = self.hr.return_heart_rate()

        # If requried, create the baroreceptor
        self.data['baroreflex_active'] = 0
        self.data['baroreflex_setpoint'] = 0
        if ('baroreflex' in sc_model):
            self.br = br.baroreflex(sc_model['baroreflex'],
                                    self,
                                    self.data['pressure_arteries'])
            self.data['baroreflex_setpoint'] = self.br.data['baro_b_setpoint']
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

        # Create a sim_options object
        self.so = []

        # Add in a temp
        self.data['test'] = 0

        # Set the time
        self.data['time'] = 0

    def rebuild_from_perturbations(self):
        """ builds reistance array"""

        for i, v in enumerate(self.model['compartment_list']):
            r = self.data[('%s_resistance' % v)]
            self.data['resistance'][i] = r

        for i, v in enumerate(self.model['compartment_list']):
            if (i < (self.model['no_of_compartments']-1)):
                c = self.data[('%s_compliance' % v)]
                self.data['compliance'][i] = c

        self.br.data['baro_b_setpoint'] = self.data['baroreflex_setpoint']

    def create_data_structure(self):
        """ creates a data frame from the data dicts of each component """

        self.sim_data = pd.DataFrame()
        z = np.zeros(self.prot.data['no_of_time_steps'])

        data_fields = list(self.data.keys()) + \
            list(self.hr.data.keys()) + \
            list(self.hs.data.keys()) + \
            list(self.hs.memb.data.keys()) + \
            list(self.hs.myof.data.keys())

        # Add in fields from optional modules
        if (self.br):
            data_fields = data_fields + list(self.br.data.keys())
        if (self.gr):
            data_fields = data_fields + list(self.gr.data.keys())

        for f in data_fields:
            s = pd.Series(data=z, name=f)
            self.sim_data = pd.concat([self.sim_data, s], axis=1)

    def run_simulation(self,
                       protocol_file_string=[],
                       output_handler_file_string=[],
                       sim_options_file_string=[]):
        """ Run the simulation """

        # Load the protocol
        if (protocol_file_string == []):
            print("No protocol_file_string. Exiting")
            return
        self.prot = prot.protocol(protocol_file_string)

        # Now that you know how many time-points there are,
        # create the data structure
        self.create_data_structure()

        # Check for sim_options
        if (sim_options_file_string):
            self.so = sim_opt.sim_options(sim_options_file_string,
                                          self.prot.data['time_step'],
                                          self)

        # Step through the simulation
        self.t_counter = 0
        for i in np.arange(self.prot.data['no_of_time_steps']):
            self.implement_time_step(self.prot.data['time_step'])

        # Load the output_handler and process
        if (output_handler_file_string == []):
            print("No output_structure_file_string. Exiting")
            return
        cb_dump_file_string = []
        if ('cb_dump_file_string' in self.so.data):
            cb_dump_file_string = self.so.data['cb_dump_file_string']
        self.oh = oh.output_handler(output_handler_file_string,
                                    self.sim_data,
                                    cb_dump_file_string)

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
            d['ejection_fraction'] = d['stroke_volume'] / \
                d['volume_ventricle_max']
            d['heart_rate'] = self.data['heart_rate']
            d['cardiac_output'] = d['stroke_volume'] * d['heart_rate']
            d['hs_length_max'] = self.temp_data['hs_length'].max()
            d['fractional_shortening'] = \
                (d['hs_length_max'] - self.temp_data['hs_length'].min()) / \
                d['hs_length_max']
            d['pressure_artery_max'] = \
                self.temp_data['pressure_arteries'].max()
            d['pressure_artery_min'] = \
                self.temp_data['pressure_arteries'].min()
            d['pressure_veins_mean'] = \
                self.temp_data['pressure_veins'].mean()
            d['volume_veins_proportion'] = \
                self.temp_data['volume_veins'].mean() / \
                self.data['blood_volume']
            d['pas_force_mean'] = self.temp_data['pas_force'].mean()
            d['n_hs'] = self.data['n_hs']
            d['mitral_insufficiency_resistance'] = \
                self.data['mitral_insufficiency_resistance']

        return d

    def implement_time_step(self, time_step):
        """ Implements time step """
        self.data['time'] = self.data['time'] + time_step

        # Display progress
        if (self.t_counter % 1000 == 0):
            print('Sim time (s): %.0f  %.0f%% complete' %
                  (self.data['time'],
                   100*self.t_counter/self.prot.data['no_of_time_steps']))
            system_values = self.return_system_values()
            print(json.dumps(system_values, indent=4))
            if (self.gr):
                print('growth_eccentric_g: %g  growth_eccentric_c: %g' %
                      (self.gr.data['growth_eccentric_g'],
                       self.gr.data['growth_eccentric_c']))
                print('growth_concentric_g: %g  growth_concentric_c: %g' %
                      (self.gr.data['growth_concentric_g'],
                       self.gr.data['growth_concentric_c']))

        # Check and implement perturbations
        for p in self.prot.perturbations:
            # Implement step_change perturbations
            if ('new_value' in p.data):
                if (self.t_counter == p.data['t_start_ind']):
                    self.data[p.data['variable']] = p.data['new_value']
            else:
                if((self.t_counter >= p.data['t_start_ind']) and
                   (self.t_counter < p.data['t_stop_ind'])):
                    self.data[p.data['variable']] += p.data['increment']

        self.rebuild_from_perturbations()

        # Check for baroreflex and implement
        if (self.br):
            self.data['baroreflex_active'] = 0
            for b in self.prot.baro_activations:
                if ((self.t_counter >= b.data['t_start_ind']) and
                        (self.t_counter < b.data['t_stop_ind'])):
                    self.data['baroreflex_active'] = 1

            self.br.implement_time_step(self.data['pressure_arteries'],
                                        time_step,
                                        reflex_active=self.data['baroreflex_active'])

        # Check for growth module and implement
        if (self.gr):
            self.data['growth_active'] = 0
            for g in self.prot.growth_activations:
                if ((self.t_counter >= g.data['t_start_ind']) and
                        (self.t_counter < g.data['t_stop_ind'])):
                    self.data['growth_active'] = 1

            self.gr.implement_time_step(time_step,
                                        growth_active=self.data['growth_active'])

        # Run the hr module
        activation = self.hr.implement_time_step(time_step)
        for f in list(self.hr.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hr.data[f]

        # Advance half_sarcomere forward in time
        # First update the kinetic steps
        self.hs.update_simulation(time_step, 0, activation)

        # Now evolve volumes
        self.evolve_volumes(time_step)

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
        self.update_data()
        self.hs.update_data()

        # Now update the sim_data
        for f in list(self.data.keys()):
            if (f not in ['p', 'v', 's', 'compliance', 'resistance', 'f']):
                self.sim_data.at[self.t_counter, f] = self.data[f]
        for f in list(self.hs.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.data[f]
        for f in list(self.hs.memb.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.memb.data[f]
        for f in list(self.hs.myof.data.keys()):
            self.sim_data.at[self.t_counter, f] = self.hs.myof.data[f]
        if (self.br):
            for f in list(self.br.data.keys()):
                self.sim_data.at[self.t_counter, f] = self.br.data[f]
        if (self.gr):
            for f in list(self.gr.data.keys()):
                self.sim_data.at[self.t_counter, f] = self.gr.data[f]

        # Dump cb distributions if required
        if ('cb_dump_file_string' in self.so.data):
            if ((self.t_counter >=
                 self.so.data['cb_dump_t_start_ind']) and
                (self.t_counter <
                 self.so.data['cb_dump_t_stop_ind'])):
                self.so.append_cb_distribution(self.data['time'])

        # Update the t counter for the next step
        self.t_counter = self.t_counter + 1

    def update_data(self):
        # Update data for the simulation

        # Update data for the heart-rate
        self.data['heart_rate'] = self.hr.return_heart_rate()

        flows = self.return_flows(self.data['v'])
        for i, f in enumerate(self.model['flow_list']):
            self.data[f] = flows[i]

        for i, v in enumerate(self.model['compartment_list']):
            self.data['pressure_%s' % v] = self.data['p'][i]
            self.data['volume_%s' % v] = self.data['v'][i]

    def return_lv_pressure(self, chamber_volume):
        """ return pressure for a given volume """
        from scipy.constants import mmHg as mmHg_in_pascals

        # Estimate the force produced at the new length
        new_lv_circumference = self.return_lv_circumference(chamber_volume)
        new_hs_length = 1e9 * new_lv_circumference / self.data['n_hs']
        delta_hsl = new_hs_length - self.hs.data['hs_length']
        f = self.hs.myof.check_myofilament_forces(delta_hsl)
        total_force = f['total_force']

        internal_r = self.return_internal_radius_for_chamber_volume(
            chamber_volume)

        wall_thickness = self.return_wall_thickness(chamber_volume)

        # Pressure from Laplaces lawNo documentation available
        # https://www.annalsthoracicsurgery.org/action/showPdf?pii=S0003-4975%2810%2901981-8
        if (internal_r < 1e-6):
            P_in_pascals = 0
        else:
            P_in_pascals = ((total_force * wall_thickness *
                             (2.0 + (wall_thickness / internal_r))) /
                            internal_r)
        P_in_mmHg = P_in_pascals / mmHg_in_pascals

        return P_in_mmHg

    def return_wall_thickness(self, chamber_volume):
        """ returns wall thickness given internal_r """
        if (chamber_volume < 0):
            chamber_volume = 0

        # Note that volumes are in liters, dimensions are in m
        internal_r = self.return_internal_radius_for_chamber_volume(
                        chamber_volume)

        t  = np.power(0.001 * (chamber_volume +
                               self.data['ventricle_wall_volume']) /
                      ((2.0 / 3.0) * np.pi), (1.0 / 3.0)) - \
                        internal_r

        return t


    def return_lv_circumference(self, chamber_volume):
        # Based on 2 pi * (internal r + 0.5 * wall thickness)
        # volume is in liters, circumference is in meters

        if (chamber_volume < 0.0):
            chamber_volume = 0
            
        wall_thickness = self.return_wall_thickness(chamber_volume)

        lv_circum = (2.0 * np.pi *
                     (self.return_internal_radius_for_chamber_volume(
                         chamber_volume) +
                      (0.5 * wall_thickness)))

        return lv_circum


    def return_internal_radius_for_chamber_volume(self, chamber_volume):
        # Returns internal radius in meters for chamber volume in liters
        if (chamber_volume < 0):
            chamber_volume = 0

        r = np.power((3.0 * 0.001 * chamber_volume) / (2.0 * np.pi), (1.0/3.0))

        return r

    def return_flows(self, v):
        """ return flows between compartments """

        # Calculate pressure in each compartment
        p = np.zeros(self.model['no_of_compartments'])
        for i in np.arange(len(p)-1):
            p[i] = (v[i]-self.data['s'][i]) / self.data['compliance'][i]
        p[-1] = self.return_lv_pressure(v[-1])

        f = np.zeros(self.model['no_of_compartments'])
        r = self.data['resistance']
        for i in np.arange(len(p)):
            f[i] = (p[i-1]-p[i]) / r[i]

        # Add in the valves
        # Aortic
        if (p[-1] <= p[0]):
            f[0] = 0
        # Mitral
        if (p[-1] >= p[-2]):
            f[-1] = (p[-2]-p[-1]) / \
                self.data['mitral_insufficiency_resistance']

        return f

    def evolve_volumes(self, time_step):
        """ Evolves volumes for a time-step """
        from scipy.integrate import solve_ivp

        def derivs(t, v):
            dv = np.zeros(self.model['no_of_compartments'])
            flows = self.return_flows(v)
            for i in np.arange(self.model['no_of_compartments']):
                if (i == (self.model['no_of_compartments']-1)):
                    dv[i] = flows[i] - flows[0]
                else:
                    dv[i] = flows[i] - flows[i+1]
            return dv

        sol = solve_ivp(derivs, [0, time_step], self.data['v'])

        # Tidy up negative values
        y = sol.y[:, -1]
        y[np.nonzero(y < 0)] = 0
        # Rest goes in veins
        y[-2] = y[-2] + (self.data['blood_volume'] - np.sum(y))
        self.data['v'] = y