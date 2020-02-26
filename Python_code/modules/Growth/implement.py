import numpy as np
from math import *
from scipy.integrate import solve_ivp
import pandas as pd

def update_growth(self,time_step):
    self.wall_thickness = return_lv_wall_thickness(self,time_step)
    self.number_of_hs = return_number_of_hs(self,time_step)
# stress driven growth
def return_lv_wall_thickness(self,time_step):#,cb_stress,cb_stress_null,i):
    f = self.hs.myof.cb_force
    #f=cb_stress
    f_null = self.cb_stress_null

    """tw_1 = self.tw
    dwdt=self.G_tw*(f-f_null)*self.tw
    tw = dwdt*time_step+tw_1"""

    window = 5000

    """tw_1 = self.tw
    dwdt= self.G_tw*(f-f_null)*self.tw
    tw = dwdt*time_step+tw_1
    self.tw_array = np.append(self.tw_array,tw)
    self.tw = np.mean(self.tw_array[-window:])"""

    tw_1 = self.tw
    dwdt_0 = self.G_tw*(f-f_null)*self.tw
    self.tw_rate = np.append(self.tw_rate,dwdt_0)
    dwdt=np.mean(self.tw_rate[-window:])
    tw = dwdt*time_step+tw_1
    self.tw = tw
    if self.tw <= self.min_tw:
        self.tw = self.min_tw

    return self.tw

def return_number_of_hs(self,time_step):#,passive_stress,passive_stress_null,i):
    p = self.hs.myof.pas_force
    p_null = self.passive_stress_null

    """n_1 = self.n_of_hs
    dndt = self.G_n_hs_0 * self.n_of_hs* (p - p_null)
    n=dndt*time_step+n_1"""

    window = 5000

    """n_1 = self.n_of_hs
    dndt = self.G_n_hs * self.n_of_hs* (p - p_null)
    n=dndt*time_step+n_1
    self.n_of_hs_array = np.append(self.n_of_hs_array,n)
    self.n_of_hs = np.mean(self.n_of_hs_array[-window:])"""

    n_1 = self.n_of_hs
    dndt_0 = self.G_n_hs * self.n_of_hs* (p - p_null)
    self.n_hs_rate = np.append(self.n_hs_rate,dndt_0)
    dndt = np.mean(self.n_hs_rate[-window:])
    n=dndt*time_step+n_1
    self.n_of_hs = n
    if self.n_of_hs<=self.min_n_hs:
        print('too less')
    if self.n_of_hs>=self.max_n_hs:
        print('lv vol',lv_volume)
        print('n_hs',self.n_of_hs)

    return self.n_of_hs
# strain driven
def return_lv_wall_thickness_strain(self,time_step,cell_strain,strain_null):

    s=cell_strain
    s_null = self.strain_null

    tw_1 = self.tw
    dwdt = self.G_tw*self.tw*(s-s_null)
    tw = dwdt*time_step+tw_1
    self.tw = tw

    if self.tw <= self.min_tw:
        self.tw = self.min_tw



    return self.tw

def return_number_of_hs_strain(self,time_step,cell_strain,strain_null):

    s= cell_strain
    s_null = strain_null

    n_1 = self.n_of_hs
    dndt = self.G_n_hs_0 * self.n_of_hs* np.power((s - s_null),1)
    n=dndt*time_step+n_1

    self.n_of_hs = n
    if self.n_of_hs<=self.min_n_hs:
        self.n_of_hs = self.min_n_hs


    return self.n_of_hs


def update_data_holder(self,time_step):

    self.gr_time = self.gr_time + time_step
    self.data_buffer_index += 1

#    self.gr_data.at[self.data_buffer_index, 'ventricle_wall_volume'] = self.ventricle_wall_volume
    self.gr_data.at[self.data_buffer_index, 'ventricle_wall_thickness'] = self.wall_thickness
    self.gr_data.at[self.data_buffer_index, 'number_of_hs'] = self.number_of_hs
#    self.gr_data.at[self.data_buffer_index, 'Gain_factor'] = self.G_n_hs
#    self.gr_data.at[self.data_buffer_index, 'growth_control'] = self.c


#    self.gr_data.at[self.data_buffer_index, 'passive_set'] = self.pas_set
