import numpy as np
from math import *
from scipy.integrate import solve_ivp
from scipy import signal

def update_baroreceptor(self,time_step,arterial_pressure,arterial_pressure_rate):

    if (self.baro_scheme == "simple_baroreceptor"):
        # baroreceptor control
        self.b = np.append(self.b,\
         ((self.b_min+self.b_max*exp((arterial_pressure-self.P_n)*self.S))\
            /(1+exp((arterial_pressure-self.P_n)*self.S))))

def return_heart_period(self,time_step,i):

    if (self.baro_scheme == "simple_baroreceptor"):
        return_heart_period_control(self,time_step,i)
        self.T_counter -= 1
        if (self.T_counter <= -self.counter_systole):

            self.T=self.T_prime
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.T_counter = self.counter_diastole

    return self.T
def return_heart_period_control(self,time_step,i):

    if (self.baro_scheme == "simple_baroreceptor"):

        T_prime_0 = self.T_prime
        self.T_rate_array = np.roll(self.T_rate_array,-1)
        dTdt_0 = self.G_T*(self.b[i]-self.b_mid)*self.T0
        self.T_rate_array[-1] = dTdt_0
        dTdt = np.mean(self.T_rate_array)
        T_prime=dTdt*time_step+T_prime_0
        self.T_prime = T_prime

        #implement minimum range of heart period for human
        if self.T_prime <= 0.33:
            self.T_prime = 0.33
        if self.T_prime >= 1.5:
            self.T_prime = 1.5

def return_contractility(self,time_step,i):

    if (self.baro_scheme == "simple_baroreceptor"):
        #time delay

        k1_0 = self.k1
        self.k1_rate_array = np.roll(self.k1_rate_array,-1)
        dk1dt_0 = self.G_k1*(self.b[i]-self.b_mid)*self.k1_0
        self.k1_rate_array[-1] = dk1dt_0
        dk1dt = np.mean(self.k1_rate_array)
        k1 = dk1dt*time_step+k1_0
        self.k1 = k1

        if self.k1<0.3*self.k1_0:
            self.k1 = 0.3*self.k1_0
        if self.k1>2*self.k1_0:
            self.k1 = 2*self.k1_0

        """k3_0 = self.k3
        self.k3_rate_array = np.roll(self.k3_rate_array,-1)
        dk3dt_0 = self.G_k3*(self.b[i]-self.b_mid)*self.k3_0
        self.k3_rate_array[-1] = dk3dt_0
        dk3dt = np.mean(self.k3_rate_array)
        k3 = dk3dt*time_step+k3_0
        self.k3 = k3

        if self.k3<0.3*self.k3_0:
            self.k3 = 0.3*self.k3_0
        if self.k3>2*self.k3_0:
            self.k3 = 2*self.k3_0"""

        k_on_0 = self.k_on
        self.k_on_rate_array = np.roll(self.k_on_rate_array,-1)
        dk_ondt_0 = self.G_k_on*(self.b[i]-self.b_mid)*self.k_on_0
        self.k_on_rate_array[-1] = dk_ondt_0
        dk_ondt = np.mean(self.k_on_rate_array)
        k_on = dk_ondt*time_step+k_on_0
        self.k_on = k_on

        if self.k_on<0.3*self.k_on_0:
            self.k_on = 0.3*self.k_on_0
        if self.k_on>2*self.k_on_0:
            self.k_on = 2*self.k_on_0


        ca_up_0 = self.ca_uptake
        self.ca_uptake_rate_array = np.roll(self.ca_uptake_rate_array,-1)
        dupdt_0 = self.G_up*(self.b[i]-self.b_mid)*self.ca_uptake_0
        self.ca_uptake_rate_array[-1] = dupdt_0
        dupdt = np.mean(self.ca_uptake_rate_array)
        ca_uptake = dupdt*time_step+ca_up_0
        self.ca_uptake = ca_uptake

        if self.ca_uptake<0.3*self.ca_uptake_0:
            self.ca_uptake = 0.3*self.ca_uptake_0
        if self.ca_uptake>2*self.ca_uptake_0:
            self.ca_uptake = 2*self.ca_uptake_0

        gcal_0 = self.g_cal
        self.g_cal_rate_array = np.roll(self.g_cal_rate_array,-1)
        dgcaldt_0 = self.G_gcal*(self.b[i]-self.b_mid)*self.g_cal_0
        self.g_cal_rate_array[-1] = dgcaldt_0
        dgcaldt = np.mean(self.g_cal_rate_array)
        g_cal = dgcaldt*time_step+gcal_0
        self.g_cal = g_cal

        if self.g_cal<0.3*self.g_cal_0:
            self.g_cal = 0.3*self.g_cal_0
        if self.g_cal>2*self.g_cal_0:
            self.g_cal = 2*self.g_cal_0

    return self.k1,self.k_on,self.ca_uptake,self.g_cal  #self.L_scale_factor, self.k_3_scale_factor, self.k_cb_scale_factor,self.k_force_scale_factor

def return_activation(self):
    if (self.baro_scheme == "fixed_heart_rate"):

        self.activation_level = self.predefined_activation_level[self.activation_counter]
        self.activation_counter += 1
        return self.activation_level

    else:
        self.baroreceptor_counter -= 1
        if (self.baroreceptor_counter <= 0):
            self.activation_level = 1.0
        if (self.baroreceptor_counter <= -self.counter_systole):
            self.activation_level = 0.0
            self.T_systole = self.activation_duty_ratio * self.T
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
        return self.activation_level

def return_venous_resistance(self,time_step,i):
    if i < self.D_Rv:
        delay_Rv = int(0)
    else:
        delay_Rv = self.D_Rv

    Rv_0 = self.Rv
    dRvdt = self.G_Rv*(self.b[i-delay_Rv]-self.b_mid)*self.Rv_0
    Rv = dRvdt*time_step+Rv_0
    self.Rv = Rv

    return Rv
def update_data_holder(self,time_step):

    # Update data struct for system-control
    self.sys_time = self.sys_time + time_step
    self.data_buffer_index += 1
    self.sys_data.at[self.data_buffer_index, 'heart_period']=self.T
    self.sys_data.at[self.data_buffer_index, 'heart_rate']=60/self.T

    if (self.baro_scheme !="fixed_heart_rate"):
        self.sys_data.at[self.data_buffer_index, 'k_1'] = self.k1
        #self.sys_data.at[self.data_buffer_index, 'k_3'] = self.k3
        self.sys_data.at[self.data_buffer_index, 'k_on'] = self.k_on
        self.sys_data.at[self.data_buffer_index, 'Ca_Vmax_up_factor'] = self.hs.membr.constants[39]
        self.sys_data.at[self.data_buffer_index, 'g_CaL_factor'] = self.hs.membr.constants[18]#self.g_cal

        if (self.baro_scheme == "simple_baroreceptor"):
            self.sys_data.at[self.data_buffer_index, 'baroreceptor_output']\
             = self.b[-1]
#            self.sys_data.at[self.data_buffer_index, 'venous_resistance']=\
#                self.Rv
