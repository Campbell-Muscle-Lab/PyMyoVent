# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 10:07:05 2021

@author: ken
"""

import numpy as np
import pandas as pd

import scipy.constants as scipy_constants

def handle_energetics(self, time_step, new_beat):
    """ handles energertics
        new_beat is 1 if it's a new beat, 0 otherwise
        This is a signal to calculate stroke work and
        efficiency """

    # Irrespective, calculate and store myosin ATPase
    self.data['myosin_ATPase'] = self.return_myosin_ATPase()

    # It's a new beat, calculate stroke work and myosin ATPase
    if ((new_beat > 0) and (self.last_heart_beat_time > 0)):
        
        # Pull off data for energy calculations
        d_temp = self.sim_data[['time',
                               'pressure_ventricle',
                               'volume_ventricle',
                               'myosin_ATPase']]
        d_temp = d_temp[d_temp['time'].between(
            self.last_heart_beat_time, self.data['time'])]

        self.data['stroke_work'] = self.return_stroke_work(d_temp)

        myosin_used = time_step * d_temp['myosin_ATPase'].sum()

        self.data['myosin_efficiency'] = self.data['stroke_work'] / \
                                            myosin_used


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
    m_myocardium = 0.001 * self.data['ventricle_wall_volume']

    # Deduce the flux
    if (self.hs.myof.implementation['kinetic_scheme'] == '3_state_with_SRX'):
        flux = self.hs.myof.data['J_3']
    if (self.hs.myof.implementation['kinetic_scheme'] == '4_state_with_SRX'):
        flux = self.hs.myof.data['J_7']

    # Now calculate energy per second
    ATPase = d_heads * m_myocardium * \
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
