import numpy as np

class membranes():
    """ Class for membranes """

    def __init__(self, membrane_params, parent_half_sarcomere):
        self.parent_hs = parent_half_sarcomere;

        self.kinetic_scheme = membrane_params["kinetic_scheme"]

        # Set up the rates and the y vector which are kinetics specific
        if (self.kinetic_scheme == "simple_2_compartment"):
            self.Ca_content = membrane_params['Ca_content']
            self.k_leak = membrane_params['k_leak']
            self.k_act = membrane_params['k_act']
            self.k_serca = membrane_params['k_serca']
            self.t_open = membrane_params['t_open']

            self.y = np.zeros(2)
            self.y[1] = self.Ca_content
            
            self.on_left = 0

            self.myofilament_Ca_conc = self.y[0]
