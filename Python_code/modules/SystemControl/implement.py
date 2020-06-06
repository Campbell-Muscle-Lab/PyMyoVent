import numpy as np
from math import *
from scipy.integrate import solve_ivp
from scipy import signal

def update_baroreceptor(self,time_step,arterial_pressure,arterial_pressure_rate):

    if (self.baro_scheme == "simple_baroreceptor"):
        # baroreceptor control
        self.bc = np.append(self.bc,\
         ((self.bc_min+self.bc_max*exp((arterial_pressure-self.P_n)/self.slope))\
            /(1+exp((arterial_pressure-self.P_n)/self.slope))))

    if (self.baro_scheme=="Ursino_1998"):

        def P_tilda_deriv(y,t):
            dy=np.zeros(1)
            dy[0]=1/self.tau_p*(arterial_pressure\
                    +self.tau_z*arterial_pressure_rate-self.P_tilda)
            return dy

        sol=solve_ivp(P_tilda_deriv,[0,time_step],self.P_tilda)
        self.P_tilda=sol.y[:,-1]

        #determine the frequency of spikes in the affetent pathway
        self.f_cs=(self.f_min+self.f_max*exp((self.P_tilda-self.P_n)/self.k_a))\
            /(1+exp((self.P_tilda-self.P_n)/self.k_a))

        #determine the frequency of spikes in the efferent sympathetic pathway
        self.f_es=np.append(self.f_es,\
                (self.f_es_inf+(self.f_es_0-self.f_es_inf)*exp(-self.k_es*self.f_cs)))
        self.f_es_min=(self.f_es_inf+(self.f_es_0-self.f_es_inf)*exp(-self.k_es*self.f_max))

        #determine the frequency of spikes in the efferent vagal pathway
        self.f_ev=np.append(self.f_ev,\
        (self.f_ev_0+self.f_ev_inf*exp((self.f_cs-self.f_cs_0)/self.k_ev))\
            /(1+exp((self.f_cs-self.f_cs_0)/self.k_ev)))
        #return self.P_tilda,self.f_cs,self.f_es,self.f_es_min,self.f_ev
def return_heart_period(self,time_step,i):

    if (self.baro_scheme == "simple_baroreceptor"):
        return_heart_period_control(self,time_step,i)
        self.T_counter -= 1
        if (self.T_counter <= -self.counter_systole):

            self.T=self.T_prime
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.T_counter = self.counter_diastole

    if (self.baro_scheme == "Ursino_1998"):
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
        #time delay
        if i < self.D_T:
            delay_T = int(0)
        else:
            delay_T = self.D_T
        T_prime_0 = self.T_prime
        dTdt=self.G_T*(self.bc[i-delay_T]-self.bc_mid)*self.T0
        T_prime=dTdt*time_step+T_prime_0
        self.T_prime = T_prime
        #implement minimum range of heart period for human
        if self.T_prime <= 0.4:
            self.T_prime = 0.4
        if self.T_prime >= 1.5:
            self.T_prime = 1.5
    if (self.baro_scheme=="Ursino_1998"):
        #determine the outputs of static characteristics (steady-state changes)
        # apply time delay
        if i < self.D_Ts:
            delay_Ts=int(0)
        else:
            delay_Ts=self.D_Ts
        #sympathetic
        if self.f_es[i] >= self.f_es_min:
            sigma_Ts=self.G_Ts*log(self.f_es[i-delay_Ts]-self.f_es_min+1)
        else:
            sigma_Ts=0.0

        # apply time delay
        if i < self.D_Tv:
            delay_Tv=int(0)
        else:
            delay_Tv=self.D_Tv
        #vagal
        sigma_Tv=self.G_Tv*self.f_ev[i-delay_Tv]

        #determine the heart rate change due to sympathetic and vagal activities
        def delta_T_derivs(y,t):

            delta_T=np.zeros(2)
            #delta_Ts_deriv
            delta_T[0]=1/self.tau_Ts*(sigma_Ts-self.delta_Ts)
            #delta_Tv_deriv
            delta_T[1]=1/self.tau_Tv*(sigma_Tv-self.delta_Tv)
            return delta_T
        initial_condition = [self.delta_Ts,self.delta_Tv]
        sol=solve_ivp(delta_T_derivs,[0,time_step],initial_condition)
        self.y=sol.y[:,-1]
        #print(self.y)
        self.delta_Ts=self.y[0]
        self.delta_Tv=self.y[1]

        self.T_prime=self.delta_Ts+self.delta_Tv+self.T0

        #return self.T, self.P_tilda,self.f_cs,self.f_es[-1],self.f_es_min,self.f_ev[-1],self.delta_Ts,self.delta_Tv

def return_contractility(self,time_step,i):

    if (self.baro_scheme == "simple_baroreceptor"):
        #time delay
        if i < self.D_k1:
            delay_k1 = int(0)
        else:
            delay_k1 = self.D_k1

        if i < self.D_k3:
            delay_k3 = int(0)
        else:
            delay_k3 = self.D_k3

        k1_0 = self.k1
        dk1dt = self.G_k1*(self.bc[i-delay_k1]-self.bc_mid)*self.k1_0
        k1 = dk1dt*time_step+k1_0
        self.k1 = k1

        k3_0 = self.k3
        dk3dt = self.G_k3*(self.bc[i-delay_k3]-self.bc_mid)*self.k3_0
        k3 = dk3dt*time_step + k3_0
        self.k3 = k3


    if (self.baro_scheme=="Ursino_1998"):
        #determine the outputs of static characteristics (steady-state changes)
        if i<self.D_k1:
            delay_k1=int(0)
        else:
            delay_k1=self.D_k1

        if i<self.D_k3:
            delay_k3=int(0)
        else:
            delay_k3=self.D_k3

        if self.f_es[i] >= self.f_es_min:
            sigma_k1=self.G_k1*log(self.f_es[i-delay_k1]-self.f_es_min+1)
            sigma_k3=self.G_k3*log(self.f_es[i-delay_k3]-self.f_es_min+1)
        else:
            sigma_k1=0
            sigma_k3=0
        #determine the elastance rate change due to sympathetic
        def derivs(y,t):
            delta=np.zeros(2)
            delta[0]=1/self.tau_k1*(sigma_k1-self.delta_k1)
            delta[1]=1/self.tau_k3*(sigma_k3-self.delta_k3)
            return delta
        initial_condition=[self.delta_k1,self.delta_k3]
        sol=solve_ivp(derivs,[0,time_step], initial_condition)
        y=sol.y[:,-1]
        self.delta_k1=y[0]
        self.delta_k3=y[1]

        self.k1 = self.delta_k1 + self.k1_0
        self.k3 = self.delta_k3 + self.k3_0

    return self.k1,self.k3 #self.L_scale_factor, self.k_3_scale_factor, self.k_cb_scale_factor,self.k_force_scale_factor

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
    dRvdt = self.G_Rv*(self.bc[i-delay_Rv]-self.bc_mid)*self.Rv_0
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
        self.sys_data.at[self.data_buffer_index, 'k_3'] = self.k3

        if (self.baro_scheme == "simple_baroreceptor"):
            self.sys_data.at[self.data_buffer_index, 'baroreceptor_output']\
             = self.bc[-1]
            self.sys_data.at[self.data_buffer_index, 'venous_resistance']=\
                self.Rv
        if (self.baro_scheme == "Ursino_1998"):
            self.sys_data.at[self.data_buffer_index, 'P_tilda'] = self.P_tilda
            self.sys_data.at[self.data_buffer_index, 'f_cs'] = self.f_cs
