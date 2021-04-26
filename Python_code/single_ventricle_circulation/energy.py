# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 10:07:05 2021

@author: ken
"""

import scipy.constants as scipy_constants

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
                    (self.hs.myof.implementation['reference_hsl_0'] / 1e9)

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
                scipy_constants.Avogadro * \
                flux

    return ATPase
