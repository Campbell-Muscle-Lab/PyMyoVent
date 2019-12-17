import numpy as np
from math import *
from scipy.integrate import solve_ivp
from scipy import signal

def update_baroreceptor(self,time_step,arterial_pressure,arterial_pressure_rate,i):

    if (self.baro_scheme == "simple_model"):
        # baroreceptor control
        self.bc = self.bc_min+self.bc_max*exp((arterial_pressure-self.P_n)/self.slope)\
            /(1+exp((arterial_pressure-self.P_n)/self.slope))

    if (self.baro_scheme=="Ursino_1998"):

        #print('arterial_pressure_rate',arterial_pressure_rate)
        def P_tilda_deriv(y,t):
            dy=np.zeros(1)
            dy[0]=1/self.tau_p*(arterial_pressure+self.tau_z*arterial_pressure_rate-self.P_tilda)
            return dy
            #determine the output variable of the linear dynamic block
            #print('self.P_tilda',self.P_tilda)
        sol=solve_ivp(P_tilda_deriv,[0,time_step],self.P_tilda)
        self.P_tilda=sol.y[:,-1]

        #determine the frequency of spikes in the affetent pathway
        self.f_cs=(self.f_min+self.f_max*exp((self.P_tilda-self.P_n)/self.k_a))\
            /(1+exp((self.P_tilda-self.P_n)/self.k_a))

        #determine the frequency of spikes in the efferent sympathetic pathway
        self.f_es=np.append(self.f_es,\
                (self.f_es_inf+(self.f_es_0-self.f_es_inf)*exp(-self.k_es*self.f_cs)))
        self.f_es_min=(self.f_es_inf+(self.f_es_0-self.f_es_inf)*exp(-self.k_es*self.f_max))
        #print(self.f_es[i])
        #determine the frequency of spikes in the efferent vagal pathway
        self.f_ev=np.append(self.f_ev,\
        (self.f_ev_0+self.f_ev_inf*exp((self.f_cs-self.f_cs_0)/self.k_ev))\
            /(1+exp((self.f_cs-self.f_cs_0)/self.k_ev)))
        #return self.P_tilda,self.f_cs,self.f_es,self.f_es_min,self.f_ev
def return_heart_period(self,time_step,i):

    if (self.baro_scheme == "simple_model"):
        self.return_heart_period_control(self,time_step,i)
        self.T_counter -= 1
        if (self.T_counterr <= -self.counter_systole):
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

#def return_contractility(self,time_step,i):
#        self.return_contractility_control(self,time_step,i)
#        self.contractility_counter -= 1
#        if (self.baroreceptor_counter <= -self.counter_systole):
#            jj



def return_heart_period_control(self,time_step,i):

    if (self.baro_scheme == "simple_model"):
        def derivs(y,t):
            delta_T_prime=np.zeros(0)
            delta_T_prime[0] = self.G_T*(self.bc-self.bc)
            return delta_T_prime

        sol = solve_ivp(derivs,[0,time_step],self.delta_T_prime)
        self.delta_T_prime=sol.y[:,-1]
        self.T_prime=self.T_prime+self.delta_T_prime

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

        sol=solve_ivp(delta_T_derivs,[0,time_step], [self.delta_Ts,self.delta_Tv])
        self.y=sol.y[:,-1]
        #print(self.y)
        self.delta_Ts=self.y[0]
        self.delta_Tv=self.y[1]

        self.T_prime=self.delta_Ts+self.delta_Tv+self.T0

    return self.T, self.P_tilda,self.f_cs,self.f_es[-1],self.f_es_min,self.f_ev[-1],self.delta_Ts,self.delta_Tv

