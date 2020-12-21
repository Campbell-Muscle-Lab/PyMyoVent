import numpy as np
import pandas as pd
from .myofilaments import myofilaments as myof
from .membranes import membranes as membr


class half_sarcomere():
    """Class for a half-sarcomere"""

    from .implement import update_simulation, update_data_holder
    from .display import display_fluxes
    #from .update_contractility import update_contractility

    def __init__(self, hs_struct):
        
        self.hs_model = dict()
        self.hs_length = hs_struct['initial_hs_length']
        self.Ca_conc = 1e-9
        self.activation = 0

        # Pull of membrane parameters
        membrane_struct = hs_struct["membranes"]
        self.membr = membr.membranes(membrane_struct, self)

        # Initialise hs_force, required for myofilament kinetics
        self.hs_force = 0

        # Pull off the mofilament_params
        myofil_struct = hs_struct["myofilaments"]
        self.myof = myof.myofilaments(myofil_struct, self)
        
        # Set hs fields
        self.data_fields = ['activation', 'Ca_conc', 'hs_length',
                            'hs_force', 'cb_force', 'pas_force']

        # print(self.myof.cb_force)

        # # Update forces
        # self.hs_force = self.myof.cb_force + self.myof.pas_force
        # print("hs_force: %f" % self.hs_force)

        # # Create a pandas data structure to store data
        # self.data_buffer_size = data_buffer_size
        # self.hs_time = 0.0
        # self.data_buffer_index = int(0)
        # self.hs_data = pd.DataFrame({'hs_time' : np.zeros(self.data_buffer_size),
        #                              'activation': np.zeros(self.data_buffer_size),
        #                              'hs_length' : self.hs_length * np.ones(self.data_buffer_size),
        #                              'hs_force' : np.zeros(self.data_buffer_size),
        #                              'cb_force' : np.zeros(self.data_buffer_size),
        #                              'pas_force' : np.zeros(self.data_buffer_size),
        #                              'Ca_conc' : np.zeros(self.data_buffer_size)})

        # # Add in specific fields for each scheme
        # if (self.myof.kinetic_scheme == '3state_with_SRX'):
        #     # Initialise
        #     self.hs_data['M_OFF'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['M_ON'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['M_bound'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['n_off'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['n_on'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['n_bound'] = pd.Series(np.zeros(self.data_buffer_size))

        #     # Set first values
        #     self.hs_data.at[self.data_buffer_index, 'M_OFF'] = 1.0
        #     self.hs_data.at[self.data_buffer_index, 'M_ON'] = 0.0
        #     self.hs_data.at[self.data_buffer_index, 'M_bound'] = 0.0
        #     self.hs_data.at[self.data_buffer_index, 'n_off'] = 1.0
        #     self.hs_data.at[self.data_buffer_index, 'n_on'] = 0.0
        #     self.hs_data.at[self.data_buffer_index, 'n_bound'] = 0.0

        #     # Fluxes
        #     self.hs_data['J1'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['J2'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['J3'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['J4'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['Jon'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['Joff'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['N_overlap'] = pd.Series(np.full(self.data_buffer_size,self.myof.n_overlap))

        #     self.hs_data['r4_N10'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N9'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N8'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N7'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N6'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N5'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N4'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N3'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N2'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_N1'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_0'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P1'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P2'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P3'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P4'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P5'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P6'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P7'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P8'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P9'] = pd.Series(np.zeros(self.data_buffer_size))
        #     self.hs_data['r4_P10'] = pd.Series(np.zeros(self.data_buffer_size))

        #     #ATPase
        #     if self.ATPase_activation:
        #         self.ATPase = 0
        #         self.hs_data['ATPase'] = pd.Series(np.zeros(self.data_buffer_size))

        # if (self.membrane.kinetic_scheme == "Ten_Tusscher_2004"):
        #     self.hs_data['membrane_voltage'] = pd.Series(np.zeros(self.data_buffer_size))

        # # Other stuff
        # self.hs_data['cb_number_density'] = \
        #     pd.Series(np.zeros(self.data_buffer_size))
