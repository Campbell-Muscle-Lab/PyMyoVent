import numpy as np
import pandas as pd
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

        f = self.hs.myof.check_myofilament_forces(0)
        passive_force = f['pas_force']
        new_number_of_hs = \
            self.gr.return_number_of_hs(time_step,passive_force)

        new_hs_length = 10e9*new_lv_circumference / new_number_of_hs
        delta_hsl = new_hs_length - self.hs.hs_length

    #calculating half-sarcomere length change without considering any growth
    else:
        delta_hsl = self.hs.hs_length *\
            ((new_lv_circumference / self.lv_circumference) - 1.0)
    # Implements the length change on the half-sarcomere
    self.hs.update_simulation(0.0, delta_hsl, 0.0, 1)

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

        self.syscon.update_baroreceptor(time_step,arterial_pressure, arterial_pressure_rate,i)

        heart_period = self.syscon.return_heart_period(time_step,i)

        k_1, k_3 =self.syscon.return_contractility(time_step,i)

        self.hs.myof.update_contractility(k_1, k_3)

    #Concentric growth
    if self.growth_activation:
        f = self.hs.myof.check_myofilament_forces(delta_hsl)
        total_force = f['total_force']

        self.ventricle_wall_volume = \
        self.gr.return_lv_mass(time_step,total_force)

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

    #self.data.at[self.data_buffer_index, 'ventricle_wall_volume'] = \
    #    self.ventricle_wall_volume
#    self.data.at[self.data_buffer_index, 'ventricle_wall_thickness'] =\
#        self.wall_thickness
#    self.data.at[self.data_buffer_index, 'slack_hsl'] =\
#        self.slack_hsl
#    self.data.at[self.data_buffer_index, 'lv_circumference'] = \
#        self.lv_circumference
#    self.data.at[self.data_buffer_index, 'slack_lv_circumference'] =\
#        self.slack_lv_circumference

    if self.growth_activation:
#        self.data.at[self.data_buffer_index, 'cell_strain'] =\
#            self.cell_strain
        self.data.at[self.data_buffer_index, 'ventricle_wall_thickness'] =\
            self.wall_thickness
#    self.data.at[self.data_buffer_index, 'ventricle_slack_volume'] = \
#        self.ventricle_slack_volume

    # Now update data structure for half_sarcomere
    self.hs.update_data_holder(time_step, activation)

    #if self.baro_scheme == "Ursino_1998":
    self.syscon.update_data_holder(time_step)

    if self.growth_activation:
        self.gr.update_data_holder(time_step)

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
    # Deduce new lv circumference
    new_lv_circumference = return_lv_circumference(self,lv_volume)

    # Deduce relative change in hsl
    delta_hsl = self.hs.hs_length * \
        ((new_lv_circumference / self.lv_circumference) - 1.0)

    # Estimate the force produced at the new length
    f = self.hs.myof.check_myofilament_forces(delta_hsl)
    total_force = f['total_force']

#      # Laplaces law says that for a sphere,
#      # P = 2 * S * w / r, where S is wall stress,
#      # w is thickness, and r is internal radius
#      r = np.power((3.0 * 0.001 * lv_volume / (2.0 * np.pi)),(1.0 / 3.0))
#        w = 0.01
#        P_in_pascals = 2 * total_force * w / r
#        P_in_mmHg = P_in_pascals / mmHg_in_pascals
        # Deduce internal radius
    internal_r = np.power((3.0 * 0.001 * lv_volume) /(2.0 * np.pi), (1.0 / 3.0))

    internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)

#    if self.growth_activation:
#        wall_thickness = self.wall_thickness
#    else:
#        wall_thickness = 0.001 * self.ventricle_wall_volume / internal_area
    self.wall_thickness = 0.001 * self.ventricle_wall_volume / internal_area

    P_in_pascals = 2.0 * total_force * self.wall_thickness / internal_r
    P_in_mmHg = P_in_pascals / mmHg_in_pascals

    return P_in_mmHg
def return_ventricle_slack_volume(self,circumference):
    ventricle_slack_volume = 2*1000*np.pi/3*np.power(circumference/(2*np.pi),3)

    return ventricle_slack_volume
