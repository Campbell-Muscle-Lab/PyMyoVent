import numpy as np
import pandas as pd
from scipy import signal

class system_control():
    """Class for baro_params"""

    from .implement import update_baroreceptor,return_heart_period,return_contractility
    from .implement import return_activation, update_data_holder, return_venous_resistance
    from .display import display_baro_results, display_arterial_pressure
    from modules.SingleVentricle import SingleVentricle as sv
    def __init__(self,baro_params,hs_params,hs_class,circ_params,data_buffer_size):#,growth_activation): #baro_params
        """input constant parameters"""
        #baro_params = baro_params
        self.baro_scheme = baro_params["baro_scheme"][0]
        self.hs = hs_class

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
            self.start_index = 0
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
            self.start_index = int(temp["simulation"]["start_index"][0])
            print(self.start_index)
            memory_in_seconds = int(temp["simulation"]["memory"][0])
            memory = int(memory_in_seconds/self.dt)
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
            self.b = np.zeros(self.start_index)
            self.b_max = float(temp["afferent"]["b_max"][0])
            self.b_min =  float(temp["afferent"]["b_min"][0])
            self.b_mid = float((self.b_max+self.b_min)/2)
            self.S = float(temp["afferent"]["S"][0])
            self.P_n = float(temp["afferent"]["P_n"][0])

            #efferent pathway (regulation)
                #heart period
            self.T_prime = self.T
            self.T0 = self.T
            self.G_T = float(temp["regulation"]["heart_period"]["G_T"][0])
            self.T_rate_array = np.zeros(memory)
                #contractility
                    #k_1
            self.k1 = float(hs_params["myofilaments"]["k_1"][0]) #float(temp["regulation"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(temp["regulation"]["k_1"]["G_k1"][0])
            self.k1_rate_array = np.zeros(memory)
                    #k_3
            self.k3 = float(hs_params["myofilaments"]["k_3"][0])#float(temp["regulation"]["k_3"]["k3"][0])
            self.k3_0 = self.k3
            self.G_k3 = float(temp["regulation"]["k_3"]["G_k3"][0])
            self.k3_rate_array = np.zeros(memory)
                    #k_on
            self.k_on = float(hs_params["myofilaments"]["k_on"][0])#float(temp["regulation"]["k_3"]["k3"][0])
            self.k_on_0 = self.k_on
            self.G_k_on = float(temp["regulation"]["k_on"]["G_k_on"][0])
            self.k_on_rate_array = np.zeros(memory)
                    #ca_uptake
            self.ca_uptake = float(hs_params["membranes"]["Ten_Tusscher_2004"]["Ca_Vmax_up_factor"][0])
            self.ca_uptake_0 = self.ca_uptake
            self.G_up = float(temp["regulation"]["ca_uptake"]["G_up"][0])
            self.ca_uptake_rate_array = np.zeros(memory)
                    #g_cal
            self.g_cal = float(hs_params["membranes"]["Ten_Tusscher_2004"]["g_CaL_factor"][0])
            self.g_cal_0 = self.g_cal
            self.G_gcal = float(temp["regulation"]["g_cal"]["G_gcal"][0])
            self.g_cal_rate_array = np.zeros(memory)


            # data
        self.data_buffer_size = data_buffer_size
        self.sys_time = 0.0
        self.data_buffer_index = self.start_index
        self.sys_data = pd.DataFrame({'heart_period':
                                            np.full(self.data_buffer_size,self.T),
                                            'heart_rate':
                                            np.full(self.data_buffer_size,60/self.T)})
#        self.sys_data.at[0, 'heart_period'] = self.T
#        self.sys_data.at[0, 'heart_rate'] = 60/self.T

        if (self.baro_scheme !="fixed_heart_rate"):

            self.sys_data['k_1'] = pd.Series(np.full(self.data_buffer_size,self.k1))
            self.sys_data['k_3'] = pd.Series(np.full(self.data_buffer_size,self.k3))
            self.sys_data['k_on'] = pd.Series(np.full(self.data_buffer_size,self.k_on))
            self.sys_data['Ca_Vmax_up_factor'] = \
                pd.Series(np.full(self.data_buffer_size,self.hs.membr.constants[39]))
            self.sys_data['g_CaL_factor'] = \
                pd.Series(np.full(self.data_buffer_size,self.hs.membr.constants[18]))#self.g_cal))


            """self.sys_data.at[0, 'k_1'] = self.k1
            self.sys_data.at[0, 'k_3'] = self.k3
            self.sys_data.at[0, 'Ca_Vmax_up_factor'] = self.ca_uptake
            self.sys_data.at[0, 'g_CaL_factor'] = self.g_cal"""
        # Add in specific fields for each scheme
        if self.baro_scheme == "simple_baroreceptor":

            self.sys_data['baroreceptor_output'] = pd.Series(np.zeros(self.data_buffer_size))
    #        self.sys_data['venous_resistance'] = pd.Series(np.zeros(self.data_buffer_size))
            # initial values
            self.sys_data.at[0, 'baroreceptor_output'] = 0
    #        self.sys_data.at[0, 'venous_resistance'] = self.Rv
