import numpy as np
import pandas as pd
import cProfile
from scipy.integrate import solve_ivp
from scipy.constants import mmHg as mmHg_in_pascals

def implement_time_step(self, time_step, activation,i):
    """ Steps circulatory system forward in time """
    # Update the half-sarcomere
    self.hs.update_simulation(time_step, 0.0, activation, 1)
    #sol = solve_ivp(self.derivs, [0, time_step], self.v)
    #self.v = sol.y[:, -1]
    self.v = evolve_volumes(self, time_step, self.v)
    new_lv_circumference = return_lv_circumference(self,self.v[-1])

    #Growth module
    if self.growth_activation:
            #Calculating null stress for growth module
        if self.growth_activation_array[i-1]==False:
            self.gr.growth_driver()
        self.gr.update_growth(time_step)

        #self.wall_thickness = self.gr.wall_thickness
        self.ventricle_wall_volume = self.gr.wall_volume
#        print(self.ventricle_wall_volume)
        self.n_hs = self.gr.number_of_hs

    if self.growth_activation_array[-1]:
        #self.ventricle_wall_volume = return_wall_volume(self, self.v[-1])
        self.lv_mass , self.lv_mass_indexed = \
        return_lv_mass(self,self.ventricle_wall_volume)
    new_hs_length = 10e9*new_lv_circumference / self.n_hs
    delta_hsl = new_hs_length - self.hs.hs_length

    if self.hs.ATPase_activation:

        self.hs.ATPase = self.hs.myof.return_ATPase(self.ventricle_wall_volume)
        #self.ATPase = return_ATPase(self)
#    if self.growth_activation and self.driven_signal == "strain":
#        self.strain = (new_hs_length - self.slack_hsl)/self.slack_hsl
    # Implements the length change on the half-sarcomere
    self.hs.update_simulation(0.0, delta_hsl, 0.0, 1)

    self.lv_circumference = new_lv_circumference

    # Update the pressures
    vi = range(self.no_of_compartments-1)
    for x in vi:
        self.p[x] = self.v[x] / self.compliance[x]
    self.p[-1] = return_lv_pressure(self,self.v[-1])

    #if self.mitral_valve_perturbation[-1] != 0 or self.aortic_valve_perturbation[-1] != 0:
    if self.pert_activation:
        self.vl=return_regurgitation_volume(self,time_step,self.v)

    "New section added by HS"

    if self.baro_activation_array[-1]:

        arterial_pressure=self.p[1]
        self.syscon.update_baroreceptor(time_step,arterial_pressure)
        self.syscon.update_MAP(arterial_pressure)
        if self.baro_activation:
            # Update the heart period

            self.syscon.return_heart_period(time_step,arterial_pressure)

            self.hs.myof.k_1,self.hs.myof.k_on = \
            self.syscon.return_contractility(time_step)

            self.hs.membr.Ca_Vmax_up_factor,self.hs.membr.g_CaL_factor= \
            self.syscon.update_ca_transient(time_step)

            #self.resistance[-2] = self.syscon.return_venous_resistance(time_step,i)

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

    self.data.at[self.data_buffer_index, 'aorta_resistance'] = self.resistance[0]
    self.data.at[self.data_buffer_index, 'arteries_resistance'] = self.resistance[1]
    self.data.at[self.data_buffer_index, 'arterioles_resistance'] = self.resistance[2]
    self.data.at[self.data_buffer_index, 'capillaries_resistance'] = self.resistance[3]
    self.data.at[self.data_buffer_index, 'veins_resistance'] = self.resistance[4]
    self.data.at[self.data_buffer_index, 'ventricle_resistance'] = self.resistance[5]

    self.data.at[self.data_buffer_index, 'aorta_compliance'] = self.compliance[0]
    self.data.at[self.data_buffer_index, 'arteries_compliance'] = self.compliance[1]
    self.data.at[self.data_buffer_index, 'arterioles_compliance'] = self.compliance[2]
    self.data.at[self.data_buffer_index, 'capillaries_compliance'] = self.compliance[3]
    self.data.at[self.data_buffer_index, 'veins_compliance'] = self.compliance[4]

    #self.vl=return_regurgitation_volume(self,self.v)

    self.data.at[self.data_buffer_index, 'volume_aortic_regurgitation'] = \
                                                            1000*self.vl[0]
    self.data.at[self.data_buffer_index, 'volume_mitral_regurgitation'] = \
                                                            1000*self.vl[1]


    flows = return_flows(self,self.v)
    self.data.at[self.data_buffer_index, 'flow_ventricle_to_aorta'] = \
        flows['ventricle_to_aorta']
    self.data.at[self.data_buffer_index, 'flow_aorta_to_arteries'] = \
        flows['aorta_to_arteries']
    self.data.at[self.data_buffer_index, 'flow_arteries_to_arterioles'] = \
        flows['arteries_to_arterioles']
    self.data.at[self.data_buffer_index,'flow_arterioles_to_capillaries'] = \
        flows['arterioles_to_capillaries']
    self.data.at[self.data_buffer_index, 'flow_capillaries_to_veins'] = \
        flows['capillaries_to_veins']
    self.data.at[self.data_buffer_index, 'flow_veins_to_ventricle'] = \
        flows['veins_to_ventricle']
    if self.pert_activation:
        self.data.at[self.data_buffer_index, 'volume_perturbation'] = \
            self.volume_perturbation[self.data_buffer_index]

    if self.growth_activation_array[-1]:

        # 1000 is for coverting liter to mili liter
