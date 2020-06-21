import numpy as np
import pandas as pd
from scipy import signal


class system_control():
    """Class for baro_params"""

    from .implement import update_baroreceptor,return_heart_period,return_contractility
    from .implement import return_activation, update_data_holder, return_venous_resistance
    from .display import display_baro_results, display_arterial_pressure

    def __init__(self,baro_params,hs_params,circ_params,data_buffer_size):#,growth_activation): #baro_params
        """input constant parameters"""
        #baro_params = baro_params
        self.baro_scheme = baro_params["baro_scheme"][0]

        if (self.baro_scheme == "fixed_heart_rate"):

            temp = baro_params["fixed_heart_rate"]

            self.T=float(temp["simulation"]["basal_heart_period"][0])
            self.activation_duty_ratio = \
            float(temp["simulation"]["duty_ratio"][0])
            self.dt = float(temp["simulation"]["time_step"][0])

            self.no_of_time_points = \
                int(temp["simulation"]["no_of_time_points"][0])
            self.activation_frequency = float(1/self.T)
            self.t = self.dt*np.arange(1, self.no_of_time_points+1)

            self.predefined_activation_level =\
                0.5*(1+signal.square(np.pi+2*np.pi*self.activation_frequency*self.t,
                duty=self.activation_duty_ratio))

            self.activation_counter=int(0)
            self.sys_data = pd.DataFrame({})

        if (self.baro_scheme == "simple_baroreceptor"):
            temp = baro_params["simple_baroreceptor"]

            self.T=float(temp["simulation"]["basal_heart_period"][0])
            self.activation_duty_ratio = \
            float(temp["simulation"]["duty_ratio"][0])
            self.dt = float(temp["simulation"]["time_step"][0])
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
            self.bc_max = float(temp["afferent"]["bc_max"][0])
            self.bc_min =  float(temp["afferent"]["bc_min"][0])
            self.bc_mid = float((self.bc_max+self.bc_min)/2)
            self.slope = float(temp["afferent"]["slope"][0])
            self.P_n = float(temp["afferent"]["P_n"][0])

            #efferent pathway (regulation)
                #heart period
            self.T_prime = self.T
            self.T0 = self.T
            self.delta_T_prime = [0.0]
            self.G_T = float(temp["regulation"]["heart_period"]["G_T"][0])
            D_T_in_second = float(temp["regulation"]["heart_period"]["D_T"][0])
            self.D_T = int(D_T_in_second / self.dt)
            self.tau_T = float(temp["regulation"]["heart_period"]["tau_T"][0])
                #contractility
                    #k_1
            self.k1 = float(hs_params["myofilaments"]["k_1"][0]) #float(temp["regulation"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(temp["regulation"]["k_1"]["G_k1"][0])
            D_k1_in_second = float(temp["regulation"]["k_1"]["D_k1"][0])
            self.D_k1 = int(D_k1_in_second / self.dt)
            self.tau_k1 = float(temp["regulation"]["k_1"]["tau_k1"][0])
            self.delta_k1=0.0
                    #k_3
            self.k3 = float(hs_params["myofilaments"]["k_3"][0])#float(temp["regulation"]["k_3"]["k3"][0])
            self.k3_0 = self.k3
            self.G_k3 = float(temp["regulation"]["k_3"]["G_k3"][0])
            D_k3_in_second = float(temp["regulation"]["k_3"]["D_k3"][0])
            self.D_k3 = int(D_k3_in_second / self.dt)
            self.tau_k3 = float(temp["regulation"]["k_3"]["tau_k3"][0])
            self.delta_k3 = 0.0
                    #ca_uptake
            self.ca_uptake = float(hs_params["membranes"]["Ten_Tusscher_2004"]["Ca_Vmax_up_factor"][0])
            self.ca_uptake_0 = self.ca_uptake
            self.G_up = float(temp["regulation"]["ca_uptake"]["G_up"][0])
            D_ca_uptake_in_second = float(temp["regulation"]["ca_uptake"]["D_up"][0])
            self.D_ca_uptake = int(D_ca_uptake_in_second/self.dt)
                    #g_cal
            self.g_cal = float(hs_params["membranes"]["Ten_Tusscher_2004"]["g_CaL_factor"][0])
            self.g_cal_0 = self.g_cal
            self.G_gcal = float(temp["regulation"]["g_cal"]["G_gcal"][0])
            D_gcal_in_second = float(temp["regulation"]["g_cal"]["D_gcal"][0])
            self.D_gcal = int(D_gcal_in_second/self.dt)

                    #Venous resistance
            self.Rv = float(circ_params["veins"]["resistance"][0])#float(temp["regulation"]["k_3"]["k3"][0])
            self.Rv_0 = self.Rv
            self.G_Rv = float(temp["regulation"]["Rv"]["G_Rv"][0])
            D_Rv_in_second = float(temp["regulation"]["Rv"]["D_Rv"][0])
            self.D_Rv = int(D_Rv_in_second / self.dt)

        if (self.baro_scheme == "Ursino_1998"):

            #Activation function
            self.T0 = self.T
            self.T_prime = self.T
            self.T_systole = float(baro_params["simulation"]["duration_of_systole"][0])
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.counter_systole = int(self.T_systole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
            self.T_counter = self.counter_diastole
            self.cardiac_cycle_counter = 0
            self.activation_level = 0.0

            #Afferent pathway
            self.tau_p = float(baro_params["afferent"]["tau_p"][0])
            self.tau_z = float(baro_params["afferent"]["tau_z"][0])
            self.f_min = float(baro_params["afferent"]["f_min"][0])
            self.f_max = float(baro_params["afferent"]["f_max"][0])
            self.P_n = float(baro_params["afferent"]["P_n"][0])
            self.k_a = float(baro_params["afferent"]["k_a"][0])
            self.P_tilda = [0.0]

            #Effernet sympathetic pathway
            self.f_es_inf = float(baro_params["efferent_sym"]["f_es_inf"][0])
            self.f_es_0 = float(baro_params["efferent_sym"]["f_es_0"][0])
            self.k_es = float(baro_params["efferent_sym"]["k_es"][0])
            self.f_es = np.array([])

            #Efferent parasympathetic (vagal) pathway
            self.f_ev_inf = float(baro_params["efferent_vagal"]["f_ev_inf"][0])
            self.f_ev_0 = float(baro_params["efferent_vagal"]["f_ev_0"][0])
            self.k_ev = float(baro_params["efferent_vagal"]["k_ev"][0])
            self.f_cs_0 = float(baro_params["efferent_vagal"]["f_cs_0"][0])
            self.f_ev = np.array([])

            #Regulation effector for heart period and contractility
            #Sympathetic activity
                #heart period
            self.G_Ts = float(baro_params["regulation_sym"]["heart_period"]["G_Ts"][0])
            D_Ts_in_second = float(baro_params["regulation_sym"]["heart_period"]["D_Ts"][0])
            self.D_Ts = int(D_Ts_in_second / self.dt)
            self.tau_Ts = float(baro_params["regulation_sym"]["heart_period"]["tau_Ts"][0])
            self.delta_Ts = 0.0
                #contractility
                    #k_1
            self.k1 = float(baro_params["regulation_sym"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(baro_params["regulation_sym"]["k_1"]["G_k1"][0])
            D_k1_in_second = float(baro_params["regulation_sym"]["k_1"]["D_k1"][0])
            self.D_k1 = int(D_k1_in_second/self.dt)
            self.tau_k1 = float(baro_params["regulation_sym"]["k_1"]["tau_k1"][0])
            self.delta_k1 =0

                    #k_3
            self.k3 = float(baro_params["regulation_sym"]["k_3"]["k3"][0])
            self.k3_0 = self.k3
            self.G_k3 = float(baro_params["regulation_sym"]["k_3"]["G_k3"][0])
            D_k3_in_second = float(baro_params["regulation_sym"]["k_3"]["D_k3"][0])
            self.D_k3 = int(D_k3_in_second/self.dt)
            self.tau_k3 = float(baro_params["regulation_sym"]["k_3"]["tau_k3"][0])
            self.delta_k3 = 0

            #Parasympathetic (vagal) activity
                #heart period
            self.G_Tv = float(baro_params["regulation_vagal"]["G_Tv"][0])
            D_Tv_in_second = float(baro_params["regulation_vagal"]["D_Tv"][0])
            self.D_Tv = int(D_Tv_in_second / self.dt)
            self.tau_Tv = float(baro_params["regulation_vagal"]["tau_Tv"][0])
            self.delta_Tv = 0.0

            # data
        self.data_buffer_size = data_buffer_size
        self.sys_time = 0.0
        self.data_buffer_index = 0
        self.sys_data = pd.DataFrame({'heart_period':
                                            np.zeros(self.data_buffer_size)})
        self.sys_data.at[0, 'heart_period'] = self.T
        self.sys_data.at[0, 'heart_rate'] = 60/self.T

        if (self.baro_scheme !="fixed_heart_rate"):

            self.sys_data['k_1'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['k_3'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['Ca_Vmax_up_factor'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['g_CaL_factor'] = pd.Series(np.zeros(self.data_buffer_size))


            self.sys_data.at[0, 'k_1'] = self.k1
            self.sys_data.at[0, 'k_3'] = self.k3
            self.sys_data.at[0, 'Ca_Vmax_up_factor'] = self.ca_uptake
            self.sys_data.at[0, 'g_CaL_factor'] = self.g_cal
        # Add in specific fields for each scheme
        if self.baro_scheme == "simple_baroreceptor":

            self.sys_data['baroreceptor_output'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['venous_resistance'] = pd.Series(np.zeros(self.data_buffer_size))
            # initial values
            self.sys_data.at[0, 'baroreceptor_output'] = 0
            self.sys_data.at[0, 'venous_resistance'] = self.Rv
        if self.baro_scheme == "Ursino_1998":

            self.sys_data['P_tilda'] = pd.Series(np.zeros(self.data_buffer_size))
            self.sys_data['f_cs'] = pd.Series(np.zeros(self.data_buffer_size))
            # initial values
            self.sys_data.at[0, 'P_tilda'] = 0
            self.sys_data.at[0, 'f_cs'] = 0
