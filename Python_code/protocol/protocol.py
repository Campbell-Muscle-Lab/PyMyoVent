# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 15:03:44 2020

@author: ken
"""

import json

class protocol():
    
    def __init__(self, protocol_file_string):
        
        self.data = dict()
        
        with open(protocol_file_string,'r') as f:
            s = json.load(f)
            prot = s['protocol']
            for p in list(prot.keys()):
                self.data[p] = prot[p]
