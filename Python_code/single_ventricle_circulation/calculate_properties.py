# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:50:06 2022

@author: ken
"""

import numpy as np

from scipy.constants import mmHg as mmHg_in_pascals

def return_wall_thickness(self, chamber_volume):
    """ returns wall thickness given internal_r """
    if (chamber_volume < 0):
        chamber_volume = 0

    # Note that volumes are in liters, dimensions are in m
    internal_r = self.return_internal_radius_for_chamber_volume(
                    chamber_volume)

    t  = np.power(0.001 * (chamber_volume +
                           self.data['ventricle_wall_volume']) /
                  ((2.0 / 3.0) * np.pi), (1.0 / 3.0)) - \
                      internal_r

    return t

def return_lv_circumference(self, chamber_volume):
    # Based on 2 pi * (internal r + 0.5 * wall thickness)
    # volume is in liters, circumference is in meters

    if (chamber_volume < 0.0):
        chamber_volume = 0

    wall_thickness = self.return_wall_thickness(chamber_volume)

    lv_circum = (2.0 * np.pi *
                 (self.return_internal_radius_for_chamber_volume(
                     chamber_volume) +
                  (0.5 * wall_thickness)))

    return lv_circum

def return_internal_radius_for_chamber_volume(self, chamber_volume):
    # Returns internal radius in meters for chamber volume in liters
    if (chamber_volume < 0):
        chamber_volume = 0

    r = np.power((3.0 * 0.001 * chamber_volume) / (2.0 * np.pi), (1.0/3.0))

    return r

def return_lv_pressure(self, chamber_volume):
    """ return pressure for a given volume """

    # Estimate the force produced at the new length
    new_lv_circumference = self.return_lv_circumference(chamber_volume)
    new_hs_length = 1e9 * new_lv_circumference / self.data['n_hs']
    delta_hsl = new_hs_length - self.hs.data['hs_length']
    f = self.hs.myof.check_myofilament_stresses(delta_hsl)
    total_stress = f['hs_stress']

    internal_r = self.return_internal_radius_for_chamber_volume(
        chamber_volume)

    wall_thickness = self.return_wall_thickness(chamber_volume)

    # Pressure from Laplaces law
    # https://www.annalsthoracicsurgery.org/action/showPdf?pii=S0003-4975%2810%2901981-8
    if (internal_r < 1e-6):
        P_in_pascals = 0
    else:
        # Check options for approximation
        P_in_pascals = ((total_stress * wall_thickness *
                         (2.0 + self.thick_wall_multiplier*(wall_thickness / internal_r))) /
                        internal_r)
    P_in_mmHg = P_in_pascals / mmHg_in_pascals

    return P_in_mmHg

