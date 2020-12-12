import numpy as np
import pandas as pd
from modules.MyoSim.half_sarcomere.myofilaments import myofilaments as myofilaments
from modules.MyoSim.half_sarcomere.membranes import membranes as membranes


class half_sarcomere():
    """Class for a half-sarcomere"""

    from .implement import update_simulation, update_data_holder
    from .display import display_fluxes
    #from .update_contractility import update_contractility

    def __init__(self, hs_params, data_buffer_size):

        self.hs_length = float(hs_params["initial_hs_length"][0])
        self.Ca_conc = 1.0e-9
        self.activation = 0.0

        # Pull of class parameters
        self.max_rate = float(hs_params["max_rate"][0])
        self.temperature = float(hs_params["temperature"][0])
        self.cb_number_density = float(hs_params["cb_number_density"][0])

        self.ATPase_activation = hs_params["ATPase_activation"][0]
        self.delta_G = float(hs_params["delta_energy"][0])
        self.N_A = float(hs_params["avagadro_number"][0])
        self.L0 = float(hs_params["reference_hs_length"][0])

        # Pull of membrane parameters
        membr_params = hs_params["membranes"]
        self.membr = membranes.membranes(membr_params, self)

        # Initialise hs_force, required for myofilament kinetics
        self.hs_force = 0

        # Pull off the mofilament_params
        myofil_params = hs_params["myofilaments"]
        self.myof = myofilaments.myofilaments(myofil_params, self)

        print(self.myof.cb_force)

        # Update forces
        self.hs_force = self.myof.cb_force + self.myof.pas_force
        print("hs_force: %f" % self.hs_force)

        # Create a pandas data structure to store data
        self.data_buffer_size = data_buffer_size
        self.hs_time = 0.0
        self.data_buffer_index = int(0)
        self.hs_data = pd.DataFrame({'hs_time' : np.zeros(self.data_buffer_size),
                                     'activation': np.zeros(self.data_buffer_size),
                                     'hs_length' : self.hs_length * np.ones(self.data_buffer_size),
                                     'hs_force' : np.zeros(self.data_buffer_size),
                                     'cb_force' : np.zeros(self.data_buffer_size),
                                     'pas_force' : np.zeros(self.data_buffer_size),
                                     'Ca_conc' : np.zeros(self.data_buffer_size)})

        # Add in specific fields for each scheme
        if (self.myof.kinetic_scheme == '3state_with_SRX' or self.myof.kinetic_scheme == '3state_with_SRX_and_exp_J4' ):
            # Initialise
            self.hs_data['M_OFF'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['M_ON'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['M_bound'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['n_off'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['n_on'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['n_bound'] = pd.Series(np.zeros(self.data_buffer_size))

            # Set first values
            self.hs_data.at[self.data_buffer_index, 'M_OFF'] = 1.0
            self.hs_data.at[self.data_buffer_index, 'M_ON'] = 0.0
            self.hs_data.at[self.data_buffer_index, 'M_bound'] = 0.0
            self.hs_data.at[self.data_buffer_index, 'n_off'] = 1.0
            self.hs_data.at[self.data_buffer_index, 'n_on'] = 0.0
            self.hs_data.at[self.data_buffer_index, 'n_bound'] = 0.0

            # Fluxes
            self.hs_data['J1'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['J2'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['J3'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['J4'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['Jon'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['Joff'] = pd.Series(np.zeros(self.data_buffer_size))
            self.hs_data['N_overlap'] = pd.Series(np.full(self.data_buffer_size,self.myof.n_overlap))


            #ATPase
            if self.ATPase_activation:
                self.ATPase = 0
                self.hs_data['ATPase'] = pd.Series(np.zeros(self.data_buffer_size))

        if (self.membr.kinetic_scheme == "Ten_Tusscher_2004"):
            self.hs_data['membrane_voltage'] = pd.Series(np.zeros(self.data_buffer_size))

        # Other stuff
        self.hs_data['cb_number_density'] = \
            pd.Series(np.zeros(self.data_buffer_size))
