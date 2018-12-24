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

    def __init__(self,single_circulation_model):

#        # Initialize output data
        print(single_circulation_model)
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

        print('%d' % self.blood_volume)
        print("aorta resistance: %f" % self.aorta_resistance)

        # Initialise the resistance and compliance arrays for calcuations
        self.resistance = np.array([self.aorta_resistance,
                                    self.arteries_resistance,
                                    self.veins_resistance,
                                    self.ventricle_resistance])
        self.compliance = np.array([self.aorta_compliance,
                                    self.arteries_compliance,
                                    self.veins_compliance,
                                    0])
        self.p = np.zeros(self.no_of_compartments)
        self.v = np.array([0, 0, self.blood_volume, 0])

        self.ventricular_pressure = 0
        self.ventricular_slack_volume = 100
        self.ventricular_stiffness = 1

        # Pull of the half_sarcomere parameters
        hs_params = single_circulation_model.half_sarcomere
        self.hs = hs.half_sarcomere(hs_params, self.output_buffer_size)

        # Create a pandas data structure to store data
        self.sim_time = 0.0
        self.data_buffer_index = int(0)
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

    def derivs(self, t, v):
        # returns dv, derivative of volume
        p = np.zeros(self.no_of_compartments)

        # Calculate pressure in each compartment
        vi = range(self.no_of_compartments-1)
        for x in vi:
            p[x] = v[x] / self.compliance[x]
        p[-1] = self.ventricular_pressure
        if (v[-1] > self.ventricular_slack_volume):
            p[-1] = p[-1] + \
                (v[-1]-self.ventricular_slack_volume) * \
                self.ventricular_stiffness

        # display
        vi = range(self.no_of_compartments)
#        for x in vi:
#            print("x: %d p: %f v: %f" % (x, p[x], self.v[x]))

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
        self.hs.implement_time_step(time_step, 0.0, activation)

        # steps solution forward in time
        sol = solve_ivp(self.derivs, [0, time_step], self.v)
        self.v = sol.y[:, -1]

        # Update data structures
        self.sim_time = self.sim_time + time_step
        self.data_buffer_index = self.data_buffer_index + int(1)
        self.data.at[self.data_buffer_index, 'time'] = self.sim_time
        self.data.at[self.data_buffer_index, 'pressure_aorta'] = self.p[0]
        self.data.at[self.data_buffer_index, 'pressure_arteries'] = self.p[1]
        self.data.at[self.data_buffer_index, 'pressure_veins'] = self.p[2]
        self.data.at[self.data_buffer_index, 'pressure_ventricle'] = self.p[3]
        self.data.at[self.data_buffer_index, 'volume_aorta'] = self.v[0]
        self.data.at[self.data_buffer_index, 'volume_arteries'] = self.v[1]
        self.data.at[self.data_buffer_index, 'volume_veins'] = self.v[2]
        self.data.at[self.data_buffer_index, 'volume_ventricle'] = self.v[3]

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
