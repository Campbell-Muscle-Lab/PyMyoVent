import numpy as np
from scipy.integrate import solve_ivp

try:
    import Python_MyoSim.half_sarcomere.half_sarcomere as hs
except:
    import sys
    sys.path.append('c:\\ken\\github\\campbellmusclelab\\python\\modules')
    import Python_MyoSim.half_sarcomere.half_sarcomere as hs


class single_circulation():
    """Class for a single ventricle circulation"""

    def __init__(self):
        self.blood_volume = 0.5         # blood volume in liters
        self.no_of_compartments = 4     # aorta, arteries, veins, ventricle
        self.resistance = np.array([3, 50, 75, 6])
        self.compliance = np.array([0.001, 0.005, 0.3, 0.001])
        self.p = np.zeros(self.no_of_compartments)
        self.v = np.array([0, 0, self.blood_volume, 0])
        self.ventricular_pressure = 0
        self.ventricular_slack_volume = 100
        self.ventricular_stiffness = 1

        self.hs = hs.half_sarcomere()

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
