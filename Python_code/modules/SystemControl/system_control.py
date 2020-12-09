import numpy as np
import pandas as pd
from scipy import signal

class system_control():
    """Class for baro_params"""

    from .implement import update_baroreceptor,return_heart_period,return_contractility,return_venous_compliance
    from .implement import update_ca_tran_tt,return_activation, update_data_holder,return_arteriolar_resistance
    from .implement import updat_ca_tran_two_compartment,update_mean_active_force,update_mean_passive_force,update_MAP
    from .display import display_baro_results,display_baro_results_tt, display_arterial_pressure
    from modules.SingleVentricle import SingleVentricle as sv
    def __init__(self,sys_params,hs_params,hs_class,circ_params,data_buffer_size):#,growth_activation): #baro_params
        """input constant parameters"""

        self.sys_params = sys_params
        self.hs = hs_class

        # simulation params
        sim_temp = sys_params["simulation"]

        self.T=float(sim_temp["basal_heart_period"][0])
        self.duty_ratio = float(sim_temp["duty_ratio"][0])
        self.dt = float(sim_temp["time_step"][0])
        self.no_of_time_points = int(sim_temp["no_of_time_points"][0])

        if "baroreceptor" in sys_params:

            # baroreceptor params
            baro_temp = sys_params["baroreceptor"]
            self.start_index = int(baro_temp["start_index"][0])
            memory = int(baro_temp["N_t"][0])
            #Activation function
            self.T_systole = self.duty_ratio
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.counter_systole = int(self.T_systole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
            self.T_counter = self.counter_diastole
            self.cardiac_cycle_counter = 0
            self.activation_level = 0.0
            # MAP
            self.MAP_memory = int(self.T/self.dt)
            self.pressure_arteries_array = np.zeros(self.MAP_memory)
            self.MAP_counter = self.T_counter
            self.MAP = 0
            # Mean sarcomere force
            # 1) Active force
            self.mean_active_force_memory = int(self.T/self.dt)
            self.active_force_array = np.zeros(self.mean_active_force_memory)
            self.mean_active_force_counter = self.T_counter
            self.mean_active_force = 0
            # 2) Passive force
            self.mean_passive_force_memory = int(self.T/self.dt)
            self.passive_force_array = np.zeros(self.mean_passive_force_memory)
            self.mean_passive_force_counter = self.T_counter
            self.mean_passive_force = 0

            # afferent pathway (baroreceptor control)
            self.b_max = float(baro_temp["afferent"]["b_max"][0])
            self.b_min =  float(baro_temp["afferent"]["b_min"][0])
            self.b_mid = float((self.b_max+self.b_min)/2)
            self.b = self.b_mid
            self.S = float(baro_temp["afferent"]["S"][0])
            self.P_set = float(baro_temp["afferent"]["P_set"][0])

            #efferent pathway (regulation)
                #heart period
            self.T_prime = self.T
            self.T0 = self.T
            self.G_T = float(baro_temp["efferent"]["heart_period"]["G_T"][0])
            self.T_rate_array = np.zeros(memory)
                #contractility
                    #k_1
            self.k1 = float(hs_params["myofilaments"]["k_1"][0]) #float(temp["regulation"]["k_1"]["k1"][0])
            self.k1_0 = self.k1
            self.G_k1 = float(baro_temp["efferent"]["k_1"]["G_k1"][0])
            self.k1_rate_array = np.zeros(memory)
                    #k_on
            self.k_on = float(hs_params["myofilaments"]["k_on"][0])#float(temp["regulation"]["k_3"]["k3"][0])
            self.k_on_0 = self.k_on
            self.G_k_on = float(baro_temp["efferent"]["k_on"]["G_k_on"][0])
            self.k_on_rate_array = np.zeros(memory)

                 # Ca transient
            self.kinetic_scheme = hs_params['membranes']["kinetic_scheme"][0]
            if self.kinetic_scheme == "Ten_Tusscher_2004":

                    #ca_uptake
                self.ca_uptake = float(hs_params["membranes"]["Ten_Tusscher_2004"]["Ca_Vmax_up_factor"][0])
                self.ca_uptake_0 = self.ca_uptake
                self.G_up = float(baro_temp["efferent"]["ca_uptake"]["G_up"][0])
                self.ca_uptake_rate_array = np.zeros(memory)
                        #g_cal
                self.g_cal = float(hs_params["membranes"]["Ten_Tusscher_2004"]["g_CaL_factor"][0])
                self.g_cal_0 = self.g_cal
                self.G_gcal = float(baro_temp["efferent"]["g_cal"]["G_gcal"][0])
                self.g_cal_rate_array = np.zeros(memory)

            elif self.kinetic_scheme == "simple_2_compartment":

                    #ca_uptake
                self.k_serca = float(hs_params["membranes"]['simple_2_compartment']['k_serca'][0])
                self.k_serca_0 = self.k_serca
                self.G_serca = float(baro_temp['efferent']['k_serca']['G_serca'][0])
                self.k_serca_rate_array = np.zeros(memory)
                    #ca_act
                self.k_act = float(hs_params["membranes"]['simple_2_compartment']['k_act'][0])
                self.k_act_0 = self.k_act
                self.G_act = float(baro_temp['efferent']['k_act']['G_act'][0])
                self.k_act_rate_array = np.zeros(memory)
                    # ca_leak
                self.k_leak = float(hs_params["membranes"]['simple_2_compartment']['k_leak'][0])
                self.k_leak_0 = self.k_leak
                self.G_leak = float(baro_temp['efferent']['k_leak']['G_leak'][0])
                self.k_leak_rate_array = np.zeros(memory)
                    #duty_ratio
                self.duty_ratio_0 = self.duty_ratio
                self.G_dr =  float(baro_temp['efferent']['duty_ratio']['G_dr'][0])
                self.duty_ratio_rate_array = np.zeros(memory)

                # vascular tone
                    #venous_compliance
            self.c_venous = float(circ_params["veins"]["compliance"][0])
            self.c_venous_0 = self.c_venous
            self.G_c_venous = float(baro_temp["efferent"]["c_venous"]["G_c_venous"][0])
            self.c_venous_rate_array = np.zeros(memory)
                    #arteriolar_resistance
            self.r_arteriolar = float(circ_params["arterioles"]["resistance"][0])
            self.r_arteriolar_0 = self.r_arteriolar
            self.G_r_arteriolar = float(baro_temp["efferent"]["r_arteriolar"]["G_r_arteriolar"][0])
            self.r_arteriolar_rate_array = np.zeros(memory)

        else:

            self.activation_frequency = float(1/self.T)
            self.t = self.dt*np.arange(1, self.no_of_time_points+1)
            self.start_index = 0
            self.predefined_activation_level =\
                0.5*(1+signal.square(np.pi+2*np.pi*self.activation_frequency*self.t,
                duty=self.duty_ratio))

            self.activation_counter=int(0)
            #self.sys_data = pd.DataFrame({})

            # data
        self.data_buffer_size = data_buffer_size
        self.sys_time = 0.0
        self.data_buffer_index = 0#self.start_index
        self.sys_data = pd.DataFrame({'heart_period':
                                            np.full(self.data_buffer_size,self.T),
                                            'heart_rate':
                                            np.full(self.data_buffer_size,60/self.T),
                                            'MAP':
                                            np.zeros(self.data_buffer_size),
                                            'mean_active_force':
                                            np.zeros(self.data_buffer_size),
                                            'mean_passive_force':
                                            np.zeros(self.data_buffer_size)})

        if "baroreceptor" in sys_params:

            self.sys_data['k_1'] = pd.Series(np.full(self.data_buffer_size,self.k1))
            self.sys_data['k_on'] = pd.Series(np.full(self.data_buffer_size,self.k_on))

            if self.kinetic_scheme == "Ten_Tusscher_2004":
                self.sys_data['Ca_Vmax_up_factor'] = \
                    pd.Series(np.full(self.data_buffer_size,self.hs.membr.constants[39]))
                self.sys_data['g_CaL_factor'] = \
                    pd.Series(np.full(self.data_buffer_size,self.hs.membr.constants[18]))#self.g_cal))
            elif self.kinetic_scheme == "simple_2_compartment":
                self.sys_data['k_serca'] = \
                    pd.Series(np.full(self.data_buffer_size,self.k_serca))
                self.sys_data['k_act'] = \
                    pd.Series(np.full(self.data_buffer_size,self.k_act))
                self.sys_data['k_leak'] = \
                    pd.Series(np.full(self.data_buffer_size,self.k_leak))
                self.sys_data['duty_ratio'] = \
                    pd.Series(np.full(self.data_buffer_size,self.duty_ratio))

            self.sys_data['compliance_veins'] = pd.Series(np.full(self.data_buffer_size,self.c_venous))
            self.sys_data['resistance_arterioles'] = pd.Series(np.full(self.data_buffer_size,self.r_arteriolar))
            self.sys_data['baroreceptor_output'] = pd.Series(np.zeros(self.data_buffer_size))
