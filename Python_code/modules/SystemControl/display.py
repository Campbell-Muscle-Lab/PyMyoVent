# Code for displaying baroreceptor model
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np



def display_baro_results (data_structure, output_file_string="",dpi=300):
    no_of_rows = 7
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 10])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time','pressure_arteries',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax0.set_ylabel('$P_a$ $(mm$ $Hg)$', fontsize = 10)
    ax0.tick_params(labelsize = 10)

    if(hasattr(data_structure,'baroreceptor_output')):
        ax1 = f.add_subplot(spec2[1, 0])
        ax1.plot('time','baroreceptor_output',data=data_structure)
        #ax2.set_xlabel('time (s)', fontsize = 15)
        ax1.set_ylabel('$b$', fontsize = 10)
        ax1.tick_params(labelsize = 10)

    """ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time','heart_period',data=data_structure)
    #ax3.set_xlabel('time (s)', fontsize = 15)
    ax3.set_ylabel('Heart period\n$T (s)$', fontsize = 10)
    ax3.tick_params(labelsize = 10)"""

    ax2 = f.add_subplot(spec2[2, 0])
    ax2.plot('time','heart_rate',data=data_structure)
    #ax4.set_xlabel('time (s)', fontsize = 15)
    ax2.set_ylabel('Heart Beat (BPM)', fontsize = 10)
    ax2.tick_params(labelsize = 10)

    ax3=f.add_subplot(spec2[3,0])
    ax3.plot('time','k_1',data=data_structure)
    #ax5.set_xlabel('time (s)', fontsize = 15)
    ax3.set_ylabel('$k_1$ ($s^{-1}$)', fontsize = 10)
    ax3.tick_params(labelsize = 10)

    """ax4=f.add_subplot(spec2[4,0])
    ax4.plot('time','k_3',data=data_structure)
    #ax6.set_xlabel('time (s)', fontsize = 15)
    ax4.set_ylabel('$k_3$ ($s^{-1}$)', fontsize = 10)
    ax4.tick_params(labelsize = 10)
    #ax6.set_xlabel('time (s)', fontsize = 15)"""

    ax5=f.add_subplot(spec2[4,0])
    ax5.plot('time','k_on',data=data_structure)
    #ax6.set_xlabel('time (s)', fontsize = 15)
    ax5.set_ylabel('$k_{on}$ ($M^{-1}s^{-1}$)', fontsize = 10)
    ax5.tick_params(labelsize = 10)

    ax6=f.add_subplot(spec2[5,0])
    ax6.plot('time','Ca_Vmax_up_factor',data=data_structure)
    #ax6.set_xlabel('time (s)', fontsize = 15)
    ax6.set_ylabel('$V_{max,up}$\n ($mM.ms^{-1}$)', fontsize = 10)
    ax6.tick_params(labelsize = 10)
    ax6.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    #ax7.set_xlabel('time (s)', fontsize = 15)

    ax7=f.add_subplot(spec2[6,0])
    ax7.plot('time','g_CaL_factor',data=data_structure)
    #ax6.set_xlabel('time (s)', fontsize = 15)
    ax7.set_ylabel('$G_{CaL}$\n ($cm^3$.\u03BC$F^{-1}$.$s^{-1}$)', fontsize = 10)
    ax7.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax7.tick_params(labelsize = 10)
    ax7.set_xlabel('Time (s)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_arterial_pressure(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 6
    no_of_cols = 2

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 8])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    #PRESSURE
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time','pressure_aorta',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax1.set_ylabel('$P_aorta (mmHg)$', fontsize = 7)
    ax1.tick_params(labelsize = 10)

    ax2 = f.add_subplot(spec2[1, 0])
    ax2.plot('time','pressure_arteries',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax2.set_ylabel('P_arteries (mmHg)', fontsize = 7)
    ax2.tick_params(labelsize = 10)

    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time','pressure_arterioles',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax3.set_ylabel('P_arterioles (mmHg)', fontsize = 7)
    ax3.tick_params(labelsize = 10)

    ax4 = f.add_subplot(spec2[3, 0])
    ax4.plot('time','pressure_capillaries',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax4.set_ylabel('P_cap (mmHg)', fontsize = 7)
    ax4.tick_params(labelsize = 10)

    ax5 = f.add_subplot(spec2[4, 0])
    ax5.plot('time','pressure_veins',data=data_structure)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax5.set_ylabel('$P_v (mmHg)$', fontsize = 7)
    ax5.tick_params(labelsize = 10)

    ax6 = f.add_subplot(spec2[5, 0])
    ax6.plot('time','pressure_ventricle',data=data_structure)
    #a1.set_xlabel('time (s)', fontsize = 15)
    ax6.set_ylabel('$P_vent (mmHg)$', fontsize = 7)
    ax6.tick_params(labelsize = 10)
    ax6.set_xlabel('time (s)', fontsize = 10)

    #VOLUME

    ax7 = f.add_subplot(spec2[0, 1])
    ax7.plot('time','volume_aorta',data=data_structure)
    ax7.set_ylabel('Aorta vol (l)', fontsize = 7)
    ax7.tick_params(labelsize = 10)

    ax8 = f.add_subplot(spec2[1, 1])
    ax8.plot('time','volume_arteries',data=data_structure)
    ax8.set_ylabel('Arterial vol (l)', fontsize = 7)
    ax8.tick_params(labelsize = 10)

    ax9 = f.add_subplot(spec2[2, 1])
    ax9.plot('time','volume_arterioles',data=data_structure)
    ax9.set_ylabel('Arterioles vol (l)', fontsize = 7)
    ax9.tick_params(labelsize = 10)

    ax10 = f.add_subplot(spec2[3, 1])
    ax10.plot('time','volume_capillaries',data=data_structure)
    ax10.set_ylabel('Cap vol (l)', fontsize = 7)
    ax10.tick_params(labelsize = 10)

    ax11 = f.add_subplot(spec2[4, 1])
    ax11.plot('time','volume_veins',data=data_structure)
    ax11.set_ylabel('Venous vol (l)', fontsize = 7)
    ax11.tick_params(labelsize = 10)

    ax12 = f.add_subplot(spec2[5, 1])
    ax12.plot('time','volume_ventricle',data=data_structure)
    ax12.set_ylabel('Vent vol (l)', fontsize = 7)
    ax12.tick_params(labelsize = 10)
    ax12.set_xlabel('time (s)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def save_figure_to_file(f, im_file_string, dpi=None, verbose=1):
    # Writes an image to file

    import os
    from skimage.io import imsave

    # Check directory exists and save image file
    dir_path = os.path.dirname(im_file_string)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    if (verbose):
        print('Saving figure to to %s' % im_file_string)

    f.savefig(im_file_string, dpi=dpi)
