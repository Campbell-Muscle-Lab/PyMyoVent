import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_force_array_per_cycle,steady_state_identifier
    from .implement import update_data_holder
    from .display import display_growth
    def __init__(self, initial_T, time_step, growth_params,data_buffer_size):

        growth = growth_params

        self.memory = int(growth.memory.cdata)
        self.force_counter = int(initial_T / time_step)
        self.total_force_array = np.zeros(self.force_counter+1)
        #self.avg_total_force_array = np.zeros(self.memory+1)
        self.avg_total_force_array = np.array([0])


        self.counter = self.force_counter
        self.avg_counter = 0

        self.data_buffer_size = data_buffer_size
        self.sys_time = 0.0
        self.data_buffer_index = 0
        self.gr_data = pd.DataFrame({'average_force':
                                    np.zeros(self.data_buffer_size),
                                    'cycle_counter':
                                    np.zeros(self.data_buffer_size)})

        self.gr_data.at[0, 'average_force'] = 0
        self.gr_data.at[0, 'cycle_counter'] = 0
