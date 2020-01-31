import numpy as np
import pandas as pd
from scipy import signal


class system_control():
    """Class for baroreflex"""

    from .implement import update_baroreceptor,return_heart_period,return_contractility
    from .implement import return_activation, update_data_holder
    from .display import display_baro_results

    def __init__(self,baro_params,data_buffer_size):#,growth_activation): #baro_params
        """input constant parameters"""
        baroreflex = baro_params
        self.baro_scheme = baroreflex["baro_scheme"][0]
        #self.growth_activation = growth_activation

        self.T=float(baroreflex["simulation"]["basal_heart_period"][0])
        self.activation_duty_ratio = \
        float(baroreflex["simulation"]["duty_ratio"][0])
        self.dt = float(baroreflex["simulation"]["time_step"][0])

        if (self.baro_scheme == "fixed_heart_rate"):

            self.no_of_time_points = \
                int(baroreflex["simulation"]["no_of_time_points"][0])
            self.activation_frequency = float(1/self.T)
            self.activation_duty_ratio = \
                    float(baroreflex["simulation"]["duty_ratio"][0])
            self.t = self.dt*np.arange(1, self.no_of_time_points+1)
            self.predefined_activation_level =\
            0.5*(1+signal.square(np.pi+2*np.pi*self.activation_frequency*self.t,
            duty=self.activation_duty_ratio))
            self.activation_counter=int(0)
            self.sys_data = pd.DataFrame({})

        if (self.baro_scheme == "simple_baroreceptor"):
            #Activation function
            self.T_systole = self.activation_duty_ratio * self.T
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.counter_systole = int(self.T_systole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
            self.T_counter = self.counter_diastole
            self.contractility_counter = self.counter_diastole
            self.cardiac_cycle_counter = 0
            self.activation_level = 0.0

            # afferent pathway (baroreceptor control)
            self.bc = np.array([])
            self.bc_max = float(baroreflex["afferent"]["bc_max"][0])
            self.bc_min =  float(baroreflex["afferent"]["bc_min"][0])
            self.bc_mid = float((self.bc_max+self.bc_min)/2)
            self.slope = float(baroreflex["afferent"]["slope"][0])
            self.P_n = float(baroreflex["afferent"]["P_n"][0])

            #efferent pathway (regulation)
                #heart period
            self.T_prime = self.T
            self.T0 = self.T
            self.delta_T_prime = [0.0]
            self.G_T = float(baroreflex["regulation"]["heart_period"]["G_T"][0])
            D_T_in_second = float(baroreflex["regulation"]["heart_period"]["D_T"][0])
            self.D_T = int(D_T_in_second / self.dt)
            self.tau_T = float(baroreflex["regulation"]["heart_period"]["tau_T"][0])
                #contractility
                    #k_1
            self.k1 = float(baroreflex["regulation"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(baroreflex["regulation"]["k_1"]["G_k1"][0])
            D_k1_in_second = float(baroreflex["regulation"]["k_1"]["D_k1"][0])
            self.D_k1 = int(D_k1_in_second / self.dt)
            self.tau_k1 = float(baroreflex["regulation"]["k_1"]["tau_k1"][0])
            self.delta_k1=0.0
                    #k_3
            self.k3 = float(baroreflex["regulation"]["k_3"]["k3"][0])
            self.k3_0 = self.k3
            self.G_k3 = float(baroreflex["regulation"]["k_3"]["G_k3"][0])
            D_k3_in_second = float(baroreflex["regulation"]["k_3"]["D_k3"][0])
            self.D_k3 = int(D_k3_in_second / self.dt)
            self.tau_k3 = float(baroreflex["regulation"]["k_3"]["tau_k3"][0])
            self.delta_k3 = 0.0


        if (self.baro_scheme == "Ursino_1998"):

            #Activation function
            self.T0 = self.T
            self.T_prime = self.T
            self.T_systole = float(baroreflex["simulation"]["duration_of_systole"][0])
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.counter_systole = int(self.T_systole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
            self.T_counter = self.counter_diastole
            self.cardiac_cycle_counter = 0
            self.activation_level = 0.0

            #Afferent pathway
            self.tau_p = float(baroreflex["afferent"]["tau_p"][0])
            self.tau_z = float(baroreflex["afferent"]["tau_z"][0])
            self.f_min = float(baroreflex["afferent"]["f_min"][0])
            self.f_max = float(baroreflex["afferent"]["f_max"][0])
            self.P_n = float(baroreflex["afferent"]["P_n"][0])
            self.k_a = float(baroreflex["afferent"]["k_a"][0])
            self.P_tilda = [0.0]

            #Effernet sympathetic pathway
            self.f_es_inf = float(baroreflex["efferent_sym"]["f_es_inf"][0])
            self.f_es_0 = float(baroreflex["efferent_sym"]["f_es_0"][0])
            self.k_es = float(baroreflex["efferent_sym"]["k_es"][0])
            self.f_es = np.array([])

            #Efferent parasympathetic (vagal) pathway
            self.f_ev_inf = float(baroreflex["efferent_vagal"]["f_ev_inf"][0])
            self.f_ev_0 = float(baroreflex["efferent_vagal"]["f_ev_0"][0])
            self.k_ev = float(baroreflex["efferent_vagal"]["k_ev"][0])
            self.f_cs_0 = float(baroreflex["efferent_vagal"]["f_cs_0"][0])
            self.f_ev = np.array([])

            #Regulation effector for heart period and contractility
            #Sympathetic activity
                #heart period
            self.G_Ts = float(baroreflex["regulation_sym"]["heart_period"]["G_Ts"][0])
            D_Ts_in_second = float(baroreflex["regulation_sym"]["heart_period"]["D_Ts"][0])
            self.D_Ts = int(D_Ts_in_second / self.dt)
            self.tau_Ts = float(baroreflex["regulation_sym"]["heart_period"]["tau_Ts"][0])
            self.delta_Ts = 0.0
                #contractility
                    #k_1
            self.k1 = float(baroreflex["regulation_sym"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(baroreflex["regulation_sym"]["k_1"]["G_k1"][0])
            D_k1_in_second = float(baroreflex["regulation_sym"]["k_1"]["D_k1"][0])
            self.D_k1 = int(D_k1_in_second/self.dt)
            self.tau_k1 = float(baroreflex["regulation_sym"]["k_1"]["tau_k1"][0])
            self.delta_k1 =0

                    #k_3
            self.k3 = float(baroreflex["regulation_sym"]["k_3"]["k3"][0])
            self.k3_0 = self.k3
            self.G_k3 = float(baroreflex["regulation_sym"]["k_3"]["G_k3"][0])
            D_k3_in_second = float(baroreflex["regulation_sym"]["k_3"]["D_k3"][0])
            self.D_k3 = int(D_k3_in_second/self.dt)
            self.tau_k3 = float(baroreflex["regulation_sym"]["k_3"]["tau_k3"][0])
            self.delta_k3 = 0

            #Parasympathetic (vagal) activity
                #heart period
            self.G_Tv = float(baroreflex["regulation_vagal"]["G_Tv"][0])
            D_Tv_in_second = float(baroreflex["regulation_vagal"]["D_Tv"][0])
            self.D_Tv = int(D_Tv_in_second / self.dt)
            self.tau_Tv = float(baroreflex["regulation_vagal"]["tau_Tv"][0])
            self.delta_Tv = 0.0

            # data
        if (self.baro_scheme !="fixed_heart_rate"):
            self.data_buffer_size = data_buffer_size
            self.sys_time = 0.0
            self.data_buffer_index = 0
            self.sys_data = pd.DataFrame({'heart_period':
                                                np.zeros(self.data_buffer_size),
                                                'T_prime':
                                                np.zeros(self.data_buffer_size),
                                                'k_1':
                                                np.zeros(self.data_buffer_size),
                                                'k_3':
                                                np.zeros(self.data_buffer_size)})

            self.sys_data.at[0, 'heart_period'] = self.T
            self.sys_data.at[0, 'T_prime'] = self.T
            self.sys_data.at[0, 'k_1'] = self.k1
            self.sys_data.at[0, 'k_3'] = self.k3

        # Add in specific fields for each scheme
        if self.baro_scheme == "simple_baroreceptor":

            self.sys_data['baroreceptor_output'] = pd.Series(np.zeros(self.data_buffer_size))
            # initial values
            self.sys_data.at[0, 'baroreceptor_output'] = 0

        if self.baro_scheme == "Ursino_1998":

            self.sys_data['P_tilda'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['f_cs'] = pd.Series(np.zeros(self.data_buffer_size))
            # initial values
            self.sys_data.at[0, 'P_tilda'] = 0
            self.sys_data.at[0, 'f_cs'] = 0
