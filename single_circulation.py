import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

try:
    import Python_MyoSim.half_sarcomere.half_sarcomere as hs
except:
    import sys
    sys.path.append('c:\\ken\\github\\campbellmusclelab\\python\\modules')
    import Python_MyoSim.half_sarcomere.half_sarcomere as hs


class single_circulation():
    """Class for a single ventricle circulation"""

    from .display import display_simulation

    def __init__(self, single_circulation_model):
        # Initialize output data
        self.output_file_string = \
            single_circulation_model.output_data.file_string.cdata
        self.output_buffer_size = \
            int(single_circulation_model.output_data.buffer_size.cdata)

        # Initialize circulation object using data from the sim_object
        circ_params = single_circulation_model.circulation

        self.no_of_compartments = int(circ_params.no_of_compartments.cdata)
        self.blood_volume = float(circ_params.blood.volume.cdata)

        self.aorta_resistance = float(circ_params.aorta.resistance.cdata)
        self.aorta_compliance = float(circ_params.aorta.compliance.cdata)

        self.arteries_resistance = float(circ_params.arteries.resistance.cdata)
        self.arteries_compliance = float(circ_params.arteries.compliance.cdata)

        self.veins_resistance = float(circ_params.veins.resistance.cdata)
        self.veins_compliance = float(circ_params.veins.compliance.cdata)

        self.ventricle_resistance = \
            float(circ_params.ventricle.resistance.cdata)
        self.ventricle_wall_volume = \
            float(circ_params.ventricle.wall_volume.cdata)
        self.ventricle_slack_volume = \
            float(circ_params.ventricle.slack_volume.cdata)

        # Initialise the resistance and compliance arrays for calcuations
        self.resistance = np.array([self.aorta_resistance,
                                    self.arteries_resistance,
                                    self.veins_resistance,
                                    self.ventricle_resistance])
        self.compliance = np.array([self.aorta_compliance,
                                    self.arteries_compliance,
                                    self.veins_compliance,
                                    0])

        # Pull off the half_sarcomere parameters
        hs_params = single_circulation_model.half_sarcomere
        self.hs = hs.half_sarcomere(hs_params, self.output_buffer_size)

        # Deduce the hsl where force is zero and set the hsl to that length
        slack_hsl = self.hs.myof.return_hs_length_for_force(0.0)
        self.hs.update_simulation(0.0,(slack_hsl - self.hs.hs_length), 0.0)

        # Deduce the slack circumference of the ventricle and set that
        self.lv_circumference = \
            self.return_lv_circumference(self.ventricle_slack_volume)

        # Set the initial volumes
        self.v = np.array([0, 0,
                           self.blood_volume - self.ventricle_slack_volume,
                           self.ventricle_slack_volume])

        # Deduce the pressures
        self.p = np.zeros(self.no_of_compartments)
        for i in np.arange(0, self.no_of_compartments-1):
            self.p[i] = self.v[i] / self.compliance[i]
        self.p[-1] = self.return_lv_pressure(self.v[-1])

        # Create a pandas data structure to store data
        self.sim_time = 0.0
        self.data_buffer_index = 0
        self.data = pd.DataFrame({'time': np.zeros(self.output_buffer_size),
                                  'pressure_aorta':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_arteries':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_veins':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_ventricle':
                                      np.zeros(self.output_buffer_size),
                                  'volume_aorta':
                                      np.zeros(self.output_buffer_size),
                                  'volume_arteries':
                                      np.zeros(self.output_buffer_size),
                                  'volume_veins':
                                      np.zeros(self.output_buffer_size),
                                  'volume_ventricle':
                                      np.zeros(self.output_buffer_size)})

        # Store the first values
        self.data.at[0, 'pressure_aorta'] = self.p[0]
        self.data.at[0, 'pressure_arteries'] = self.p[1]
        self.data.at[0, 'pressure_veins'] = self.p[2]
        self.data.at[0, 'pressure_ventricle'] = self.p[3]

        self.data.at[0, 'volume_aorta'] = self.v[0]
        self.data.at[0, 'volume_arteries'] = self.v[1]
        self.data.at[0, 'volume_veins'] = self.v[2]
        self.data.at[0, 'volume_ventricle'] = self.v[3]

    def derivs(self, t, v):
        # returns dv, derivative of volume
        p = np.zeros(self.no_of_compartments)

        # Calculate pressure in each compartment
        vi = range(self.no_of_compartments-1)
        for x in vi:
            p[x] = v[x] / self.compliance[x]
        p[-1] = self.return_lv_pressure(v[-1])

        # Calculate volume changes
        dv = np.zeros(self.no_of_compartments)

        # Aorta
        # Allow for valve
        if (p[-1] > p[0]):
            dv[0] = dv[0] + (p[-1]-p[0])/self.resistance[0]
        dv[0] = dv[0] - (p[0]-p[1]) / self.resistance[1]

        # Arteries are easier
        dv[1] = dv[1] + \
            ((p[0]-p[1]) / self.resistance[1]) - \
            ((p[1]-p[2]) / self.resistance[2])

        # Veins
        dv[2] = dv[2] + \
            ((p[1]-p[2]) / self.resistance[2])
        # Allow for valve
        if (p[2] > p[-1]):
            dv[2] = dv[2] - \
                (p[2]-p[-1]) / self.resistance[-1]

        # Ventricle
        # Allow for valve
        if (p[2] > p[-1]):
            dv[-1] = dv[-1] + \
                (p[2] - p[-1]) / self.resistance[-1]
        if (p[-1] > p[0]):
            dv[-1] = dv[-1] - \
                (p[-1]-p[0]) / self.resistance[0]

        return dv

    def implement_time_step(self, time_step, activation):
        """ Steps circulatory system forward in time """

        # Update the half-sarcomere
        self.hs.update_simulation(time_step, 0.0, activation, 1)

        # steps solution forward in time
        sol = solve_ivp(self.derivs, [0, time_step], self.v)
        self.v = sol.y[:, -1]
        print(self.v)

        print("sum of volumes: %f" % np.sum(self.v))

        # Implements the length change on the half-sarcomere
        new_lv_circumference = self.return_lv_circumference(self.v[-1])
        delta_hsl = self.hs.hs_length *\
            ((new_lv_circumference / self.lv_circumference) - 1.0)
        self.hs.update_simulation(0.0, delta_hsl, 0.0, 1)
        self.lv_circumference = new_lv_circumference
        print("lv_circumference %f" % self.lv_circumference)
        
        print("delta_hsl %f" % delta_hsl)
        

        # Update the pressures
        vi = range(self.no_of_compartments-1)
        for x in vi:
            self.p[x] = self.v[x] / self.compliance[x]
        self.p[-1] = self.return_lv_pressure(self.v[-1])

        # Update data structures
        if (time_step > 0.0):
            self.sim_time = self.sim_time + time_step
            self.data_buffer_index = self.data_buffer_index + 1
            self.data.at[self.data_buffer_index, 'time'] = self.sim_time
            self.data.at[self.data_buffer_index, 'pressure_aorta'] = self.p[0]
            self.data.at[self.data_buffer_index, 'pressure_arteries'] = self.p[1]
            self.data.at[self.data_buffer_index, 'pressure_veins'] = self.p[2]
            self.data.at[self.data_buffer_index, 'pressure_ventricle'] = self.p[-1]
            self.data.at[self.data_buffer_index, 'volume_aorta'] = self.v[0]
            self.data.at[self.data_buffer_index, 'volume_arteries'] = self.v[1]
            self.data.at[self.data_buffer_index, 'volume_veins'] = self.v[2]
            self.data.at[self.data_buffer_index, 'volume_ventricle'] = self.v[-1]

    def return_lv_circumference(self, lv_volume):
        lv_circum = np.power((6*np.power(np.pi,2.0) * 
                              (lv_volume + 
                                   (self.ventricle_wall_volume / 2.0))),
                                    (1.0 / 3.0))
        return lv_circum

    def return_lv_pressure(self, lv_volume):
        # Deduce new lv circumference
        new_lv_circumference = self.return_lv_circumference(lv_volume)

        # Deduce relative change in hsl
        delta_hsl = self.hs.hs_length * \
            ((new_lv_circumference / self.lv_circumference) - 1.0)

        # Estimate the force produced at the new length
        f = self.hs.myof.check_myofilament_forces(delta_hsl)
        total_force = f['total_force']

        return total_force * (-1 +
            np.power((1.0 + (self.ventricle_wall_volume / lv_volume)),(2/3)))

    def step_solution(self, dt):
        # steps solution forward in time
        sol = solve_ivp(self.derivs, [0, dt], self.v)
        self.v = sol.y[:, -1]

    def run_simulation(self, dt, no_of_time_points, max_ventricular_pressure):
        t = np.zeros(1)
        v = self.v

        j = 0

        x = range(no_of_time_points)
        for i in x:
            if ((i % 250) == 0):
                j = 50

            if (j > 0):
                j = j - 1
                self.ventricular_pressure = max_ventricular_pressure
            else:
                self.ventricular_pressure = 0

            print("i: %d" % i)
            self.step_solution(dt)
            t = np.vstack((t, t[-1]+dt))
            v = np.vstack((v, self.v))

        sim_output = {'t': t, 'v': v}
        return sim_output
