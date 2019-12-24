import numpy as np
import pandas as pd


class system_control():
    """Class for baroreflex"""

    from .implement import update_baroreceptor,return_heart_period,return_contractility
    from .implement import return_activation, update_data_holder


    def __init__(self,baro_params,data_buffer_size): #baro_params
        """input constant parameters"""
        baroreflex = baro_params#single_circulation_simulation.baroreflex
        self.baro_scheme = baroreflex.baro_scheme.cdata

        self.T=float(baroreflex.simulation.basal_heart_period.cdata)
        self.activation_duty_ratio = \
        float(baroreflex.simulation.duty_ratio.cdata)
        self.dt = float(baroreflex.simulation.time_step.cdata)

        if (self.baro_scheme == "fixed_heart_rate"):

            self.no_of_time_points = \
                int(baroreflex.simulation.no_of_time_points.cdata)
            self.activation_frequency = float(1/self.T)
            self.activation_duty_ratio = \
                    float(baroreflex.simulation.duty_ratio.cdata)
            self.t = self.dt*np.arange(1, self.no_of_time_points+1)
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
            self.activation_level = 0.0

            # afferent pathway (baroreceptor control)
            self.bc = np.array([])
            self.bc_max = float(baroreflex.afferent.bc_max.cdata)
            self.bc_min =  float(baroreflex.afferent.bc_min.cdata)
            self.bc_mid = float((self.bc_max+self.bc_min)/2)
            self.slope = float(baroreflex.afferent.slope.cdata)
            self.P_n = float(baroreflex.afferent.P_n.cdata)

            #efferent pathway (regulation)
                #heart period
            self.T_prime = self.T
            self.T0 = self.T
            self.delta_T_prime = [0.0]
            self.G_T = float(baroreflex.regulation.heart_period.G_T.cdata)
            D_T_in_second = float(baroreflex.regulation.heart_period.D_T.cdata)
            self.D_T = int(D_T_in_second / self.dt)
            self.tau_T = float(baroreflex.regulation.heart_period.tau_T.cdata)
                #contractility
                    #k_1
            self.k1 = float(baroreflex.regulation.k_1.k1.cdata)
            self.k1_0 = self.k1
            self.G_k1 = float(baroreflex.regulation.k_1.G_k1.cdata)
            D_k1_in_second = float(baroreflex.regulation.k_1.D_k1.cdata)
            self.D_k1 = int(D_k1_in_second / self.dt)
            self.tau_k1 = float(baroreflex.regulation.k_1.tau_k1.cdata)
            self.delta_k1=0.0
                    #k_3
            self.k3 = float(baroreflex.regulation.k_3.k3.cdata)
            self.k3_0 = self.k3
            self.G_k3 = float(baroreflex.regulation.k_3.G_k3.cdata)
            D_k3_in_second = float(baroreflex.regulation.k_3.D_k3.cdata)
            self.D_k3 = int(D_k3_in_second / self.dt)
            self.tau_k3 = float(baroreflex.regulation.k_3.tau_k3.cdata)
            self.delta_k3 = 0.0


        if (self.baro_scheme == "Ursino_1998"):

            #Activation function
            self.dt = float(baroreflex.simulation.time_step.cdata)
            self.T = float(baroreflex.simulation.basal_heart_period.cdata)
            self.T0 = self.T
            self.T_prime = self.T
            self.T_systole = float(baroreflex.simulation.duration_of_systole.cdata)
            self.T_diastole = self.T-self.T_systole
            self.counter_diastole = int(self.T_diastole/self.dt)
            self.counter_systole = int(self.T_systole/self.dt)
            self.baroreceptor_counter = self.counter_diastole
            self.T_counter = self.counter_diastole
            self.activation_level = 0.0

            #Afferent pathway
            self.tau_p = float(baroreflex.afferent.tau_p.cdata)
            self.tau_z = float(baroreflex.afferent.tau_z.cdata)
            self.f_min = float(baroreflex.afferent.f_min.cdata)
            self.f_max = float(baroreflex.afferent.f_max.cdata)
            self.P_n = float(baroreflex.afferent.P_n.cdata)
            self.k_a = float(baroreflex.afferent.k_a.cdata)
            self.P_tilda = [0.0]

            #Effernet sympathetic pathway
            self.f_es_inf = float(baroreflex.efferent_sym.f_es_inf.cdata)
            self.f_es_0 = float(baroreflex.efferent_sym.f_es_0.cdata)
            self.k_es = float(baroreflex.efferent_sym.k_es.cdata)
            self.f_es = np.array([])

            #Efferent parasympathetic (vagal) pathway
            self.f_ev_inf = float(baroreflex.efferent_vagal.f_ev_inf.cdata)
            self.f_ev_0 = float(baroreflex.efferent_vagal.f_ev_0.cdata)
            self.k_ev = float(baroreflex.efferent_vagal.k_ev.cdata)
            self.f_cs_0 = float(baroreflex.efferent_vagal.f_cs_0.cdata)
            self.f_ev = np.array([])

            #Regulation effector for heart period and contractility
            #Sympathetic activity
                #heart period
            self.G_Ts = float(baroreflex.regulation_sym.heart_period.G_Ts.cdata)
            D_Ts_in_second = float(baroreflex.regulation_sym.heart_period.D_Ts.cdata)
            self.D_Ts = int(D_Ts_in_second / self.dt)
            self.tau_Ts = float(baroreflex.regulation_sym.heart_period.tau_Ts.cdata)
            self.delta_Ts = 0.0
                #contractility
                    #k_1
            self.k1 = float(baroreflex.regulation_sym.k_1.k1.cdata)
            self.k1_0 = self.k1
            self.G_k1 = float(baroreflex.regulation_sym.k_1.G_k1.cdata)
            D_k1_in_second = float(baroreflex.regulation_sym.k_1.D_k1.cdata)
            self.D_k1 = int(D_k1_in_second/self.dt)
            self.tau_k1 = float(baroreflex.regulation_sym.k_1.tau_k1.cdata)
            self.delta_k1 =0

                    #k_3
            self.k3 = float(baroreflex.regulation_sym.k_3.k3.cdata)
            self.k3_0 = self.k3
            self.G_k3 = float(baroreflex.regulation_sym.k_3.G_k3.cdata)
            D_k3_in_second = float(baroreflex.regulation_sym.k_3.D_k3.cdata)
            self.D_k3 = int(D_k3_in_second/self.dt)
            self.tau_k3 = float(baroreflex.regulation_sym.k_3.tau_k3.cdata)
            self.delta_k3 = 0

            #Parasympathetic (vagal) activity
                #heart period
            self.G_Tv = float(baroreflex.regulation_vagal.G_Tv.cdata)
            D_Tv_in_second = float(baroreflex.regulation_vagal.D_Tv.cdata)
            self.D_Tv = int(D_Tv_in_second / self.dt)
            self.tau_Tv = float(baroreflex.regulation_vagal.tau_Tv.cdata)
            self.delta_Tv = 0.0


        if self.baro_scheme == "Ursino_1998" or \
            self.baro_scheme == "simple_baroreceptor":
            # data
            self.data_buffer_size = data_buffer_size
            self.sys_time = 0.0
            self.data_buffer_index = 0
            self.sys_data = pd.DataFrame({'heart_period':
                                              np.zeros(self.data_buffer_size),
                                          'T_prime':
                                              np.zeros(self.data_buffer_size),
                                          'P_tilda':
                                              np.zeros(self.data_buffer_size),
                                          'f_cs':
                                              np.zeros(self.data_buffer_size),
                                          'baroreceptor_output':
                                              np.zeros(self.data_buffer_size),
    #                                      'f_es':
    #                                          np.zeros(self.data_buffer_size),
    #                                      'f_es_min':
    #                                          np.zeros(self.data_buffer_size),
    #                                      'f_ev':
    #                                          np.zeros(self.data_buffer_size),
    #                                      'delta_Ts':
    #                                          np.zeros(self.data_buffer_size),
    #                                      'delta_Tv':
    #                                          np.zeros(self.data_buffer_size),
    #                                      'LV_elastance':
    #                                          np.zeros(self.data_buffer_size)
                                            'k_1':
                                                np.zeros(self.data_buffer_size),
                                            'k_3':
                                                np.zeros(self.data_buffer_size)})
                                        #    'L_scale_factor':
                                        #        np.zeros(self.data_buffer_size),
                                        #    'k_3_scale_factor':
                                        #        np.zeros(self.data_buffer_size),
                                        #    'k_cb_scale_factor':
                                        #        np.zeros(self.data_buffer_size),
                                        #    'k_force_scale_factor':
                                        #        np.zeros(self.data_buffer_size)})
            self.sys_data.at[0, 'heart_period'] = self.T
            self.sys_data.at[0, 'T_prime'] = self.T
            self.sys_data.at[0, 'P_tilda'] = 0
            self.sys_data.at[0, 'f_cs'] = 0
            self.sys_data.at[0, 'baroreceptor_output'] = 0
            self.sys_data.at[0, 'k_1'] = self.k1
            self.sys_data.at[0, 'k_3'] = self.k3
            #self.sys_data.at[0, 'L_scale_factor'] = 1
            #self.sys_data.at[0, 'k_3_scale_factor'] = 1
            #self.sys_data.at[0, 'k_cb_scale_factor'] = 1
            #self.sys_data.at[0, 'k_force_scale_factor'] = 1
    #        self.sys_data.at[0, 'f_es'] = 0
    #        self.sys_data.at[0, 'f_es_min'] = 0
    #        self.sys_data.at[0, 'f_ev'] = 0
    #        self.sys_data.at[0, 'delta_Ts'] = 0
    #        self.sys_data.at[0, 'delta_Tv'] = 0
    #        self.sys_data.at[0, 'LV_elastance'] = 2.392
