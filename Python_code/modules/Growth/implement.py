import numpy as np
from math import *
from scipy.integrate import solve_ivp
import pandas as pd

def update_growth(self,time_step):

    self.wall_thickness = return_lv_wall_thickness(self,time_step)
    self.number_of_hs = return_number_of_hs(self,time_step)

# stress driven growth
def return_lv_wall_thickness(self,time_step):

    if self.growth["driven_signal"][0] == "stress":

        f = self.hs.myof.cb_force
#         f_null = self.cb_stress_null
        window_null = int(self.start_index)
        self.cb_array = np.append(self.cb_array,f)
        f_null =np.mean(self.cb_array)
        self.cb_stress_null = f_null

        window = self.ma_window

        tw_1 = self.tw
        dwdt_0 = self.G_tw*(f-f_null)*self.tw
        self.tw_rate = np.append(self.tw_rate,dwdt_0)
        dwdt=np.mean(self.tw_rate[-window:])
        tw = dwdt*time_step+tw_1
        self.tw = tw

        if self.tw <= self.min_tw:
            self.tw = self.min_tw

    if self.growth["driven_signal"][0] == "ATPase":

        """A = self.hs.ATPase
        self.ATPase_array = np.append(self.ATPase_array,A)
        A_null = np.mean(self.ATPase_array)
        self.ATPase_null = A_null

        window = self.ma_window

        tw_1 = self.tw
        dwdt_0 = self.G_tw*(A-A_null)*self.tw
        self.tw_rate = np.append(self.tw_rate,dwdt_0)
        dwdt = np.mean(self.tw_rate[-window:])
        tw = dwdt*time_step+tw_1
        self.tw = tw"""

        self.ATPase_array = np.append(self.ATPase_array,self.hs.ATPase)
        self.ATPase_null = np.mean(self.ATPase_array)
        dwdt_0 = self.G_tw*(self.hs.ATPase-self.ATPase_null)*self.tw
        self.tw_rate = np.append(self.tw_rate,dwdt_0)
        dwdt = np.mean(self.tw_rate[-self.ma_window:])
        self.tw = dwdt*time_step + self.tw

    return self.tw

def return_number_of_hs(self,time_step):
    p = self.hs.myof.pas_force
#    p_null = self.passive_stress_null

    window_null = int(self.start_index/1)
    self.pass_array = np.append(self.pass_array,p)
    p_null =np.mean(self.pass_array)
    self.passive_stress_null = p_null

    window = self.ma_window

    n_1 = self.n_of_hs
    dndt_0 = self.G_n_hs * self.n_of_hs* (p - p_null)
    self.n_hs_rate = np.append(self.n_hs_rate,dndt_0)
    dndt = np.mean(self.n_hs_rate[-window:])
    n=dndt*time_step+n_1
    self.n_of_hs = n

    if self.n_of_hs<=self.min_n_hs:
        print('too less')
    if self.n_of_hs>=self.max_n_hs:
        #print('lv vol',lv_volume)
        print('n_hs',self.n_of_hs)

    return self.n_of_hs


def update_data_holder(self,time_step):

    self.gr_time = self.gr_time + time_step
    self.data_buffer_index += 1
    self.gr_data.at[self.data_buffer_index,'pas_force_null'] = self.passive_stress_null

    if self.growth["driven_signal"][0] == "stress":
        self.gr_data.at[self.data_buffer_index,'cb_force_null'] = self.cb_stress_null

    if self.growth["driven_signal"][0] == "ATPase":
        self.gr_data.at[self.data_buffer_index,'ATPase_null'] = self.ATPase_null
    # 1000 is to convert liter to mili liter
    self.gr_data.at[self.data_buffer_index, 'ventricle_wall_thickness'] = 1000*self.wall_thickness
    self.gr_data.at[self.data_buffer_index, 'number_of_hs'] = self.number_of_hs
