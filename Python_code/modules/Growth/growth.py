import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_lv_wall_thickness,return_lv_wall_thickness_strain,\
    return_number_of_hs_strain
    from .implement import return_number_of_hs,update_data_holder
    from .implement import update_growth
    from .lowpass_filter import lowpass_filter
    from .setpoint import growth_driver
    from .display import display_growth

    def __init__(self,growth_params,initial_numbers_of_hs,data_buffer_size,hs_module):

        self.hs = hs_module
        self.growth = growth_params
        self.start_index = int(self.growth["start_index"][0])

        self.ventricle_wall_volume = float(self.growth["ventricle_wall_volume"][0])

        # wall_thickness
        self.ventricle_slack_volume = float(self.growth["ventricle_slack_volume"][0])

        internal_r = np.power((3.0 * 0.001 * 1.5*self.ventricle_slack_volume)/
                                (2.0 * np.pi), (1.0 / 3.0))
        internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)

        initial_wall_thickness = 0.001 * self.ventricle_wall_volume /internal_area

        self.tw = initial_wall_thickness
        self.tw_array = np.full(self.start_index,self.tw)
        self.tw_rate = np.zeros(self.start_index)
        self.min_tw = 0.8*self.tw
        #self.tw_counter_memory = 100
        #self.tw_counter = self.tw_counter_memory
        #self.tw_rate_control =[]

        if self.growth["driven_signal"][0] == "stress":
            self.G_tw = float(self.growth["stress_signal"]["concenrtric_growth"]["G_wall_thickness"][0])

        if self.growth["driven_signal"][0] == "strain":
            self.G_tw = float(self.growth["strain_signal"]["concenrtric_growth"]["Gs_wall_thickness"][0])

        #Eccentric self.growth (number of hs in sereis)
        self.n_of_hs = initial_numbers_of_hs
        self.n_of_hs_array = np.full(self.start_index,self.n_of_hs)
        self.n_hs_rate =  np.zeros(self.start_index)
        #self.n_hs_counter_memory = 100
        #self.n_hs_counter = self.n_hs_counter_memory
        #self.n_hs_rate_control = []
        self.max_n_hs = 1.5*initial_numbers_of_hs
        self.min_n_hs = 0.8*initial_numbers_of_hs
        if self.growth["driven_signal"][0] == "stress":
            self.G_n_hs = float(self.growth["stress_signal"]["eccentric_growth"]["G_number_of_hs"][0])
        if self.growth["driven_signal"][0] == "strain":
            self.G_n_hs = float(self.growth["strain_signal"]["eccentric_growth"]["Gs_number_of_hs"][0])

        #data
        self.data_buffer_size = data_buffer_size
        self.gr_time = 0.0
        self.data_buffer_index = self.start_index
        self.gr_data = pd.DataFrame({'average_force':
                                            np.zeros(self.data_buffer_size),
#                                    'cycle_counter':
#                                            np.zeros(self.data_buffer_size),
#                                    'ventricle_wall_volume':
#                                            np.zeros(self.data_buffer_size),
                                    'ventricle_wall_thickness':
                                            np.full(self.data_buffer_size,self.tw),
#                                    'passive_set':
#                                            np.full((self.data_buffer_size),self.pas_set),
#                                    'Gain_factor':
#                                            np.full((self.data_buffer_size),self.G_n_hs),
                    #                'self.growth_control':
                        #                    np.zeros(self.data_buffer_size),
                                    'number_of_hs':
                                            np.full(self.data_buffer_size,self.n_of_hs)})

#        self.gr_data.at[0, 'ventricle_wall_volume'] = self.ventricle_wall_volume
#        self.gr_data.at[0, 'ventricle_wall_thickness'] = self.tw_0
#        self.gr_data.at[0, 'number_of_hs'] = self.n_of_hs_0
