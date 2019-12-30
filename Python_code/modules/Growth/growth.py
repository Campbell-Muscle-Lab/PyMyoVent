import numpy as np
import pandas as pd

class growth():
    """"Class for growth"""
    from .implement import return_force_array_per_cycle,steady_state_identifier
    from .implement import return_ventricle_slack_volume,return_ventricle_mass,update_data_holder
    from .display import display_growth
    def __init__(self,growth_params,data_buffer_size):

        growth = growth_params


        self.memory = int(growth.stress_signal.memory.cdata)
        self.f_cirt = float(growth.stress_signal.critical_stress.cdata)
        #lv_volume = float(growth.stress_signal.ventricle_slack_volume.cdata)
        #internal_r = np.power((3.0 * 0.001 * lv_volume)/
        #                        (2.0 * np.pi), (1.0 / 3.0))
        #internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)

#        self.tw_0 = initial_wall_thickness#0.001 * lv_volume / internal_area
#        self.tw= self.tw_0

#        self.G_tw = float(growth.stress_signal.G_wall_thickness.cdata)
#        self.tau_tw = float(growth.stress_signal.tau_wall_thickness.cdata)
#        self.delta_tw = [0.0]

        #ventricle_mass
        self.ventricle_wall_volume = \
        float(growth.stress_signal.ventricle_mass.ventricle_wall_volume.cdata)
        self.w_vol_0 = self.ventricle_wall_volume#float(growth.stress_signal.ventricle_wall_volume.cdata)
        #self.ventricle_wall_volume = self.w_vol_0
        self.G_w_vol = \
        float(growth.stress_signal.ventricle_mass.G_wall_volume.cdata)
        self.tau_w_vol = \
        float(growth.stress_signal.ventricle_mass.tau_wall_volume.cdata)
        self.delta_w_vol = [0.0]
        #ventricle_slack_volume
        self.ventricle_slack_volume = \
        float(growth.stress_signal.ventricle_volume.ventricle_slack_volume.cdata)
        self.sl_vol_0 = self.ventricle_slack_volume
        self.G_sl_vol = \
        float(growth.stress_signal.ventricle_volume.G_slack_volume.cdata)
        self.tau_sl_vol = \
        float(growth.stress_signal.ventricle_volume.tau_slack_volume.cdata)
        self.delta_sl_vol = [0.0]
        #self.force_counter = int(initial_T / time_step)
        #self.total_force_array = np.zeros(self.force_counter+1)
        #self.avg_total_force_array = np.zeros(self.memory+1)
        #self.avg_total_force_array = np.array([0])


        #self.counter = self.force_counter
        #self.avg_counter = 0
        #data
        self.data_buffer_size = data_buffer_size
        self.gr_time = 0.0
        self.data_buffer_index = 0
        self.gr_data = pd.DataFrame({'average_force':
                                            np.zeros(self.data_buffer_size),
                                    'cycle_counter':
                                            np.zeros(self.data_buffer_size),
                                    'lv_wall_thickness':
                                            np.zeros(self.data_buffer_size),
                                    'ventricle_wall_volume':
                                            np.zeros(self.data_buffer_size),
                                    'ventricle_slack_volume':
                                            np.zeros(self.data_buffer_size)})


        self.gr_data.at[0, 'average_force'] = 0
        self.gr_data.at[0, 'cycle_counter'] = 0
        self.gr_data.at[0, 'wall_thickness'] = 0#self.tw_0
        self.gr_data.at[0, 'ventricle_wall_volume'] = self.ventricle_wall_volume
        self.gr_data.at[0, 'ventricle_slack_volume'] = self.ventricle_slack_volume
