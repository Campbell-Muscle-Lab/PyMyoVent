# Code for displaying growth model
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def display_growth(data_structure, output_file_string="", signal="", t_limits=[],dpi=None):

    no_of_rows = 4
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time','ventricle_wall_thickness',data=data_structure)
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('LVW_t(mm)')#, fontsize = 10)
    ax0.tick_params(labelsize = 10)


    ax1 = f.add_subplot(spec2[1, 0])
    ax1.plot('time','ventricle_wall_volume',data=data_structure)
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('LVW vol(ml)')#, fontsize = 10)
    ax1.tick_params(labelsize = 10)

    ax2 = f.add_subplot(spec2[2, 0])
    ax2.plot('time','number_of_hs',data=data_structure)
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylabel('NHS')#, fontsize = 10)
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax2.tick_params(labelsize = 10)

    ax3 = f.add_subplot(spec2[3, 0])
    ax3.plot('time','volume_ventricle',data=data_structure)
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('LV vol(ml)')#, fontsize = 10)
    ax3.set_xlabel('time (s)')#, fontsize = 10)
    ax3.tick_params(labelsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_growth_summary(data_structure, output_file_string="",signal="",
                    t_limits=[],dpi=None):

    no_of_rows = 10
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([46, 28])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,figure=f)
    #gs=f.add_gridspec(3,1)
