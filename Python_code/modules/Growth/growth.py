import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_lv_wall_thickness
    from .implement import return_number_of_hs,update_data_holder
    from .implement import update_growth
    from .lowpass_filter import lowpass_filter
    from .setpoint import growth_driver
    from .display import display_growth, display_growth_summary, display_ventricular_dimensions
    from .display import display_systolic_function, display_ATPase

    def __init__(self,growth_params,initial_numbers_of_hs,hs_module,circ_params,data_buffer_size):

        self.hs = hs_module
        self.growth = growth_params
        self.start_index = int(self.growth["start_index"][0])
        self.ma_window = int(growth_params["moving_average_window"][0])

        # Concentric growth
        ventricle_wall_volume = float(circ_params["ventricle"]["wall_volume"][0])
        ventricle_slack_volume = float(circ_params["ventricle"]["slack_volume"][0])
        internal_r = np.power((3.0 * 0.001 * 1.5*ventricle_slack_volume)/
                                (2.0 * np.pi), (1.0 / 3.0))
        internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
        initial_wall_thickness = 0.001 * ventricle_wall_volume /internal_area

        self.tw = initial_wall_thickness
        self.tw_array = np.full(self.start_index,self.tw)
        self.tw_rate = np.zeros(self.start_index)
        self.min_tw = 0.8*self.tw

        #Eccentric growth (number of hs in sereis)
        self.n_of_hs = initial_numbers_of_hs
        self.n_of_hs_array = np.full(self.start_index,self.n_of_hs)
        self.n_hs_rate =  np.zeros(self.start_index)
        self.max_n_hs = 1.5*initial_numbers_of_hs
        self.min_n_hs = 0.8*initial_numbers_of_hs

        if self.growth["driven_signal"][0] == "stress":
            self.G_tw = float(self.growth["concenrtric"]["G_stress_driven"][0])
            self.G_n_hs = float(self.growth["eccentric"]["G_number_of_hs"][0])
        if self.growth["driven_signal"][0] == "ATPase":
            self.G_tw = float(self.growth["concenrtric"]["G_ATPase_driven"][0])
            self.G_n_hs = float(self.growth["eccentric"]["G_ATPase_driven"][0])
            
        #data
        self.data_buffer_size = data_buffer_size
        self.gr_time = 0.0
        self.data_buffer_index = self.start_index
        self.gr_data = pd.DataFrame({'ventricle_wall_thickness':
                                            np.full(self.data_buffer_size,1000*self.tw),
                                    'number_of_hs':
                                            np.full(self.data_buffer_size,self.n_of_hs)})
