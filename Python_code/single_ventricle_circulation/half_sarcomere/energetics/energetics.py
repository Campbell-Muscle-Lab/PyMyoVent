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
                 parent_hs):
        
        # Set the parent circulation
        self.parent_hs = parent_hs

        # Initialise the model dict
        self.model = dict()
        self.model['intracell_ATP_conc'] = \
            energetics_structure['intracell_ATP_conc']
        self.model['rate_ATP_generated'] = \
            energetics_structure['rate_ATP_generated']
        self.model['implementation'] = \
            energetics_structure['implementation']['kinetic_scheme']

        # Initialise the data dict
        self.data = dict()
        self.data['ener_intracell_ATP_conc'] = \
            self.model['intracell_ATP_conc']
        self.data['ener_rate_ATP_generated'] = \
            self.model['rate_ATP_generated']
        self.data['ener_flux_myo_ATP_consumed'] = 0
        self.data['ener_flux_SERCA_ATP_consumed'] = 0
        self.data['ener_flux_total_ATP_consumed'] = 0
        self.data['ener_flux_ATP_generated'] = 0
        self.data['ener_ATPase_to_myo'] = 0

        # Initialize ATP vectory
        self.y = np.zeros(1)

    def implement_time_step(self, time_step):
        """ updates energetic components """

        # Integrate the differential equation to get
        # new intracellular ATP concentration
        sol = odeint(self.diff_intracell_ATP_conc,
                     self.data['ener_intracell_ATP_conc'],
                     [0, time_step])
        
        self.y = sol[-1].item()

    def diff_intracell_ATP_conc(self, y, t):
        """ Differentials """

        # Calculate change in concentration of ATP as
        # moles of ATP / volume of myofibrils in liters

        v_myocyte_liters = \
            self.parent_hs.parent_circulation.data['ventricle_wall_volume'] * \
            (1.0 - self.parent_hs.myof.data['prop_fibrosis'])
            
        if (self.model['implementation'] == 'simple_2_compartment'):
            d_intracell_ATP_conc_dt = \
                (self.return_flux_ATP_generated()  + 
                     self.return_flux_myo_ATP_consumed()) / \
                     v_myocyte_liters
        elif (self.model['implementation'] == 'mito_myo_SERCA'):
            d_intracell_ATP_conc_dt = \
                (self.return_flux_ATP_generated()  + 
                     self.return_flux_myo_ATP_consumed() +
                     self.return_flux_SERCA_ATP_consumed()) / \
                     v_myocyte_liters
        else:
            print('energetics[\'implementation\']: %s not defined' %
                  self.model['implementation'])
            

        return d_intracell_ATP_conc_dt


    def update_data(self):
        """ Update data for reporting back to half-sarcomere """

        # Irrespective, calculate and store myosin ATPase
        self.data['ener_intracell_ATP_conc'] = self.y
        
        self.data['ener_flux_ATP_generated'] = self.return_flux_ATP_generated()

        self.data['ener_flux_myo_ATP_consumed'] = self.return_flux_myo_ATP_consumed()
        
        self.data['ener_flux_SERCA_ATP_consumed'] = self.return_flux_SERCA_ATP_consumed()
        
        self.data['ener_flux_total_ATP_consumed'] = \
            self.data['ener_flux_myo_ATP_consumed'] + \
                self.data['ener_flux_SERCA_ATP_consumed']

    def return_flux_ATP_generated(self):
        """ Returns rate at which ATP is generated as
            normalized rate * (1-fibrosis) * (1-prop_myofilaments) """
        
        # Calculation volume of mitochondria in m^3
        v_mitochondria = 0.001 * self.parent_hs.parent_circulation.data['ventricle_wall_volume'] * \
                            (1.0 - self.parent_hs.myof.data['prop_fibrosis']) * \
                            (1.0 - self.parent_hs.myof.data['prop_myofilaments'])

        # Deduce the rate
        flux_ATP_generated = v_mitochondria * \
            self.data['ener_rate_ATP_generated']

        return flux_ATP_generated

    def return_flux_myo_ATP_consumed(self):
        """ Returns moles of ATP consumed per s
            as product of flux through ATPase cycle (mol^-1 s^-1) and
            the number of heads corrected for Avogadro's number
            Number of heads per m^3 is (1-fibrosis) * prop_myofilaments *
            cb_number_density / l_0 [reference length]
    
            Delta_G_ATP is set in model file as Joules / mole, 45000
            https://equilibrator.weizmann.ac.il/static/classic_rxns/classic_reactions/atp.html
            """
    
        # Calculate heads per m^3
        d_heads = (1.0 - self.parent_hs.myof.data['prop_fibrosis']) * \
                    self.parent_hs.myof.data['prop_myofilaments'] * \
                    self.parent_hs.myof.data['cb_number_density'] * \
                    (1 / (1e-9 * self.parent_hs.myof.implementation['reference_hsl_0']))
    
        # Calculate volume of myocardium in m^3
        v_myocardium = 0.001 * self.parent_hs.parent_circulation.data['ventricle_wall_volume']
    
        # Deduce the flux
        if (self.parent_hs.myof.implementation['kinetic_scheme'] == '3_state_with_SRX'):
            flux = self.parent_hs.myof.data['J_4']
        if (self.parent_hs.myof.implementation['kinetic_scheme'] == '4_state_with_SRX'):
            flux = self.parent_hs.myof.data['J_7']
    
        # Now calculate energy per second
        flux_ATP_consumed = -d_heads * v_myocardium * flux  / \
            scipy_constants.Avogadro
    
        return flux_ATP_consumed
    
    def return_flux_SERCA_ATP_consumed(self):
        """ Returns moles of ATP consumed per s
            as product of 0.5 ATP per Ca2+ ion pumped
            Number of heads per m^3 is (1-fibrosis) * prop_myofilaments
            """
    
        # Calculate volume of myocytes tissue in liters
        v_myocytes_liters = (1.0 - self.parent_hs.myof.data['prop_fibrosis']) * \
                                self.parent_hs.myof.data['prop_myofilaments'] * \
                                self.parent_hs.parent_circulation.data['ventricle_wall_volume']
        
        # J_uptake is moles per second, so with 0.5 ATP per Ca2+ ion, flux is
        # vol of myocytes * 0.5 * flux
        flux_ATP_consumed = -v_myocytes_liters * 0.5 * \
            self.parent_hs.memb.data['J_uptake']
    
        return flux_ATP_consumed

    # def return_energy_consumed(self):
    #     """ Returns energy consumed by ATP """

    #     energy_consumed = -self.return_flux_ATP_consumed() * \
    #         self.model['delta_G_ATP']

    #     return energy_consumed