#    ax1 = f.add_subplot(spec2[0, 0])
#    ax1.plot('time','activation',data=data_structure)
#    ax1.set_xlabel('time (s)')
#    ax1.set_ylabel('Activation')


    ax1 = f.add_subplot(spec2[0, 0])
    #spec21 = gridspec.GridSpec(nrows=2, ncols=1, figure=ax1)

    ax1.plot('time','pressure_arteries',data=data_structure)
    if t_limits:
        ax1.set_xlim(t_limits)
    #ax1.set_xlabel('time (s)', fontsize = 15)
    ax1.set_ylabel('pressure \narteries', fontsize = 20)
    ax1.tick_params(labelsize = 25)
    ax1.set_title('Baroreceptor',fontsize=30,fontweight='bold')

    if(hasattr(data_structure,'heart_period')):

        ax2 = f.add_subplot(spec2[1, 0])
        #ax2.plot('time','heart_period',data=data_structure)
        ax2.plot('time','heart_rate',data=data_structure)
        #ax2.plot('time','cb_force_null',data=data_structure)
        if t_limits:
            ax2.set_xlim(t_limits)
        #ax2.set_xlabel('time (s)', fontsize = 20)
        #ax2.set_ylabel('heart period', fontsize = 20)
        #ax2.set_ylabel('cb force null', fontsize = 20)
        ax2.set_ylabel('heart rate', fontsize = 20)
        ax2.tick_params(labelsize = 25)

    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time','hs_force',data=data_structure, label='hs force')
    #if (signal == "stress"):
        #ax3.plot('time','hs_force_null',data=data_structure, label='hs force null')
    #ax3.set_xlabel('time (s)', fontsize = 20)
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('cell force \n(N/m2)', fontsize = 20)
    ax3.ticklabel_format(style='sci', axis='y', scilimits=(0, 0),)
    ax3.tick_params(labelsize = 25)
    ax3.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)


    ax4 = f.add_subplot(spec2[3, 0])

    if (signal == "stress"):
        ax4.plot('time', 'cb_force', data=data_structure, label='cb_force')
        ax4.plot('time','cb_force_null',data=data_structure, label='cb force null')
        ax4.set_ylabel('Active force \n(N/m2)', fontsize = 20)
    elif (signal == "ATPase") :
        ax4.plot('time', 'ATPase', data=data_structure, label='ATPase')
        ax4.plot('time','ATPase_null',data=data_structure, label='ATPase null')
        ax4.set_ylabel('ATPase (kJ)', fontsize = 20)

    if t_limits:
        ax4.set_xlim(t_limits)
    ax4.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax4.tick_params(labelsize = 25)
    ax4.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)
    ax4.set_title('Concnetric growth',fontsize=30,fontweight='bold')

    ax5 = f.add_subplot(spec2[4, 0])
    ax5.plot('time','ventricle_wall_thickness',data=data_structure, label='original')
    #ax5.plot('time','filtered_wall_thickness','r-',data=data_structure, label='filtered')
    if t_limits:
        ax5.set_xlim(t_limits)
    ax5.set_ylabel('wall thickness (m)', fontsize = 20)

    #ax4.set_xlabel('time (s)')
    ax5.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax5.tick_params(labelsize = 25)
    ax5.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)

    ax6 = f.add_subplot(spec2[5, 0])
    ax6.plot('time','ventricle_wall_volume',data=data_structure)
    if t_limits:
        ax6.set_xlim(t_limits)
    #ax5.set_xlabel('time (s)', fontsize = 20)
    ax6.set_ylabel('wall volume (L)', fontsize = 20,)
    ax6.tick_params(labelsize = 25)

    if (signal == "strain"):
        ax7 = f.add_subplot(spec2[6, 0])
        ax7.plot('time', 'cell_strain', data=data_structure, label='cell_strain')
        ax7.plot('time', 'cell_strain_null', data=data_structure, label='cell_strain null')
        if t_limits:
            ax7.set_xlim(t_limits)
        #ax9.set_xlabel('time (s)', fontsize = 20)
        ax7.set_ylabel('cell strain', fontsize = 20)
        ax7.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        ax7.tick_params(labelsize = 25)
        ax7.legend(bbox_to_anchor=(1.05, 1))



    ax7 = f.add_subplot(spec2[6, 0])
    ax7.plot('time', 'pas_force', data=data_structure, label='Passive force')
    if (signal == "stress"):
        ax7.plot('time', 'pas_force_null', data=data_structure, label='Passive force null')

    #ax6.set_xlabel('time (s)', fontsize = 15)
    if t_limits:
        ax7.set_xlim(t_limits)
    ax7.set_ylabel('Passive force \n(N/m2)', fontsize = 20)
    ax7.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax7.tick_params(labelsize = 25)
    ax7.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)
    ax7.set_title('Eccentric growth',fontsize=30,fontweight='bold')

    ax8 = f.add_subplot(spec2[7, 0])
    ax8.plot('time','number_of_hs',data=data_structure,label='original')
    #ax9.plot('time','filtered_n_hs','r-',data=data_structure,label='filtered')
    if t_limits:
        ax8.set_xlim(t_limits)
    ax8.set_ylabel('number of \n half_sarcomeres', fontsize = 20)
    ax8.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax8.tick_params(labelsize = 25)
    ax8.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)

    ax9 = f.add_subplot(spec2[8, 0])
    #ax9.plot('time', 'hs_length', data=data_structure, label='hs length')
    ax9.plot('time', 'pas_force_null', data=data_structure, label='Passive force null')
    #ax9.plot('time', 'cell_strain_null', data=data_structure, label='cell_strain null')
        #ax9.set_xlabel('time (s)', fontsize = 15)
    if t_limits:
        ax9.set_xlim(t_limits)
    ax9.set_ylabel('Passive force null', fontsize = 20)
    ax9.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax9.tick_params(labelsize = 25)
    ax9.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)

    ax10 = f.add_subplot(spec2[9, 0])
    ax10.plot('time','volume_ventricle',data=data_structure)