#        self.data.at[self.data_buffer_index, 'ventricle_wall_volume'] =\
#            self.ventricle_wall_volume
        self.data.at[self.data_buffer_index, 'ventricle_wall_thickness']=\
            self.wall_thickness
        self.data.at[self.data_buffer_index, 'ventricle_wall_mass'] =\
            self.lv_mass
        self.data.at[self.data_buffer_index, 'ventricle_wall_mass_i'] =\
            self.lv_mass_indexed

    # Now update data structure for half_sarcomere
    self.hs.update_data_holder(time_step, activation)
    #if self.baro_scheme == "simple_baroreceptor":
    if self.baro_activation_array[-1]:
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

    p[-1] = return_lv_pressure(self, v[-1])

    flows = dict()


    # Apply aortic valve perturbation if any
    if self.pert_activation:
        flows['ventricle_to_aorta'] = \
        self.aortic_valve_perturbation_factor*(p[-1] - p[0]) / self.resistance[0]
    else:
        flows['ventricle_to_aorta'] = 0

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

    #apply mitral valve perturbation if any
    if self.pert_activation:
        flows['veins_to_ventricle'] = \
        self.mitral_valve_perturbation_factor*(p[4] - p[-1]) / self.resistance[-1]
    else:
        flows['veins_to_ventricle'] = 0
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
    new_lv_circumference = return_lv_circumference(self,lv_volume)

    # Deduce relative change in hsl
    #delta_hsl = self.hs.hs_length * \
    #        ((new_lv_circumference / self.lv_circumference) - 1.0)
    new_hs_length = 10e9*new_lv_circumference / self.n_hs
    delta_hsl = new_hs_length - self.hs.hs_length

    # Estimate the force produced at the new length
    f = self.hs.myof.check_myofilament_forces(delta_hsl)
    total_force = f['total_force']


    internal_r = np.power((3.0 * 0.001 * lv_volume) /(2.0 * np.pi), (1.0 / 3.0))
    internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
    self.wall_thickness = 0.001 * self.ventricle_wall_volume / internal_area
    #if self.growth_activation_array[-1]==False:
    #    internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
    #    self.wall_thickness = 0.001 * self.ventricle_wall_volume / internal_area
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

def return_lv_mass(self,wall_volume):
    lv_mass = wall_volume * self.ventricle_wall_density #in grams
    lv_mass_indexed = lv_mass/self.body_surface_area

    return lv_mass, lv_mass_indexed

def return_regurgitation_volume(self,time_step,v):

    flows = return_flows(self,v)
    dvl=np.zeros(2)
    vl=np.zeros(2)

    dvl[0] = flows['ventricle_to_aorta']
    if dvl[0]>0:
        dvl[0]=0
        self.vl[0]=0
    vl[0]=dvl[0]*time_step+self.vl[0]

    dvl[1] = flows['veins_to_ventricle']
    if dvl[1]>0:
        dvl[1]=0
        self.vl[1]=0
    vl[1]=dvl[1]*time_step+self.vl[1]

    return vl

def return_ATPase(self):

    N0 = self.hs.cb_number_density
    delta_G = self.hs.delta_G

    L0 = 1e-9*self.hs.L0
    N_A = self.hs.N_A

    fluxes = self.hs.myof.return_fluxes(self.hs.myof.y,self.hs.Ca_conc)
    J4 = np.sum(fluxes['J4'])
    # convert liter to meter^3
    w_vol = self.ventricle_wall_volume*0.001

    ATPase = (N0 * w_vol * delta_G * J4)/(L0 * N_A)

    return ATPase

def analyze_data(self,data):
    window= 10000
    lv_ED_vol =  \
        np.array(data['volume_ventricle'].rolling(window).max())
    lv_ED_vol[:window+1] = lv_ED_vol[window]
    data["LVEDV"] = lv_ED_vol
    lv_ED_vol_i = lv_ED_vol/self.body_surface_area
    data["LVEDVi"] = lv_ED_vol_i

    lv_ES_vol =  \
        np.array(data['volume_ventricle'].rolling(window).min())
    lv_ES_vol[:window+1] = lv_ES_vol[window]
    data["LVESV"] = lv_ES_vol
    lv_ES_vol_i = lv_ES_vol/self.body_surface_area
    data["LVESVi"] = lv_ES_vol_i

    stroke_volume = lv_ED_vol-lv_ES_vol
    data['stroke_volume']=stroke_volume

    ejection_fraction = stroke_volume/lv_ED_vol*100
    data['ejection_fraction']=ejection_fraction

    data['cardiac_output'] = stroke_volume*data['heart_rate']

    window = 10000
    lv_mass_mean = \
        np.array(data['ventricle_wall_mass'].rolling(window).mean())
    lv_mass_mean[:window+1] = lv_mass_mean[window]
    data['ventricle_wall_mass_mean']=lv_mass_mean
    #self.data.loc[:10000,'ventricle_wall_mass_mean']=lv_mass_mean

    lv_mass_indexed = lv_mass_mean/self.body_surface_area
        #data['ventricle_wall_mass_i'].rolling(window=10000).mean()
    data['ventricle_wall_mass_i_mean']=lv_mass_indexed

    mitral_regurgitant_volume = \
        data['volume_mitral_regurgitation'].rolling(window=1000).min()
    data['mitral_regurgitant_volume'] = mitral_regurgitant_volume

    aortic_regurgitant_volume = \
        data['volume_aortic_regurgitation'].rolling(window=1000).min()
    data['aortic_regurgitant_volume'] = aortic_regurgitant_volume

    return data
