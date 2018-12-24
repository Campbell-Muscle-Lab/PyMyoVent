# Code for displaying single circulation model
import matplotlib.pyplot as plt
import numpy as np

def display_simulation(self):
    
    no_of_rows = 2
    no_of_cols = 1
    plot_counter = 0
    
    t = self.data['time']

    f,ax = plt.subplots(no_of_rows, no_of_cols)
    f.set_size_inches(11,8)

    y = self.data['pressure_aorta']
    print(np.size(y))
    
    p_aorta = ax[plot_counter].plot(t, self.data['pressure_aorta'])
    p_aorta.set_label('Aorta')
    p_arteries = ax[plot_counter].plot(t, self.data['pressure_arteries'])
    p_arteries.set_label('Arteries')
    ax[plot_counter].legend()
    
    
    print(ax)
    
    ax[1].plot(t,self.data['Ca_conc'])
#    plt.plot(t, self.data['pressure_arteries'], label='Arteries')
#    plt.plot(t, self.data['pressure_veins'],label='Veins')
#    plt.plot(t, self.data['pressure_ventricle'],label='Ventricle')
#    plt.ylabel('Pressure')
#
#    plot_counter = plot_counter + 1
#    plt.subplot(no_of_rows, no_of_cols, plot_counter)
#    plt.plot(t, self.data['volume_aorta'], label='Aorta')
#    plt.plot(t, self.data['volume_arteries'], label='Arteries')
#    plt.plot(t, self.data['volume_veins'], label='Veins')
#    plt.plot(t, self.data['volume_ventricle'], label='Ventricle')
#    plt.ylabel('Volume')
#    plt.legend()
#
#    plot_counter = plot_counter + 1
#    plt.subplot(no_of_rows, no_of_cols, plot_counter)
#    plt.plot(t, self.data['Ca_conc'], label = '[Ca^{2+}]')
#    plt.ticklabel_format(axis='y', scilimits=(0, 0))
#
#    plot_counter = plot_counter + 1
#    plt.subplot(no_of_rows, no_of_cols, plot_counter)
#    plt.plot(t, self.data['n_off'], label='n_{off}')
#    plt.plot(t, self.data['n_on'])
#    plt.legend()
#
#    plot_counter = plot_counter + 1
#    plt.subplot(no_of_rows, no_of_cols, plot_counter)
#    plt.plot(t, self.data['M_OFF'])
#    plt.plot(t, self.data['M_ON'])
#    plt.plot(t, self.data['M_bound'])
#
#    
#    
    plt.show()