# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 12:55:59 2021

@author: ken
"""

import matplotlib.pyplot as plt
import numpy as np

def test():
    """ Test """
    hsl = np.arange(800, 1200, 1)
    
    titin_stress = np.zeros(hsl.shape)
    collagen_stress = np.zeros(hsl.shape)

    titin_sigma = 120
    titin_l_slack = 950
    titin_exp_L = 75
    
    prop_fibrosis = 0.1
    collagen_sigma = 500
    collagen_l_slack = 1000
    collagen_exp_L = 45

    for i, x in enumerate(hsl):
        if (x >= titin_l_slack):
            titin_stress[i] = titin_sigma * \
                (np.exp((x-titin_l_slack)/titin_exp_L)-1)
        else:
            titin_stress[i] = -titin_sigma * \
                (np.exp((titin_l_slack-x)/titin_exp_L)-1)

        if (x >= collagen_l_slack):
            collagen_stress[i] = prop_fibrosis * collagen_sigma * \
                (np.exp((x-collagen_l_slack)/collagen_exp_L)-1)
        else:
            collagen_stress[i] = -prop_fibrosis * collagen_sigma * \
                (np.exp((collagen_l_slack-x)/collagen_exp_L)-1)
    
    fig, ax = plt.subplots()
    ax.plot(hsl, titin_stress, label='titin')
    ax.plot(hsl, collagen_stress, label='collagen')
    ax.set_ylim([-5000, 5000])
    ax.legend()

if __name__ == "__main__":
    test()