#    ax10.plot('time','LVEDV',data=data_structure)
#    ax10.plot('time','LVESV',data=data_structure)
    if t_limits:
        ax10.set_xlim(t_limits)
    ax10.set_xlabel('time (s)', fontsize = 20)
    ax10.set_ylabel('ventricle volume \n(L)', fontsize = 20)
    ax10.tick_params(labelsize = 25)


    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_systolic_function(data_structure, output_file_string="", t_limits=[],
                       dpi=None):

    no_of_rows = 4
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    if(hasattr(data_structure,'heart_period')):
        ax0 = f.add_subplot(spec2[0, 0])
        ax0.plot('time','heart_rate',data=data_structure)
        if t_limits:
            ax0.set_xlim(t_limits)
        ax0.set_ylabel('HR', fontsize = 10)
        #ax0.tick_params(labelsize = 25)

    ax1 = f.add_subplot(spec2[1, 0])
    ax1.plot('time', 'stroke_volume', data=data_structure, label='SV')
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('SV ($ml$)', fontsize = 10)

    """ax2 = f.add_subplot(spec2[2, 0])
    ax2.plot('time', 'cardiac_output', data=data_structure, label='CO')
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylabel('CO ($ml/min$)', fontsize = 10)"""


    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time', 'ejection_fraction', data=data_structure, label='EF')
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('EF (%)', fontsize = 10)
    ax3.set_xlabel('time (s)', fontsize = 10)



    #if data_structure["mitral_regurgitant_volume"][-1] != 0:
    ax4 = f.add_subplot(spec2[3, 0])
    ax4.plot('time', 'mitral_regurgitant_volume', data=data_structure, label='MRV')
    if t_limits:
        ax4.set_xlim(t_limits)
    ax4.set_ylabel('MRV ($ml$)', fontsize = 10)
    ax4.set_xlabel('time (s)', fontsize = 10)
    #if data_structure["aortic_regurgitant_volume"][-1] != 0:
#    ax4 = f.add_subplot(spec2[4, 0])
#    ax4.plot('time', 'aortic_regurgitant_volume', data=data_structure, label='ARV')
#    if t_limits:
#        ax4.set_xlim(t_limits)
#    ax4.set_ylabel('ARV ($ml$)', fontsize = 10)
#    ax4.set_xlabel('time (s)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_regurgitation(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 2
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([10, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time', 'mitral_regurgitant_volume', data=data_structure, label='MRV')
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('MRV (L)', fontsize = 10)

    ax1 = f.add_subplot(spec2[1, 0])
    ax1.plot('time', 'aortic_regurgitant_volume', data=data_structure, label='ARV')
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('ARV (L)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_ventricular_dimensions(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 7
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 10])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time','LVEDV',data=data_structure)
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('LVEDV ($ml$)', fontsize = 10)
    #ax0.tick_params(labelsize = 25)

    ax1 = f.add_subplot(spec2[1, 0])
    ax1.plot('time','LVEDVi',data=data_structure)
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('LVEDVi ($ml/m^2$)', fontsize = 10)
    #ax1.tick_params(labelsize = 25)

    ax2 = f.add_subplot(spec2[2, 0])
    ax2.plot('time','LVESV',data=data_structure)
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylabel('LVESV ($ml$)', fontsize = 10)
    #ax2.tick_params(labelsize = 25)

    ax3 = f.add_subplot(spec2[3, 0])
    ax3.plot('time','LVESVi',data=data_structure)
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('LVESVi ($ml/m^2$)', fontsize = 10)
    #ax3.tick_params(labelsize = 25)

    ax4 = f.add_subplot(spec2[4, 0])
    ax4.plot('time','ventricle_wall_thickness',data=data_structure)
    if t_limits:
        ax4.set_xlim(t_limits)
    ax4.set_ylabel('LVW_t(mm)', fontsize = 10)
    ax4.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    #ax4.tick_params(labelsize = 10)
    #ax4.legend(bbox_to_anchor=(1.05, 1),fontsize = 20)

    ax5=f.add_subplot(spec2[5,0])
    #ax5.plot('time','ventricle_wall_mass',data=data_structure, label="LVM")
    ax5.plot('time','ventricle_wall_mass_mean',data=data_structure, label="mean")
    if t_limits:
        ax5.set_xlim(t_limits)
    ax5.set_ylabel('LVM ($g$)', fontsize = 10)

    ax6=f.add_subplot(spec2[6,0])
    #ax6.plot('time','ventricle_wall_mass_i',data=data_structure, label="LVMi")
    ax6.plot('time','ventricle_wall_mass_i_mean',data=data_structure, label="mean")
    if t_limits:
        ax6.set_xlim(t_limits)
    ax6.set_ylabel('LVMi ($g/m^2$)', fontsize = 10)
    ax6.set_xlabel('time (s)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)
def display_ATPase(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 3])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0=f.add_subplot(spec2[0,0])
    ax0.plot('time','ATPase',data=data_structure)
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('ATPase ($kJ / s$)', fontsize = 10)
    ax0.set_xlabel('time (s)', fontsize = 10)

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