def return_contractility(self,time_step,i):

    if (self.baro_scheme == "simple_model"):
        def derivs(y,t):
            delta_c_prime=np.zeros(0)
            delta_c_prime[0] = self.G_k1*(self.bc-self.bc)
            return delta_c_prime

        sol = solve_ivp(derivs,[0,time_step],self.delta_c_prime)
        self.delta_c_prime=sol.y[:,-1]
        self.c_prime=self.c_prime+self.delta_c_prime

    if (self.baro_scheme=="Ursino_1998"):
        #update_baroreceptor(self,time_step,arterial_pressure,arterial_pressure_rate)
        #determine the outputs of static characteristics (steady-state changes)
        if i<self.D_E:
            delay_E=int(0)
        else:
            delay_E=self.D_E
        if self.f_es[i] >= self.f_es_min:
            sigma_E=self.G_E*log(self.f_es[i-delay_E]-self.f_es_min+1)
            sigma_L_factor=self.G_L*log(self.f_es[i]-self.f_es_min+1)
            sigma_k_3_factor=self.G_k3*log(self.f_es[i]-self.f_es_min+1)
            sigma_k_cb_factor=self.G_kcb*log(self.f_es[i]-self.f_es_min+1)
            sigma_k_force_factor=self.G_k_force*log(self.f_es[i]-self.f_es_min+1)
        else:
            sigma_E=0.0
            sigma_L_factor=0
            sigma_k_3_factor=0
            sigma_k_cb_factor=0
            sigma_k_force_factor=0
        #determine the elastance rate change due to sympathetic
        def derivs(y,t):
            delta=np.zeros(5)
            delta[0]=1/self.tau_E*(sigma_E-self.delta_E)
            delta[1]=1/self.tau_L*(sigma_L_factor-self.delta_L)
            delta[2]=1/self.tau_k3*(sigma_k_3_factor-self.delta_k3)
            delta[3]=1/self.tau_kcb*(sigma_k_cb_factor-self.delta_kcb)
            delta[4]=1/self.tau_k_force*(sigma_k_force_factor-self.delta_k_force)
            return delta
        initial_values=np.zeros(5)
        initial_values[0]=self.delta_E0
        initial_values[1]=self.delta_L
        initial_values[2]=self.delta_k3
        initial_values[3]=self.delta_kcb
        initial_values[4]=self.delta_k_force
        sol=solve_ivp(derivs,[0,time_step], initial_values)
        y=sol.y[:,-1]
        self.delta_E=y[0]
        self.delta_L=y[1]
        self.delta_k3=y[2]
        self.delta_kcb=y[3]
        self.delta_k_force=y[4]

        #print('delta_E',delta_E)
        E=self.delta_E+self.E_0
        self.L_scale_factor=self.delta_L+1
        self.k_3_scale_factor=self.delta_k3+1
        self.k_cb_scale_factor=self.delta_kcb+1
        self.k_force_scale_factor=self.delta_k_force+1

    return self.L_scale_factor, self.k_3_scale_factor, self.k_cb_scale_factor,self.k_force_scale_factor

def return_activation(self):
    if (self.baro_scheme=="fixed_heart_rate"):
        #print('fixed heart rate is activated')
        predefined_activation_level =\
            0.5*(1+signal.square(np.pi+2*np.pi*self.activation_frequency*self.t,
            duty=self.activation_duty_ratio))
        self.activation_level = predefined_activation_level[self.activation_counter]
        self.activation_counter += 1
        return self.activation_level

    if (self.baro_scheme=="Ursino_1998"):

        self.baroreceptor_counter -= 1
        if (self.baroreceptor_counter <= 0):
            self.activation_level = 1.0
        if (self.baroreceptor_counter <= -self.counter_systole):
            self.activation_level = 0.0
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
        return self.activation_level

def update_data_holder(self,time_step):

    # Update data struct for system-control
    self.sys_time = self.sys_time + time_step
    self.data_buffer_index += 1

    self.sys_data.at[self.data_buffer_index, 'heart_period']=self.T
    self.sys_data.at[self.data_buffer_index, 'T_prime']=self.T_prime
    self.sys_data.at[self.data_buffer_index, 'P_tilda'] = self.P_tilda
    self.sys_data.at[self.data_buffer_index, 'f_cs'] = self.f_cs
#    self.sys_data.at[self.data_buffer_index, 'f_es'] = self.f_es[-1]
#    self.sys_data.at[self.data_buffer_index, 'f_es_min'] = self.f_es_min
#    self.sys_data.at[self.data_buffer_index, 'f_ev'] = self.f_ev[-1]
#    self.sys_data.at[self.data_buffer_index, 'delta_Ts'] = self.delta_Ts
#    self.sys_data.at[self.data_buffer_index, 'delta_Tv'] = self.delta_Tv
#    self.sys_data.at[self.data_buffer_index, 'LV_elastance'] = self.E
    self.sys_data.at[self.data_buffer_index, 'L_scale_factor'] = self.L_scale_factor
    self.sys_data.at[self.data_buffer_index, 'k_3_scale_factor'] = self.k_3_scale_factor
    self.sys_data.at[self.data_buffer_index, 'k_cb_scale_factor'] = self.k_cb_scale_factor
    self.sys_data.at[self.data_buffer_index, 'k_force_scale_factor'] = self.k_force_scale_factor
