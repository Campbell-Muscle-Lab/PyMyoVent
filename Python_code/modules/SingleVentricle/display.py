# Code for displaying single circulation model
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def display_pv_loop(data_structure, output_file_string="", t_limits=[],
                    dpi=None):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([6, 2])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    # Check for t_limits, prune data if necessary
    if t_limits:
        t = data_structure['time']
        vi = np.nonzero((t>=t_limits[0])&(t<=t_limits[1]))
        data_structure = data_structure.iloc[vi]

    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('volume_ventricle', 'pressure_ventricle', data=data_structure)
    ax1.set_xlim([0, 1.1*np.max(data_structure['volume_ventricle'])])
    ax1.set_xlabel('Volume (liters)')
    ax1.set_ylabel('Pressure (mm Hg)')

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_flows(data_structure, output_file_string="",
                  dpi=None):

    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([6, 2])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'flow_ventricle_to_aorta', data=data_structure,
             label='Ventricle to Aorta')
    ax1.plot('time', 'flow_aorta_to_arteries', data=data_structure,
             label='Aorta to Arteries')
    ax1.plot('time', 'flow_arteries_to_arterioles', data=data_structure,
             label='Arteries to arterioles')
    ax1.plot('time', 'flow_arterioles_to_capillaries', data=data_structure,
             label='Arterioles to capillaries')
    ax1.plot('time', 'flow_capillaries_to_veins', data=data_structure,
             label='Capillaries to Veins')
    ax1.plot('time', 'flow_veins_to_ventricle', data=data_structure,
             label='Veins to Ventricle')
    ax1.legend(bbox_to_anchor=(1.05, 1))

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_simulation(data_structure, output_file_string="", t_limits=[],
                       dpi=None):

    no_of_rows = 9
    no_of_cols = 3

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([15, 10])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax_0_0 = f.add_subplot(spec2[0, 0])
    ax_0_0.plot('time', 'pressure_aorta', data=data_structure, label='Aorta')
    ax_0_0.plot('time', 'pressure_arteries', data=data_structure, label='Arteries')
    ax_0_0.plot('time', 'pressure_arterioles', data=data_structure, label='Arterioles')
    ax_0_0.plot('time', 'pressure_capillaries', data=data_structure, label='Capillaries')
    ax_0_0.plot('time', 'pressure_veins',  data=data_structure, label='Veins')
    ax_0_0.plot('time', 'pressure_ventricle',  data=data_structure, label='Ventricle')
    ax_0_0.set_ylabel('Pressure')
    if t_limits:
        ax_0_0.set_xlim(t_limits)
    ax_0_0.legend(bbox_to_anchor=(1.05, 1))

    ax_1_0 = f.add_subplot(spec2[1, 0])
    ax_1_0.semilogy('time', 'volume_aorta', data=data_structure, label='Aorta')
    ax_1_0.semilogy('time', 'volume_arteries', data=data_structure, label='Arteries')
    ax_1_0.semilogy('time', 'volume_arterioles', data=data_structure, label='Arterioles')
    ax_1_0.semilogy('time', 'volume_capillaries', data=data_structure, label='Capillaries')
    ax_1_0.semilogy('time', 'volume_veins',  data=data_structure, label='Veins')
    ax_1_0.semilogy('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    ax_1_0.set_ylabel('log_{10} Volume')
    if t_limits:
        ax_1_0.set_xlim(t_limits)
    ax_1_0.set_ylim([1e-3, 10])
    ax_1_0.set_yticks(np.array([1e-3, 1e-2, 1e-1, 1, 10]))
    ax_1_0.legend(bbox_to_anchor=(1.05, 1))

    ax_2_0 = f.add_subplot(spec2[2, 0])
    ax_2_0.plot('time', 'activation', data=data_structure, label='Activation')
    if t_limits:
        ax_2_0.set_xlim(t_limits)
    ax_2_0.set_ylabel('Activation')
    ax_2_0.legend(bbox_to_anchor=(1.05, 1))

    # Look for membrane voltage
    if ('membrane_voltage' in data_structure.columns):
        ax_3_0 = f.add_subplot(spec2[3, 0])
        ax_3_0.plot('time', 'membrane_voltage', data=data_structure, label='Voltage')
        if t_limits:
            ax_3_0.set_xlim(t_limits)
        ax_3_0.set_ylabel('Membrane\nvoltage\n(V)')
        ax_3_0.legend(bbox_to_anchor=(1.05, 1))

    ax_4_0 = f.add_subplot(spec2[4, 0])
    ax_4_0.plot('time', 'Ca_conc', data=data_structure, label='Ca concentration')
    if t_limits:
        ax_4_0.set_xlim(t_limits)
    ax_4_0.set_ylabel('Concentration\n[M]')
    ax_4_0.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax_4_0.legend(bbox_to_anchor=(1.05, 1))

    ax_5_0= f.add_subplot(spec2[5, 0])
    ax_5_0.plot('time', 'hs_length', data=data_structure, label='hs_length')
    if t_limits:
        ax_5_0.set_xlim(t_limits)
    ax_5_0.set_ylabel('Length')
    ax_5_0.legend(bbox_to_anchor=(1.05, 1))

    ax_6_0 = f.add_subplot(spec2[6, 0])
    ax_6_0.plot('time', 'hs_force', data=data_structure, label='Total force')
    ax_6_0.plot('time', 'cb_force', data=data_structure, label='Crossbridge force')
    ax_6_0.plot('time', 'pas_force', data=data_structure, label='Passive force')
    if t_limits:
        ax_6_0.set_xlim(t_limits)
    ax_6_0.set_ylabel('Force')
    ax_6_0.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax_6_0.legend(bbox_to_anchor=(1.05, 1))

    ax_7_0 = f.add_subplot(spec2[7, 0])
    ax_7_0.plot('time', 'n_on', data=data_structure, label='N_on')
    ax_7_0.plot('time', 'n_off', data=data_structure, label='N_off')
    ax_7_0.plot('time', 'n_bound', data=data_structure, label='N_bound')
    if t_limits:
        ax_7_0.set_xlim(t_limits)
    ax_7_0.set_ylim([0, 1.0])
    ax_7_0.set_ylabel('Thin filament')
    ax_7_0.legend(bbox_to_anchor=(1.05, 1))

    ax_8_0 = f.add_subplot(spec2[8, 0])
    ax_8_0.plot('time', 'M_OFF', data=data_structure, label='M_OFF')
    ax_8_0.plot('time', 'M_ON', data=data_structure, label='M_ON')
    ax_8_0.plot('time', 'M_bound', data=data_structure, label='M_bound')
    if t_limits:
        ax_8_0.set_xlim(t_limits)
    ax_8_0.set_ylim([0, 1.0])
    ax_8_0.set_ylabel('Thick filament')
    ax_8_0.legend(bbox_to_anchor=(1.05, 1))

    ax_0_1 = f.add_subplot(spec2[0, 1])
    ax_0_1.plot('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    if t_limits:
        ax_0_1.set_xlim(t_limits)
    ax_0_1.set_ylabel('Volume')
    ax_0_1.legend(bbox_to_anchor=(1.05, 1))
    
    ax_1_1 = f.add_subplot(spec2[1, 1])
    ax_1_1.plot('time', 'baroreceptor_signal', data=data_structure, label='Baroreceptor')
    if t_limits:
        ax_1_1.set_xlim(t_limits)
    ax_1_1.set_ylabel('Baroreceptor')
    ax_1_1.legend(bbox_to_anchor=(1.05, 1))
    
    ax_2_1 = f.add_subplot(spec2[2, 1])
    ax_2_1.plot('time', 'heart_rate', data=data_structure, label='heart_rate')
    if t_limits:
        ax_2_1.set_xlim(t_limits)
    ax_2_1.set_ylabel('Heart rate')
    ax_2_1.legend(bbox_to_anchor=(1.05, 1))
    
    ax_4_1 = f.add_subplot(spec2[4, 1])
    ax_4_1.plot('time', 'perturbation_volume', data=data_structure, label='perturbation_volume')
    if t_limits:
        ax_4_1.set_xlim(t_limits)
    ax_4_1.set_ylabel('Perturbation volume')
    ax_4_1.legend(bbox_to_anchor=(1.05, 1))

    ax_5_1 = f.add_subplot(spec2[5, 1])
    ax_5_1.plot('time', 'perturbation_venous_compliance', data=data_structure,
                label='pert_venous_compliance')
    if t_limits:
        ax_5_1.set_xlim(t_limits)
    ax_5_1.set_ylabel('Pert venous compliance')
    ax_5_1.legend(bbox_to_anchor=(1.05, 1))

    ax_6_1 = f.add_subplot(spec2[6, 1])
    ax_6_1.plot('time', 'perturbation_aorta_resistance', data=data_structure,
                label='pert_aorta_resistance')
    if t_limits:
        ax_6_1.set_xlim(t_limits)
    ax_6_1.set_ylabel('Pert aorta resistance')
    ax_6_1.legend(bbox_to_anchor=(1.05, 1))
    
    ax_0_2 = f.add_subplot(spec2[0, 2])
    ax_0_2.plot('time', 'growth_eccentric', data=data_structure, label='growth_eccentric')
    if t_limits:
        ax_0_2.set_xlim(t_limits)
    ax_0_2.set_ylabel('Growth concentric')
    ax_0_2.legend(bbox_to_anchor=(1.05, 1))

    

    ax_1_2 = f.add_subplot(spec2[1, 2])
    ax_1_2.plot('time', 'no_of_half_sarcomeres', data=data_structure, label='No of half_sarcomeres')
    if t_limits:
        ax_1_2.set_xlim(t_limits)
    ax_1_2.set_ylabel('No of half-sarcomeres')
    ax_1_2.legend(bbox_to_anchor=(1.05, 1))
    
    ax_2_2 = f.add_subplot(spec2[2, 2])
    ax_2_2.plot('time', 'growth_concentric', data=data_structure, label='growth_concentric')
    if t_limits:
        ax_2_2.set_xlim(t_limits)
    ax_2_2.set_ylabel('Growth concentric')
    ax_2_2.legend(bbox_to_anchor=(1.05, 1))

    ax_3_2 = f.add_subplot(spec2[3, 2])
    ax_3_2.plot('time', 'ventricle_wall_volume', data=data_structure, label='Wall volume')
    if t_limits:
        ax_3_2.set_xlim(t_limits)
    ax_3_2.set_ylabel('Wall volume')
    ax_3_2.legend(bbox_to_anchor=(1.05, 1))
    
    ax_5_2 = f.add_subplot(spec2[5, 2])
    ax_5_2.plot('time', 'venous_compliance', data=data_structure, label='Venous compliance')
    if t_limits:
        ax_5_2.set_xlim(t_limits)
    ax_5_2.set_ylabel('Venous compliance')
    ax_5_2.legend(bbox_to_anchor=(1.05, 1))

    ax_6_2 = f.add_subplot(spec2[6, 2])
    ax_6_2.plot('time', 'aorta_resistance', data=data_structure, label='Aorta resistance')
    if t_limits:
        ax_6_2.set_xlim(t_limits)
    ax_6_2.set_ylabel('Aorta resistance')
    ax_6_2.legend(bbox_to_anchor=(1.05, 1))


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
 