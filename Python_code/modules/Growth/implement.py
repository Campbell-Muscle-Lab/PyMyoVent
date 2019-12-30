import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd



def return_lv_wall_thickness(self,time_step,cell_stress):

    f=cell_stress
    if f > self.f_cirt:

        def derivs(y,t):
            delta_tw = np.zeros(1)
            delta_tw[0] = 1/self.tau_tw*self.G_tw*(f-self.f_cirt)*self.tw_0
            return delta_tw
        initial_conditions = self.delta_tw
        sol = solve_ivp(derivs,[0,time_step],initial_conditions)
        self.delta_tw=sol.y[:,-1]
        self.tw = self.tw_0 + self.delta_tw
    else:
        self.tw=self.tw
    return self.tw
def return_ventricle_mass(self,time_step,cell_stress):

    f=cell_stress
    if f > self.f_cirt:

        def derivs(y,t):
            delta_wall_vol = np.zeros(1)
            delta_wall_vol[0] = 1/self.tau_w_vol*self.G_w_vol*(f-self.f_cirt)*self.w_vol_0
            return delta_wall_vol
        initial_conditions = self.delta_w_vol
        sol = solve_ivp(derivs,[0,time_step],initial_conditions)
        self.delta_w_vol=sol.y[:,-1]
        self.ventricle_wall_volume = self.w_vol_0 + self.delta_w_vol
    else:
        self.ventricle_wall_volume=self.ventricle_wall_volume
    return self.ventricle_wall_volume

def return_ventricle_slack_volume(self,time_step,cell_stress):

    f=cell_stress
    if f > self.f_cirt:
        def derivs(y,t):
            delta_slack_vol = np.zeros(1)
            delta_slack_vol[0] = 1/self.tau_sl_vol*self.G_sl_vol*(f-self.f_cirt)*self.sl_vol_0
            return delta_slack_vol
        initial_conditions = self.delta_sl_vol
        sol = solve_ivp(derivs,[0,time_step],initial_conditions)
        self.delta_sl_vol=sol.y[:,-1]
        self.ventricle_slack_volume = self.sl_vol_0 + self.delta_sl_vol
    else:
        self.ventricle_wall_volume=self.ventricle_wall_volume
    return self.ventricle_wall_volume


def steady_state_identifier(self):

    #avg_total_force should be an array which includes
    # the avg_total_force for the last #memoory cardiac cycle

    if len(set(self.avg_total_force_array[-self.memory:]))==1:
        self.steady_state = True
    else:
        self.steady_state = False

def avg_total_force (self):
    print('self.avg_counter',self.avg_counter)

    self.avg_total_force_array=np.append(self.avg_total_force_array,
                                np.mean(self.total_force_array))
    self.avg_counter +=1

    #print(self.avg_total_force_array)

def return_force_array_per_cycle(self,time_step,heart_period,total_force):


    if self.counter < 0:
        avg_total_force(self)
        self.force_counter=int(heart_period/time_step)
        self.counter = self.force_counter

        self.total_force_array=np.zeros(self.force_counter+1)
        return
    i=self.force_counter - self.counter

    self.total_force_array[i] = total_force

    self.counter -= 1

def update_data_holder(self,time_step):

    self.gr_time = self.gr_time + time_step
    self.data_buffer_index += 1
    #self.gr_data.at[self.data_buffer_index, 'average_force']=\
    #                                self.avg_total_force_array[-1]
    #self.gr_data.at[self.data_buffer_index, 'cycle_counter']= self.avg_counter
    #self.gr_data.at[self.data_buffer_index, 'wall_thickness'] = self.tw
    self.gr_data.at[self.data_buffer_index, 'ventricle_wall_volume'] = self.ventricle_wall_volume
    self.gr_data.at[self.data_buffer_index, 'ventricle_slack_volume'] = self.ventricle_slack_volume
