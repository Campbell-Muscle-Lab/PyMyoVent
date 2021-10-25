# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 12:55:59 2021

@author: ken
"""

import matplotlib.pyplot as plt
import numpy as np

def test():
    n = 1
    hsl = np.arange(750, 1200, 1)
    print(hsl.shape)
    
    
    titin_stress = np.zeros((hsl.shape)

# collagen_stress = np.zeros(hsl.shape)

# titin_sigma = 200
# titin_l_slack = 950
# titin_exp_L = 70

# collagen_sigma = 200
# collagen_l_slack = 1000
# collagen_exp_L = 50

# for i, x in enumerate(hsl):
#     if (x > titin_l_slack):
#         titin_stress[i] = titin_sigma * \
#             (np.exp((x-titin_l_slack)/titin_exp_L)-1)
#     else:
#         titin_stress[i] = -titin_sigma * \
#             (np.exp((titin_l_slack-x)/titin_exp_L)-1)

#     if (x > collagen_l_slack):
#         collagen_stress[i] = collagen_sigma * \
#             (np.exp((x-collagen_l_slack)/collagen_exp_L)-1)
#     else:
#         titin_stress[i] = -collagen_sigma * \
#             (np.exp((collagen_l_slack-x)/collagen_exp_L)-1)

# fig, ax = plt.subplots()
# ax.plot(hsl, titin_stress)
# ax.plot(hsl, collagen_stress)

if __name__ == "__main__":
    test()
