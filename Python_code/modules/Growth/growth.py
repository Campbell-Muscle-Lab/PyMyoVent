import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_force_array_per_cycle
    def __init__(self, initial_T, time_step, growth_params,data_buffer_size):

        growth = growth_params
        self.memory = growth.memory
        self.avg_total_force_array = np.zeros(self.memory)

        self.force_counter = initial_T / time_step
        self.counter = self.force_counter
        self.total_force_array = np.zeros(self.force_counter)
