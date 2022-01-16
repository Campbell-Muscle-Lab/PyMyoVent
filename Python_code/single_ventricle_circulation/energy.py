# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 10:07:05 2021

@author: ken
"""

import numpy as np

from scipy.integrate import odeint

import scipy.constants as scipy_constants

class energetics():
    """ Class for the energetics component """
    
    def __init__(self, energetics_structure,
                 parent_circulation):
        
        # Set the parent circulation
        self.parent_circulation = parent_circulation

        # Initialise the model dict
        self.model = dict()
        self.model['energy_mitochondrial_ATP_rate'] = \
            energetics_structure['mitochondrial_ATP_rate']

        # Initialise the data dict
        self.data = dict()
        self.data['energy_intracell_ATP_conc'] = 0
        self.data['energy_myosin_ATPase'] = 0
        self.data['energy_mitochondrial_ATP_rate'] = 0

    def implement_time_step(self, time_step, new_beat):
        """ updates energetic components
            new beat is 1 if it is a new beat, 0 otherwise,
            and is a signal to calculate stroke work and
            efficiency """

        # Integrate the differential equation to get
        # new intracellular ATP concentration
        sol = odeint(self.diff_intracell_ATP_conc,
                     self.data['energy_intracell_ATP_conc'],
                     [0, time_step])
        
        self.data['energy_intracell_ATP_conc'] = \
            sol[-1].item()

    def diff_intracell_ATP_conc(self, y, t):
        # Differentials
        d_intracell_ATP_conc_dt = \
            self.data['energy_mitochondrial_ATP_rate'] - \
                self.return_myosin_ATPase()

        return d_intracell_ATP_conc_dt

def handle_energetics(self, time_step, new_beat):
    """ handles energertics
        new_beat is 1 if it's a new beat, 0 otherwise
        This is a signal to calculate stroke work and
        efficiency """

    # Irrespective, calculate and store myosin ATPase
    self.data['myosin_ATPase'] = self.return_myosin_ATPase()

    self.data['ATPase_to_myo'] = self.data['myosin_ATPase'] / \
        (0.001 * self.data['ventricle_wall_volume'] *
             (1.0 - self.hs.myof.data['prop_fibrosis']) *
                 self.hs.myof.data['prop_myofilaments'])


    # It's a new beat, calculate stroke work and myosin ATPase
    if ((new_beat > 0) and (self.last_heart_beat_time > 0)):
        
        # Pull off data for energy calculations
        d_temp = self.sim_data[['time',
                               'pressure_ventricle',
                               'volume_ventricle',
                               'myosin_ATPase']]
        d_temp = d_temp[d_temp['time'].between(
            self.last_heart_beat_time, self.data['time'])]

        self.data['stroke_volume'] = d_temp['volume_ventricle'].max() - \
                                        d_temp['volume_ventricle'].min()

        self.data['stroke_work'] = self.return_stroke_work(d_temp)

        self.data['ejection_fraction'] = self.data['stroke_volume'] / \
            d_temp['volume_ventricle'].max()

        myosin_used = time_step * d_temp['myosin_ATPase'].sum()

        if (myosin_used > 0):
            self.data['myosin_efficiency'] = self.data['stroke_work'] / \
                                            myosin_used
        else:
            self.data['myosin_efficiency'] = np.nan


def return_myosin_ATPase(self):
    # Returns ATPase as product of
    # flux through ATPase cycle, the number of heads, and energy from ATP
    # Number of heads per m^3 is (1-fibrosis) * prop_myofilaments *
    # cb_number_density / l_0 [reference length]

    # Delta_G_ATP is set in model file as Joules / mole, 45000
    # https://equilibrator.weizmann.ac.il/static/classic_rxns/classic_reactions/atp.html

    # Calculate heads per m^3
    d_heads = (1.0 - self.hs.myof.data['prop_fibrosis']) * \
                self.hs.myof.data['prop_myofilaments'] * \
                self.hs.myof.data['cb_number_density'] * \
                (1 / (1e-9 * self.hs.myof.implementation['reference_hsl_0']))

    # Calculate volume of myocadium in m^3
    v_myocardium = 0.001 * self.data['ventricle_wall_volume']

    # Deduce the flux
    if (self.hs.myof.implementation['kinetic_scheme'] == '3_state_with_SRX'):
        flux = self.hs.myof.data['J_4']
    if (self.hs.myof.implementation['kinetic_scheme'] == '4_state_with_SRX'):
        flux = self.hs.myof.data['J_7']

    # Now calculate energy per second
    ATPase = d_heads * v_myocardium * \
                self.hs.myof.implementation['delta_G_ATP'] * \
                flux / scipy_constants.Avogadro

    return ATPase

def return_stroke_work(self, d_temp):
    # Calculate stroke work from p and v using shoe-string formula
    # https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates

    # Convert pressure to Pa
    p = scipy_constants.mmHg * d_temp['pressure_ventricle'].to_numpy()
    
    # Convert volume to m^3
    v = 0.001 * d_temp['volume_ventricle'].to_numpy()

    # Calculate area inside loop
    e = 0.5*np.abs(np.dot(v, np.roll(p, 1)) -
                   np.dot(p, np.roll(v,1)))

    return e
