# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 11:04:38 2020

@author: ken
"""

import numpy as np

from scipy.integrate import odeint
from scipy.misc import derivative as dr

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def test():
    
    no_of_rows = 4
    fig = plt.figure(constrained_layout = True)
    spec = gridspec.GridSpec(figure=fig,
                             nrows = no_of_rows,
                             ncols = 1)
    ax=[]
    
    for i in np.arange(0,no_of_rows):
        ax.append(fig.add_subplot(spec[i,0]))
    
    n = 100000
    dt = 0.001
    t = np.linspace(0,(n*dt),n)
    k_baro = 2
    k_recov = 0.2
    c = np.NaN * np.ones(n)
    c[0] = 0.5
    y = np.NaN * np.ones(n)
    y_base = 60
    y_min = 40
    y_max = 150
    y[0] = y_base
    
    
    b = 0.5*np.ones(n)
    b[5000:12000]=1
    b[13000:18000]=0
    b[22000:27000]=0.85
    b[27000:35000]=0.25
    b[45000:55000]=0.75
    b[65000:66000]=1
    b[70000:71000]=0
    for i in range(82000,95000):
        b[i] = 0.5+0.25*np.sin(0.2*2*np.pi*t[i])
    

    # for i in np.arange(1,n):
    #     sol = odeint(diff_c, c[i-1], [0, dt], args=((b[i]),k_baro,k_recov))
    #     c[i] = sol[-1]
    #     y[i] = return_y(c[i], y_base, y_min, y_max)
        
    # ax[0].plot(t,b)
    # ax[0].set_ylabel('b')
    # ax[0].set_title('Baroreceptor signal, default=1 which is basal tone')
    
    # ax[1].plot(t,c)
    # ax[1].set_ylabel('c')
    # ax[1].set_title('Controller, constrained between min_bound=-1 and max_bound=1')
    
    # ax[2].plot(t,y)
    # ax[2].set_ylabel('y')
    # ax[2].set_title('Physiological signal = 2*10^c\nStarts at 2, bound between 0.2 and 20')

    x = np.arange(200)
    y = np.zeros(200)
    for i,xi in enumerate(x):
        y[i] = return_b(xi)
        
    ax[3].plot(x,y)
        

def diff_c(c,t,b,k_drive,k_recov,min_bound=-1,max_bound=1):
    dcdt = -k_recov*(c-0.5)
    if (b>=0.5):
        dcdt += k_drive*(b-0.5)*(1-c)
    else:
        dcdt += k_drive*(b-0.5)*c

    return dcdt

def return_y(c, y_base, y_min, y_max):
    if (c>=0.5):
        y = y_base + (c-0.5)*(y_max-y_base)/0.5
    else:
        y = y_base + (c-0.5)*(y_base-y_min)/0.5
        
    return y

def return_b(p):
    
    y = 1 / (1 + np.exp(-0.1*(p-90)))
    return y
    
    

if __name__ == "__main__":
    test()
