import numpy as np
import pandas as pd
import cProfile
from scipy.integrate import solve_ivp
from scipy.constants import mmHg as mmHg_in_pascals

def implement_time_step(self, time_step, activation,i):
    """ Steps circulatory system forward in time """
    # Update the half-sarcomere
    self.hs.update_simulation(time_step, 0.0, activation, 1)
#    self.slack_hsl = self.hs.myof.return_hs_length_for_force(0.0)
    # steps solution forward in time
    self.v = evolve_volumes(self, time_step, self.v)
    new_lv_circumference = return_lv_circumference(self,self.v[-1])

    #calculating half-sarcomere length change with considering eccentric growth

    if self.growth_activation:
        #stress driven signal
        if self.driven_signal == "stress":
            #calculate cell stress set-point
            if self.growth_activation_array[i-1]==False:

                self.pass_force_null= np.mean(self.hs.hs_data["pas_force"][i-100000:i])
#                self.pass_force_null =3200
                self.data['pas_force_null'] = \
                pd.Series(np.full(self.output_buffer_size,self.pass_force_null))

                self.cb_force_null = np.mean(self.hs.hs_data["cb_force"][i-100000:i])
#                self.cb_force_null = 22000
                self.data['cb_force_null'] = \
                pd.Series(np.full(self.output_buffer_size,self.cb_force_null))

                self.total_force_null = np.mean(self.hs.hs_data["hs_force"][:i])
                self.data['hs_force_null'] = \
                pd.Series(np.full(self.output_buffer_size,self.total_force_null))

                print('***')
                print('Growth module is started to work!')
                print('with passive force_null of ',self.pass_force_null)
                print('and active force_null of',self.cb_force_null)
                print('and total force null of',self.total_force_null)
                print('***')


            passive_force = self.hs.myof.pas_force #f['pas_force']
            cb_force = self.hs.myof.cb_force#f['cb_force']
            total_force = self.hs.myof.total_force


            #concentric
            self.wall_thickness = \
            self.gr.return_lv_wall_thickness(time_step,cb_force,self.cb_force_null)
            #eccentric
            #new_number_of_hs = \
            self.n_hs = \
            self.gr.return_number_of_hs(time_step,passive_force,
                            self.pass_force_null,self.v[-1],self.hs.hs_length)
        #strain driven signal
        elif self.driven_signal == "strain":
#            hsl_pre_gr = 10e9*new_lv_circumference/self.gr.n_of_hs
#            self.strain = (hsl_pre_gr - self.slack_hsl)/self.slack_hsl
            if self.growth_activation_array[i-1]==False:
                self.cell_strain_null = np.mean(self.data["cell_strain"][:i])
                self.data['cell_strain_null'] = \
                pd.Series(np.full(self.output_buffer_size,self.cell_strain_null))
                print('cell_strain_null',self.cell_strain_null)
            #concentric
            self.wall_thickness = \
            self.gr.return_lv_wall_thickness_strain(time_step,self.strain,self.cell_strain_null)
            #eccentric
            #new_number_of_hs = \
            self.n_hs = \
            self.gr.return_number_of_hs_strain(time_step,self.strain,
            self.cell_strain_null,self.v[-1],self.hs.hs_length)


#        self.ventricle_wall_volume = return_wall_volume(self, self.v[-1])
#        self.wall_thickness = return_wall_thickness(self,self.v[-1])


#        new_hs_length = 10e9*new_lv_circumference / self.n_hs#new_number_of_hs
#        delta_hsl = new_hs_length - self.hs.hs_length

    #calculating half-sarcomere length change without considering any growth
#    else:
#        delta_hsl = self.hs.hs_length *\
#            ((new_lv_circumference / self.lv_circumference) - 1.0)
    if self.growth_activation_array[-1]:
        self.ventricle_wall_volume = return_wall_volume(self, self.v[-1])
    new_hs_length = 10e9*new_lv_circumference / self.n_hs
    self.strain = (new_hs_length - self.slack_hsl)/self.slack_hsl
    delta_hsl = new_hs_length - self.hs.hs_length
    # Implements the length change on the half-sarcomere
    self.hs.update_simulation(0.0, delta_hsl, 0.0, 1)

