import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_force_array_per_cycle,steady_state_identifier
    from .implement import return_number_of_hs,return_lv_mass,update_data_holder
    from .display import display_growth
    def __init__(self,growth_params,initial_numbers_of_hs,data_buffer_size):

        growth = growth_params


        self.memory = int(growth.stress_signal.memory.cdata)
        self.f_cirt = float(growth.stress_signal.critical_total_stress.cdata)
        self.pas_cirt = float(growth.stress_signal.critical_passive_stress.cdata)

        #Concentric growth (ventricle_mass)
        self.ventricle_wall_volume = \
        float(growth.stress_signal.concenrtric_growth.ventricle_wall_volume.cdata)
        self.w_vol_0 = self.ventricle_wall_volume#float(growth.stress_signal.ventricle_wall_volume.cdata)
        #self.ventricle_wall_volume = self.w_vol_0
        self.G_w_vol = \
        float(growth.stress_signal.concenrtric_growth.G_wall_volume.cdata)
        self.tau_w_vol = \
        float(growth.stress_signal.concenrtric_growth.tau_wall_volume.cdata)
        self.delta_w_vol = [0.0]

        #Eccentric growth (number of hs in sereis)
        self.n_of_hs_0 = initial_numbers_of_hs
        self.G_n_hs = float(growth.stress_signal.eccenrtric_growth.G_number_of_hs.cdata)
        self.delta_n_hs = [0.0]

        #data
        self.data_buffer_size = data_buffer_size
        self.gr_time = 0.0
        self.data_buffer_index = 0
        self.gr_data = pd.DataFrame({'average_force':
                                            np.zeros(self.data_buffer_size),
                                    'cycle_counter':
                                            np.zeros(self.data_buffer_size),
                                    'ventricle_wall_volume':
                                            np.zeros(self.data_buffer_size),
                                    'lv_wall_thickness':
                                            np.zeros(self.data_buffer_size),
                                    'number_of_hs':
                                            np.zeros(self.data_buffer_size)})

        self.gr_data.at[0, 'ventricle_wall_volume'] = self.ventricle_wall_volume
        self.gr_data.at[0, 'number_of_hs'] = self.n_of_hs_0
