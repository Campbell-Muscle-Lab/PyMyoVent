import numpy as np
from scipy.integrate import solve_ivp

from functools import partial

from .Ten_Tusscher_2004 import computeRates_with_activation as \
tt_computeRates_with_activation
from .Ten_Tusscher_2004 import initConsts_with_adjustments as \
tt_initConsts_with_adjustments
from .Ten_Tusscher_2004 import computeRates as tt_computeRates
from .Ten_Tusscher_2004 import initConsts as tt_initConsts
from .Shannon_Bers_2004 import initConsts as sb_initConsts
from .Shannon_Bers_2004 import computeRates as sb_computeRates
from .Shannon_Bers_2004 import solve_system as sb_solve_system
from .Grandi_2009 import initConsts as g_initConsts
from .Grandi_2009 import computeRates as g_coputeRates

class membranes():
    """ Class for membranes """

    def __init__(self, membrane_params, parent_half_sarcomere):
        self.parent_hs = parent_half_sarcomere;

        self.kinetic_scheme = membrane_params["kinetic_scheme"][0]

        # Set up the rates and the y vector which are kinetics specific
        if (self.kinetic_scheme == "simple_2_compartment"):
            self.Ca_content = float(membrane_params["Ca_content"][0])
            self.k_leak = float(membrane_params["k_leak"][0])
            self.k_act = float(membrane_params["k_act"][0])
            self.k_serca = float(membrane_params["k_serca"][0])

            self.y = np.zeros(2)
            self.y[1] = self.Ca_content

            self.myofilament_Ca_conc = self.y[0]

        if (self.kinetic_scheme == "Ten_Tusscher_2004"):
            # Adjust membrane factors
            membrane_factors = dict();
            membrane_factors['g_to'] = \
                float(membrane_params["g_to_factor"][0]) #const 20
            membrane_factors['g_Kr'] = \
                float(membrane_params["g_Kr_factor"][0]) #const 14
            membrane_factors['g_Ks'] = \
                float(membrane_params["g_Ks_factor"][0]) #const 15
            membrane_factors['Ca_a_rel'] = \
                float(membrane_params["Ca_a_rel_factor"][0]) #const 34
            membrane_factors['Ca_V_leak'] = \
                float(membrane_params["Ca_V_leak_factor"][0]) #const 38
            membrane_factors['Ca_Vmax_up'] = \
                float(membrane_params["Ca_Vmax_up_factor"][0]) #const 39
            membrane_factors['g_CaL'] = \
                float(membrane_params["g_CaL_factor"][0]) #const 18
            (self.y, self.constants) = \
                tt_initConsts()
                #tt_initConsts_with_adjustments(membrane_factors)

            # Ten_Tusscher model assumese Ca_conc is in mM
            self.myofilament_Ca_conc = 0.001*self.y[3]

        if (self.kinetic_scheme=="Shannon_Bers_2004"):

            (self.y, self.constants) = sb_initConsts()
            self.myofilament_Ca_conc = 0.001*self.y[32]

        if (self.kinetic_scheme=="Grandi_2009"):
            (self.y, self.constants)=g_initConsts()





    def evolve_kinetics(self, time_step, activation):
        """ evolves kinetics """

        if (self.kinetic_scheme == "simple_2_compartment"):
            # Pull out the v vector
            y = self.y

            def derivs(t, y):
                dy = np.zeros(np.size(y))
                dy[0] = (self.k_leak + activation * self.k_act) * y[1] - \
                        self.k_serca * y[0]
                dy[1] = -dy[0]
                return dy

            # Evolve
            sol = solve_ivp(derivs, [0, time_step], y, method = 'RK23')
            self.y = sol.y[:, -1]
            self.myofilament_Ca_conc = self.y[0]

        if (self.kinetic_scheme == "Ten_Tusscher_2004"):

            # Ten_Tusscher model assumes time step is in ms
            sol = solve_ivp(partial(tt_computeRates_with_activation,
                                    constants=self.constants,
                                    activation=activation),
                            [0, 1000*time_step], self.y,
                            method='BDF')
            #sol = solve_ivp(partial(tt_computeRates,
            #                        constants=self.constants,activation=activation),
            #                [0, 1000*time_step], self.y,
            #                method='BDF')
            #sol = solve_ivp(partial(tt_computeRates,
            #                        constants=self.constants),[0, 1000*time_step], self.y,method='BDF')
            self.y = sol.y[:, -1]
            # Ten_Tusscher model assumese Ca_conc is in mM
            self.myofilament_Ca_conc = 0.001*self.y[3]

        if (self.kinetic_scheme=="Shannon_Bers_2004"):

            sol=solve_ivp(partial(sb_computeRates,
                                    constants=self.constants,activation=activation),\
                                    [0, 1000*time_step], self.y,
                                    method='BDF')
            self.y = sol.y[:, -1]
            # Shannon model assumese Ca_conc is in mM
            self.myofilament_Ca_conc = 0.001*self.y[32]

        if (self.kinetic_scheme=="Grandi_2009"):
            sol=solve_ivp(partial(g_computeRates,
                                    constants=self.constants,activation=activation),\
                                    [0, 1000*time_step], self.y,
                                    method='BDF')
            #(self.voi, self.states, self.algebraic) = sb_solve_system()
            self.y = sol.y[:, -1]
            # Grandi model assumese Ca_conc is in mM
            self.myofilament_Ca_conc = 0.001*self.y[32]
