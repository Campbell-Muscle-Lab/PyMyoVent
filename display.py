# Code for displaying single circulation model
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def display_pv_loop(self, output_file_string):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([6, 2])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('volume_ventricle', 'pressure_ventricle', data=self.data)
    ax1.set_xlabel('Volume (liters)')
    ax1.set_ylabel('Pressure (mm Hg)')
    
    f.savefig(output_file_string)

def display_flows(self, output_file_string):

    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([6, 2])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'flow_ventricle_to_aorta', data=self.data,
             label='Ventricle to Aorta')
    ax1.plot('time', 'flow_aorta_to_arteries', data=self.data,
             label='Aorta to Arteries')
    ax1.plot('time', 'flow_arteries_to_veins', data=self.data,
             label='Arteries to Veins')
    ax1.plot('time', 'flow_veins_to_ventricle', data=self.data,
             label='Veins to Ventricle')
    ax1.legend(bbox_to_anchor=(1.05, 1))

    f.savefig(output_file_string)


def display_simulation(self, output_file_string):

    no_of_rows = 9
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 12])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'pressure_aorta', data=self.data, label='Aorta')
    ax1.plot('time', 'pressure_arteries', data=self.data, label='Arteries')
    ax1.plot('time', 'pressure_veins',  data=self.data, label='Veins')
    ax1.plot('time', 'pressure_ventricle',  data=self.data, label='Ventricle')
    ax1.set_ylabel('Pressure')
    ax1.legend(bbox_to_anchor=(1.05, 1))

    ax2 = f.add_subplot(spec2[1, 0])
    ax2.semilogy('time', 'volume_aorta', data=self.data, label='Aorta')
    ax2.semilogy('time', 'volume_arteries', data=self.data, label='Arteries')
    ax2.semilogy('time', 'volume_veins',  data=self.data, label='Veins')
    ax2.semilogy('time', 'volume_ventricle', data=self.data, label='Ventricle')
    ax2.set_ylabel('log_{10} Volume')
    ax2.set_ylim([1e-3, 10])
    ax2.set_yticks(np.array([1e-3, 1e-2, 1e-1, 1, 10]))
    ax2.legend(bbox_to_anchor=(1.05, 1))

    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time', 'activation', data=self.data, label='Activation')
    ax3.set_ylabel('Activation')
    ax3.legend(bbox_to_anchor=(1.05, 1))

    ax4 = f.add_subplot(spec2[3, 0])
    ax4.plot('time', 'Ca_conc', data=self.data, label='Ca concentration')
    ax4.set_ylabel('Concentration\n[M]')
    ax4.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax4.legend(bbox_to_anchor=(1.05, 1))

    ax5 = f.add_subplot(spec2[4, 0])
    ax5.plot('time', 'hs_length', data=self.data, label='hs_length')
    ax5.set_ylabel('Length')
    ax5.legend(bbox_to_anchor=(1.05, 1))

    ax6 = f.add_subplot(spec2[5, 0])
    ax6.plot('time', 'hs_force', data=self.data, label='Total force')
    ax6.plot('time', 'cb_force', data=self.data, label='Crossbridge force')
    ax6.plot('time', 'pas_force', data=self.data, label='Passive force')
    ax6.set_ylabel('Force')
    ax6.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax6.legend(bbox_to_anchor=(1.05, 1))

    ax7 = f.add_subplot(spec2[6, 0])
    ax7.plot('time', 'n_on', data=self.data, label='N_on')
    ax7.plot('time', 'n_off', data=self.data, label='N_off')
    ax7.plot('time', 'n_bound', data=self.data, label='N_bound')
    ax7.set_ylim([0, 1.0])
    ax7.set_ylabel('Thin filament')
    ax7.legend(bbox_to_anchor=(1.05, 1))

    ax8 = f.add_subplot(spec2[7, 0])
    ax8.plot('time', 'M_OFF', data=self.data, label='M_OFF')
    ax8.plot('time', 'M_ON', data=self.data, label='M_ON')
    ax8.plot('time', 'M_bound', data=self.data, label='M_bound')
    ax8.set_ylim([0, 1.0])
    ax8.set_ylabel('Thick filament')
    ax8.legend(bbox_to_anchor=(1.05, 1))

    ax9 = f.add_subplot(spec2[8, 0])
    ax9.plot('time', 'volume_ventricle', data=self.data, label='Ventricle')
    ax9.set_ylabel('Volume')
    ax9.legend(bbox_to_anchor=(1.05, 1))

    f.savefig(output_file_string)
