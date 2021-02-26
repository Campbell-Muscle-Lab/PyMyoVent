# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 22:51:06 2021

@author: ken
"""


class VAD():
    """ Class for VAD """

    def __init__(self, VAD_structure, parent_circulation):

        # Set the parent circulation
        self.parent_circulation = parent_circulation

        # Create a data dictionary
        self.data = dict()

        # Pull of the variables
        self.data['max_flow'] = VAD_structure['max_flow']
        self.data['pump_slope'] = VAD_structure['pump_slope']