#    total_force = self.hs.myof.total_force

    self.lv_circumference = new_lv_circumference

    # Update the pressures
    vi = range(self.no_of_compartments-1)
    for x in vi:
        self.p[x] = self.v[x] / self.compliance[x]
    self.p[-1] = return_lv_pressure(self,self.v[-1])

    "New section added by HS"
    if (self.baro_scheme !="fixed_heart_rate"):
        # Update the heart period
        arterial_pressure=self.p[1]
        #dv=derivs(self,self.v)
        flows=return_flows(self,self.v)
        arterial_pressure_rate=\
        (flows['aorta_to_arteries'] - flows['arteries_to_arterioles'])/self.compliance[1]

        self.syscon.update_baroreceptor(time_step,arterial_pressure, arterial_pressure_rate)

        heart_period = self.syscon.return_heart_period(time_step,i)

        self.hs.myof.k_1, self.hs.myof.k_3 =\
        self.syscon.return_contractility(time_step,i)




def update_data_holders(self, time_step, activation):

    # Update data structure for circulation
    self.sim_time = self.sim_time + time_step
    self.data_buffer_index = self.data_buffer_index + 1
    self.data.at[self.data_buffer_index, 'time'] = self.sim_time
    self.data.at[self.data_buffer_index, 'pressure_aorta'] = self.p[0]
    self.data.at[self.data_buffer_index, 'pressure_arteries'] = self.p[1]
    self.data.at[self.data_buffer_index, 'pressure_arterioles'] = self.p[2]
    self.data.at[self.data_buffer_index, 'pressure_capillaries'] = self.p[3]
    self.data.at[self.data_buffer_index, 'pressure_veins'] = self.p[4]
    self.data.at[self.data_buffer_index, 'pressure_ventricle'] = self.p[-1]
    self.data.at[self.data_buffer_index, 'volume_aorta'] = self.v[0]
    self.data.at[self.data_buffer_index, 'volume_arteries'] = self.v[1]
    self.data.at[self.data_buffer_index, 'volume_arterioles'] = self.v[2]
    self.data.at[self.data_buffer_index, 'volume_capillaries'] = self.v[3]
    self.data.at[self.data_buffer_index, 'volume_veins'] = self.v[4]
    self.data.at[self.data_buffer_index, 'volume_ventricle'] = self.v[-1]

    flows = return_flows(self,self.v)
    self.data.at[self.data_buffer_index, 'flow_ventricle_to_aorta'] = \
        flows['ventricle_to_aorta']
    self.data.at[self.data_buffer_index, 'flow_aorta_to_arteries'] = \
        flows['aorta_to_arteries']
    self.data.at[self.data_buffer_index, 'flow_arteries_to_arterioles'] = \
        flows['arteries_to_arterioles']
    self.data.at[self.data_buffer_index,'flow_arterioles_to_capilllaries'] = \
        flows['arterioles_to_capillaries']
    self.data.at[self.data_buffer_index, 'flow_capillaries_to_veins'] = \
        flows['capillaries_to_veins']
    self.data.at[self.data_buffer_index, 'flow_veins_to_ventricle'] = \
        flows['veins_to_ventricle']

    self.data.at[self.data_buffer_index, 'volume_perturbation'] = \
        self.volume_perturbation[self.data_buffer_index]
    self.data.at[self.data_buffer_index, 'ventricle_wall_thickness'] =\
            self.wall_thickness
    self.data.at[self.data_buffer_index, 'cell_strain'] = self.strain
    if self.growth_activation_array[-1]:
        self.data.at[self.data_buffer_index, 'ventricle_wall_volume'] =\
            self.ventricle_wall_volume
#        if self.driven_signal == "strain":
#            self.data.at[self.data_buffer_index, 'cell_strain'] = self.strain

    # Now update data structure for half_sarcomere
    self.hs.update_data_holder(time_step, activation)

    #if self.baro_scheme == "Ursino_1998":
    self.syscon.update_data_holder(time_step)

    if self.growth_activation:
        self.gr.update_data_holder(time_step)

