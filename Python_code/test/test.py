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
    
    no_of_rows = 3
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
    k_baro = 1
    k_recov = 1
    c = np.NaN * np.ones(n)
    c[0] = 0
    y = np.NaN * np.ones(n)
    y_base = 2
    y[0] = y_base * np.power(10,c[0])
    
    
    b = np.ones(n)
    b[5000:12000]=2
    b[12000:13000]=0
    b[13000:18000]=1
    b[22000:27000]=0.85
    b[27000:35000]=0.25
    b[45000:55000]=1.25
    b[65000:66000]=2
    b[70000:71000]=0
    for i in range(82000,95000):
        b[i] = 1+0.5*np.sin(0.2*2*np.pi*t[i])
    

    for i in np.arange(1,n):
        sol = odeint(diff_c, c[i-1], [0, dt], args=((b[i]),k_baro,k_recov))
        c[i] = sol[-1]
        y[i] = y_base * np.power(10,c[i])
        
    ax[0].plot(t,b)
    ax[0].set_ylabel('b')
    ax[0].set_title('Baroreceptor signal, default=1 which is basal tone')
    
    ax[1].plot(t,c)
    ax[1].set_ylabel('c')
    ax[1].set_title('Controller, constrained between min_bound=-1 and max_bound=1')
    
    ax[2].plot(t,y)
    ax[2].set_ylabel('y')
    ax[2].set_title('Physiological signal = 2*10^c\nStarts at 2, bound between 0.2 and 20')

def diff_c(c,t,b,k_drive,k_recov,min_bound=-1,max_bound=1):

    dcdt = 0
    if (b>1):
        dcdt = k_drive*(b-1)*(max_bound-c)
    if (b<1):
        dcdt = k_drive*(b-1)*(c-min_bound)
    if (b==1):
        dcdt = - k_recov*c

    return dcdt

if __name__ == "__main__":
    test()
