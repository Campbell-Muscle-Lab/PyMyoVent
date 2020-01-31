import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_lv_wall_thickness,return_lv_wall_thickness_strain,\
    return_number_of_hs_strain
    from .implement import return_number_of_hs,return_lv_mass,update_data_holder
    from .display import display_growth
    def __init__(self,growth_params,initial_numbers_of_hs,data_buffer_size):

        growth = growth_params

        start_time_percentage = int(growth["start_time_percentage"][0])
        start_index=\
        int(start_time_percentage*data_buffer_size/100)
#        self.memory = int(growth.stress_signal.memory.cdata)
        self.f_cirt = float(growth["stress_signal"]["critical_total_stress"][0])

        self.pas_set = float(growth["stress_signal"]["passive_set_point"][0])
        self.pas_set_max = float(growth["stress_signal"]["max_passive_set_point"][0])
        self.pas_set_min = float(growth["stress_signal"]["min_passive_set_point"][0])
        self.pas_set_slope = float(growth["stress_signal"]["slope_passive_set_point"][0])

        self.s_cirt = float(growth["strain_signal"]["critical_strain"][0])
        #Concentric growth (ventricle_mass)
        #wall_volume
        self.ventricle_wall_volume = \
        float(growth["stress_signal"]["concenrtric_growth"]["ventricle_wall_volume"][0])
        self.w_vol_0 = self.ventricle_wall_volume
        #self.G_w_vol = float(growth["stress_signal"]["concenrtric_growth"]["G_wall_volume"][0])
        self.delta_w_vol = [0.0]

        # wall_thickness
        self.ventricle_slack_volume = \
        float(growth["stress_signal"]["concenrtric_growth"]["ventricle_slack_volume"][0])


        internal_r = np.power((3.0 * 0.001 * 1.5*self.ventricle_slack_volume)/
                                (2.0 * np.pi), (1.0 / 3.0))
        internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)

        self.initial_wall_thickness = 0.001 * self.ventricle_wall_volume /internal_area
        self.tw = self.initial_wall_thickness
        self.tw_0 = self.initial_wall_thickness
        self.G_tw = float(growth["stress_signal"]["concenrtric_growth"]["G_wall_thickness"][0])
        self.delta_tw = [0.0]

        #Eccentric growth (number of hs in sereis)
        self.n_of_hs_0 = initial_numbers_of_hs
        self.max_n_hs = 1.5*initial_numbers_of_hs
        self.min_n_hs = 0.8*initial_numbers_of_hs
        self.n_of_hs = self.n_of_hs_0

        self.n_hs_set = self.n_of_hs
        self.v_set = 0.2
        self.v_slope = 0.03
        self.G_n_hs = float(growth["stress_signal"]["eccentric_growth"]["G_number_of_hs"][0])
        self.delta_n_hs = [0.0]

        #data
        self.data_buffer_size = data_buffer_size
        self.gr_time = 0.0
        self.data_buffer_index = start_index
        self.gr_data = pd.DataFrame({'average_force':
                                            np.zeros(self.data_buffer_size),
                                    'cycle_counter':
                                            np.zeros(self.data_buffer_size),
#                                    'ventricle_wall_volume':
#                                            np.zeros(self.data_buffer_size),
#                                    'ventricle_wall_thickness':
#                                            np.full(self.data_buffer_size,self.tw_0),
                                    'passive_set':
                                            np.full((self.data_buffer_size),self.pas_set),
                                    'number_of_hs':
                                            np.full(self.data_buffer_size,self.n_of_hs_0)})

#        self.gr_data.at[0, 'ventricle_wall_volume'] = self.ventricle_wall_volume
#        self.gr_data.at[0, 'ventricle_wall_thickness'] = self.tw_0
#        self.gr_data.at[0, 'number_of_hs'] = self.n_of_hs_0