def evolve_volumes(self,time_step,v):

    def derivs(t, v):
        # returns dv, derivative of volume
        dv = np.zeros(self.no_of_compartments)
        # First deduce flows
        flows = return_flows(self,v)
        # Different compartments
        dv[0] = flows['ventricle_to_aorta'] - flows['aorta_to_arteries']
        dv[1] = flows['aorta_to_arteries'] - flows['arteries_to_arterioles']
        dv[2] = flows['arteries_to_arterioles'] - flows['arterioles_to_capillaries']
        dv[3] = flows['arterioles_to_capillaries'] - flows['capillaries_to_veins']
        dv[4] = flows['capillaries_to_veins'] - flows['veins_to_ventricle']
        dv[-1] = flows['veins_to_ventricle'] - flows['ventricle_to_aorta']
        return dv

    sol = solve_ivp(derivs, [0, time_step], self.v)
    self.v = sol.y[:, -1]
    return self.v

def return_flows(self, v):
    # returns fluxes between different compartments

    # Calculate pressure in each compartment
    p = np.zeros(self.no_of_compartments)
    vi = range(self.no_of_compartments-1)
    for x in vi:
        p[x] = v[x] / self.compliance[x]
    p[-1] = return_lv_pressure(self, self.v[-1])

    flows = dict()

    flows['ventricle_to_aorta'] = 0.0
    if (p[-1] > p[0]):
        flows['ventricle_to_aorta'] = \
            (p[-1] - p[0]) / self.resistance[0]

    flows['aorta_to_arteries'] = \
        (p[0] - p[1]) / self.resistance[1]

    flows['arteries_to_arterioles'] = \
        (p[1] - p[2]) / self.resistance[2]

    flows['arterioles_to_capillaries'] = \
        (p[2] - p[3]) / self.resistance[3]

    flows['capillaries_to_veins'] = \
        (p[3] - p[4]) / self.resistance[4]

    flows['veins_to_ventricle'] = 0.0
    if (p[4] > p[-1]):
        flows['veins_to_ventricle'] = \
            (p[4] - p[-1]) / self.resistance[-1]

    return flows

def return_lv_circumference(self, lv_volume):
    # 0.001 below is to do with liters to meters conversion
    if (lv_volume > 0.0):
        #print('lv_volume',lv_volume)
        #print('ventricle_wall_volume',self.ventricle_wall_volume)
        lv_circum = (2.0 * np.pi *
            np.power((3 * 0.001 *
                     (lv_volume + (self.ventricle_wall_volume / 2.0))/(2 * np.pi)) , (1.0 / 3.0)))
    else:
        lv_circum = (2.0 * np.pi *
            np.power((3 * 0.001 *
                     ((self.ventricle_wall_volume / 2.0)) /
                     (2 * np.pi)) , (1.0 / 3.0)))
#       print("lv %f vwv %f" % (lv_volume,self.ventricle_wall_volume))
    return lv_circum

def return_lv_pressure(self,lv_volume):

    # Estimate the force produced at the new length
    total_force = self.hs.myof.total_force

    internal_r = np.power((3.0 * 0.001 * lv_volume) /(2.0 * np.pi), (1.0 / 3.0))

    if self.growth_activation_array[-1]==False:
        internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
        self.wall_thickness = 0.001 * self.ventricle_wall_volume / internal_area
    # Pressure from Laplace law
    P_in_pascals = 2.0 * total_force * self.wall_thickness / internal_r
    P_in_mmHg = P_in_pascals / mmHg_in_pascals

    return P_in_mmHg

def return_wall_thickness(self,lv_volume):
    total_ventricle_volume = lv_volume + self.ventricle_wall_volume
    internal_r = np.power((3.0 * 0.001 * lv_volume) /(2.0 * np.pi), (1.0 / 3.0))
    external_R = \
        np.power((3.0 * 0.001 * total_ventricle_volume) /(2.0 * np.pi), (1.0 / 3.0))
    wall_thickness = external_R - self.internal_r
    return wall_thickness

def return_wall_volume(self, lv_volume):

    internal_r = np.power((3.0 * 0.001 * lv_volume) /(2.0 * np.pi), (1.0 / 3.0))
    internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
    ventricle_wall_volume = self.wall_thickness* internal_area *1000

    return ventricle_wall_volume
