import numpy as np
from math import *
from scipy.integrate import solve_ivp
from scipy import signal

def update_baroreceptor(self,time_step,arterial_pressure):

    if (self.baro_scheme == "simple_baroreceptor"):
        # baroreceptor control
        self.b = ((self.b_min+self.b_max*exp((arterial_pressure-self.P_set)*self.S))\
           /(1+exp((arterial_pressure-self.P_set)*self.S)))

def return_heart_period(self,time_step,arterial_pressure):

    if (self.baro_scheme == "simple_baroreceptor"):
        return_heart_period_control(self,time_step)

        self.T_counter -= 1
        if (self.T_counter <= -self.counter_systole):

            self.T=self.T_prime
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.T_counter = self.counter_diastole


    return self.T

def update_MAP(self,arterial_pressure):
    self.MAP_counter -= 1
    if (self.MAP_counter <= -self.counter_systole):
        self.MAP = np.mean(self.pressure_arteries_array)
        self.pressure_arteries_array = np.zeros(int(self.T/self.dt))
        self.MAP_counter = self.counter_diastole

    self.pressure_arteries_array = np.roll(self.pressure_arteries_array,-1)
    self.pressure_arteries_array[-1] = arterial_pressure


def return_heart_period_control(self,time_step):

    if (self.baro_scheme == "simple_baroreceptor"):

        T_prime_0 = self.T_prime
        self.T_rate_array = np.roll(self.T_rate_array,-1)
        #dTdt_0 = self.G_T*(self.b[i]-self.b_mid)*self.T0
        dTdt_0 = self.G_T*(self.b-self.b_mid)*self.T0
        self.T_rate_array[-1] = dTdt_0
        dTdt = np.mean(self.T_rate_array)
        T_prime=dTdt*time_step+T_prime_0
        self.T_prime = T_prime

        #implement minimum range of heart period for human
        if self.T_prime <= 0.33:
            self.T_prime = 0.33
        if self.T_prime >= 1.5:
            self.T_prime = 1.5

def return_contractility(self,k_1,k_on,time_step):

    if (self.baro_scheme == "simple_baroreceptor"):
        #time delay

        k1_0 = k_1#self.k1
        self.k1_rate_array = np.roll(self.k1_rate_array,-1)
#        dk1dt_0 = self.G_k1*(self.b[i]-self.b_mid)*self.k1_0
        dk1dt_0 = self.G_k1*(self.b-self.b_mid)*self.k1_0
        self.k1_rate_array[-1] = dk1dt_0
        dk1dt = np.mean(self.k1_rate_array)
        k1 = dk1dt*time_step+k1_0
        self.k1 = k1


        k_on_0 = k_on#self.k_on
        self.k_on_rate_array = np.roll(self.k_on_rate_array,-1)
#        dk_ondt_0 = self.G_k_on*(self.b[i]-self.b_mid)*self.k_on_0
        dk_ondt_0 = self.G_k_on*(self.b-self.b_mid)*self.k_on_0
        self.k_on_rate_array[-1] = dk_ondt_0
        dk_ondt = np.mean(self.k_on_rate_array)
        k_on = dk_ondt*time_step+k_on_0
        self.k_on = k_on

    return self.k1,self.k_on


def update_ca_transient(self,ca_up,g_cal,time_step):

    if (self.baro_scheme == "simple_baroreceptor"):

        ca_up_0 = ca_up#self.ca_uptake
        self.ca_uptake_rate_array = np.roll(self.ca_uptake_rate_array,-1)
        #dupdt_0 = self.G_up*(self.b[i]-self.b_mid)*self.ca_uptake_0
        dupdt_0 = self.G_up*(self.b-self.b_mid)*self.ca_uptake_0
        self.ca_uptake_rate_array[-1] = dupdt_0
        dupdt = np.mean(self.ca_uptake_rate_array)
        ca_uptake = dupdt*time_step+ca_up_0
        self.ca_uptake = ca_uptake


        gcal_0 = g_cal#self.g_cal
        self.g_cal_rate_array = np.roll(self.g_cal_rate_array,-1)
        #dgcaldt_0 = self.G_gcal*(self.b[i]-self.b_mid)*self.g_cal_0
        dgcaldt_0 = self.G_gcal*(self.b-self.b_mid)*self.g_cal_0
        self.g_cal_rate_array[-1] = dgcaldt_0
        dgcaldt = np.mean(self.g_cal_rate_array)
        g_cal = dgcaldt*time_step+gcal_0
        self.g_cal = g_cal


    return self.ca_uptake,self.g_cal

def return_venous_compliance(self,cv,time_step):
    if (self.baro_scheme == "simple_baroreceptor"):
        #time delay

        cv_0 = self.c_venous
        self.c_venous_rate_array = np.roll(self.c_venous_rate_array,-1)
#        dk1dt_0 = self.G_k1*(self.b[i]-self.b_mid)*self.k1_0
        dcvdt_0 = self.G_c_venous*(self.b-self.b_mid)*self.c_venous_0
        self.c_venous_rate_array[-1] = dcvdt_0
        dcvdt = np.mean(self.c_venous_rate_array)
        cv = dcvdt*time_step+cv_0
        self.c_venous = cv

    return self.c_venous

def return_arteriolar_resistance(self,ra,time_step):
    if (self.baro_scheme == "simple_baroreceptor"):
        #time delay

        ra_0 = self.r_arteriolar
        self.r_arteriolar_rate_array = np.roll(self.r_arteriolar_rate_array,-1)
#        dk1dt_0 = self.G_k1*(self.b[i]-self.b_mid)*self.k1_0
        dradt_0 = self.G_r_arteriolar*(self.b-self.b_mid)*self.r_arteriolar_0
        self.r_arteriolar_rate_array[-1] = dradt_0
        dradt = np.mean(self.r_arteriolar_rate_array)
        ra = dradt*time_step+ra_0
        self.r_arteriolar = ra

    return self.r_arteriolar

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

def update_data_holder(self,time_step):

    # Update data struct for system-control
    self.sys_time = self.sys_time + time_step
    self.data_buffer_index += 1
    self.sys_data.at[self.data_buffer_index, 'heart_period']=self.T
    self.sys_data.at[self.data_buffer_index, 'heart_rate']=60/self.T
    self.sys_data.at[self.data_buffer_index, 'MAP']=self.MAP

    if (self.baro_scheme !="fixed_heart_rate"):
        self.sys_data.at[self.data_buffer_index, 'k_1'] = self.k1
        self.sys_data.at[self.data_buffer_index, 'k_on'] = self.k_on
        self.sys_data.at[self.data_buffer_index, 'Ca_Vmax_up_factor'] = \
                                                self.hs.membr.constants[39]
        self.sys_data.at[self.data_buffer_index, 'g_CaL_factor'] = \
                                                self.hs.membr.constants[18]
        self.sys_data.at[self.data_buffer_index, 'compliance_veins'] = self.c_venous
        self.sys_data.at[self.data_buffer_index, 'resistance_arterioles'] = self.r_arteriolar

        if (self.baro_scheme == "simple_baroreceptor"):
            self.sys_data.at[self.data_buffer_index, 'baroreceptor_output']= self.b
#            self.sys_data.at[self.data_buffer_index, 'venous_resistance']=\
#                self.Rv
