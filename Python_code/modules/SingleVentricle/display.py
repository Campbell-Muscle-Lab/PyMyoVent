# Code for displaying single circulation model
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def display_pv_loop(data_structure, output_file_string="", t_limits=[],
                    dpi=200):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([5, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])

    # Check for t_limits, prune data if necessary
    if t_limits:
        t = data_structure['time']
        for i in range(len(np.shape(t_limits))):
            vi = np.nonzero((t>=t_limits[i][0])&(t<=t_limits[i][1]))
            data_structure_new = data_structure.iloc[vi]
            x_axis = data_structure_new['volume_ventricle']
            y_axis = data_structure_new['pressure_ventricle']
            if i==0:
                label='Before applying the blood loss perturbation'
            if i==1:
                label ='After applying the blood loss perturbation'
            ax1.plot(x_axis, y_axis,label=label)
    else:
        ax1.plot('volume_ventricle', 'pressure_ventricle', data=data_structure,label='PV Loop')
    x_bound =ax1.get_xbound()
    ax1.set_xlim(0.9*x_bound[0],1.1*x_bound[1])
    #ax1.set_xlim([0, 1.1*np.max(data_structure['volume_ventricle'])])
    ax1.set_xlabel('Volume (liters)',fontsize=7)
    ax1.set_ylabel('Pressure (mm Hg)',fontsize=7)
    ax1.legend(loc='upper right',fontsize=7)
    ax1.tick_params(labelsize = 7)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_flows(data_structure, output_file_string="",
                  t_limits=[],dpi=300):

    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([7, 3])
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
    ax1.legend(bbox_to_anchor=(1.05, 1),fontsize = 7)
    ax1.tick_params(labelsize = 7)
    if t_limits:
        ax1.set_xlim(t_limits)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_pres(data_structure, output_file_string="", t_limits=[],
                       dpi=None):

    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    if t_limits:
        time_span = t_limits[1]-t_limits[0]
        plot_width = 46
    else:
        plot_width=46
    #f.set_size_inches([10, 9])
    f.set_size_inches([10, 3])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'pressure_aorta', data=data_structure, label='Aorta')
    ax1.plot('time', 'pressure_arteries', data=data_structure, label='Arteries')
    ax1.plot('time', 'pressure_arterioles', data=data_structure, label='Arterioles')
    ax1.plot('time', 'pressure_capillaries', data=data_structure, label='Capillaries')
    ax1.plot('time', 'pressure_veins',  data=data_structure, label='Veins')
    ax1.plot('time', 'pressure_ventricle',  data=data_structure, label='Ventricle')
    ax1.set_ylabel('Pressure (mmHg)', fontsize = 10)
    ax1.tick_params(labelsize = 10)
    #ax1.legend(bbox_to_anchor=(1.05, 1),ncol=2,fontsize = 10)
    if t_limits:
        ax1.set_xlim(t_limits)

    """ax2 = f.add_subplot(spec2[1, 0])
    ax2.plot('time', 'flow_ventricle_to_aorta', data=data_structure,
             label='Ventricle to Aorta')
    ax2.plot('time', 'flow_aorta_to_arteries', data=data_structure,
             label='Aorta to Arteries')
    ax2.plot('time', 'flow_arteries_to_arterioles', data=data_structure,
             label='Arteries to arterioles')
    ax2.plot('time', 'flow_arterioles_to_capillaries', data=data_structure,
             label='Arterioles to capillaries')
    ax2.plot('time', 'flow_capillaries_to_veins', data=data_structure,
             label='Capillaries to Veins')
    ax2.plot('time', 'flow_veins_to_ventricle', data=data_structure,
             label='Veins to Ventricle')
    ax2.set_ylabel('Flow', fontsize = 10)
    ax2.legend(bbox_to_anchor=(1.05, 1))
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.legend(bbox_to_anchor=(1.05, 1),ncol=2,fontsize = 10)

    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time', 'volume_aorta', data=data_structure, label='Aorta')
    ax3.plot('time', 'volume_arteries', data=data_structure, label='Arteries')
    ax3.plot('time', 'volume_arterioles', data=data_structure, label='Arterioles')
    ax3.plot('time', 'volume_capillaries', data=data_structure, label='Capillaries')
    #ax3.plot('time', 'volume_veins',  data=data_structure, label='Veins')
    ax3.plot('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    ax3.set_ylabel('Volume', fontsize = 10)
    ax3.tick_params(labelsize = 10)
    if t_limits:
        ax3.set_xlim(t_limits)
    #ax2.set_ylim([1e-3, 10])
    #ax2.set_yticks(np.array([1e-3, 1e-2, 1e-1, 1, 10]))
    ax3.legend(bbox_to_anchor=(1.05, 1),fontsize = 10, ncol=2)
    ax3.set_xlabel('time (s)',fontsize = 10)"""

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_simulation(data_structure, output_file_string="", t_limits=[],
                       dpi=None):

    no_of_rows = 10
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    if t_limits:
        time_span = t_limits[1]-t_limits[0]
        plot_width = 46
    else:
        plot_width=46
    f.set_size_inches([10, 15])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'pressure_aorta', data=data_structure, label='Aorta')
    ax1.plot('time', 'pressure_arteries', data=data_structure, label='Arteries')
    ax1.plot('time', 'pressure_arterioles', data=data_structure, label='Arterioles')
    ax1.plot('time', 'pressure_capillaries', data=data_structure, label='Capillaries')
    ax1.plot('time', 'pressure_veins',  data=data_structure, label='Veins')
    ax1.plot('time', 'pressure_ventricle',  data=data_structure, label='Ventricle')
    ax1.set_ylabel('Pressure (mmHg)', fontsize = 10)
    ax1.tick_params(labelsize = 10)
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.legend(bbox_to_anchor=(1.05, 1),ncol=2,fontsize = 10)

    ax2 = f.add_subplot(spec2[1, 0])
    ax2.semilogy('time', 'volume_aorta', data=data_structure, label='Aorta')
    ax2.semilogy('time', 'volume_arteries', data=data_structure, label='Arteries')
    ax2.semilogy('time', 'volume_arterioles', data=data_structure, label='Arterioles')
    ax2.semilogy('time', 'volume_capillaries', data=data_structure, label='Capillaries')
    ax2.semilogy('time', 'volume_veins',  data=data_structure, label='Veins')
    #ax2.semilogy('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    ax2.set_ylabel('log_{10} Volume', fontsize = 10)
    ax2.tick_params(labelsize = 10)
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylim([1e-3, 10])
    ax2.set_yticks(np.array([1e-3, 1e-2, 1e-1, 1, 10]))
    ax2.legend(bbox_to_anchor=(1.05, 1),fontsize = 10, ncol=2)

    ax3 = f.add_subplot(spec2[2, 0])
    ax3.plot('time', 'activation', data=data_structure, label='Activation')
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('Activation', fontsize = 10)
    ax3.tick_params(labelsize = 10)
    ax3.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    # Look for membrane voltage
    if ('membrane_voltage' in data_structure.columns):
        ax4 = f.add_subplot(spec2[3, 0])
        ax4.plot('time', 'membrane_voltage', data=data_structure, label='Voltage')
        if t_limits:
            ax4.set_xlim(t_limits)
        ax4.set_ylabel('Membrane\nvoltage\n(V)', fontsize = 10)
        ax4.tick_params(labelsize = 10)
        ax4.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)


    ax5 = f.add_subplot(spec2[4, 0])
    ax5.plot('time', 'Ca_conc', data=data_structure, label='Ca concentration')
    if t_limits:
        ax5.set_xlim(t_limits)
    ax5.set_ylabel('Concentration\n[M]', fontsize = 10)
    ax5.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax5.tick_params(labelsize = 10)
    ax5.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax6 = f.add_subplot(spec2[5, 0])
    ax6.plot('time', 'hs_length', data=data_structure, label='hs_length')

    if t_limits:
        ax6.set_xlim(t_limits)
    ax6.set_ylabel('Length (nm)', fontsize = 10)
    ax6.tick_params(labelsize = 10)
    ax6.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax7 = f.add_subplot(spec2[6, 0])
    ax7.plot('time', 'hs_force', data=data_structure, label='Total force')
    ax7.plot('time', 'cb_force', data=data_structure, label='Crossbridge force')
    ax7.plot('time', 'pas_force', data=data_structure, label='Passive force')
    if t_limits:
        ax7.set_xlim(t_limits)
    ax7.set_ylabel('Force (N/m2)', fontsize = 10)
    ax7.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax7.tick_params(labelsize = 10)
    ax7.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax8 = f.add_subplot(spec2[7, 0])
    ax8.plot('time', 'n_on', data=data_structure, label='N_on')
    ax8.plot('time', 'n_off', data=data_structure, label='N_off')
    ax8.plot('time', 'n_bound', data=data_structure, label='N_bound')
    if t_limits:
        ax8.set_xlim(t_limits)
    ax8.set_ylim([0, 1.0])
    ax8.set_ylabel('Thin filament', fontsize = 10)
    ax8.tick_params(labelsize = 10)
    ax8.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax9 = f.add_subplot(spec2[8, 0])
    ax9.plot('time', 'M_OFF', data=data_structure, label='M_OFF')
    ax9.plot('time', 'M_ON', data=data_structure, label='M_ON')
    ax9.plot('time', 'M_bound', data=data_structure, label='M_bound')
    if t_limits:
        ax9.set_xlim(t_limits)
    ax9.set_ylim([0, 1.0])
    ax9.set_ylabel('Thick filament', fontsize = 10)
    ax9.tick_params(labelsize = 10)
    ax9.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax10 = f.add_subplot(spec2[9, 0])
    ax10.plot('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    #ax10.plot('time','LVEDV','r-',data=data_structure, label="EDV")
    #ax10.plot('time','LVESV','r-',data=data_structure, label="ESV")
    if t_limits:
        ax10.set_xlim(t_limits)
    ax10.set_ylabel('Volume (ml)', fontsize = 10)
    ax10.tick_params(labelsize = 10)
    ax10.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_simulation_publish(data_structure, output_file_string="", t_limits=[],
                       dpi=300):

    no_of_rows = 5
    no_of_cols = 2

    f = plt.figure(constrained_layout=True)
    if t_limits:
        time_span = t_limits[1]-t_limits[0]
        plot_width = 46
    else:
        plot_width=46
    f.set_size_inches([10, 7.5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time', 'activation', data=data_structure, label='Activation')
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('Activation', fontsize = 10)
    ax0.tick_params(labelsize = 10)
    #ax0.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    if ('membrane_voltage' in data_structure.columns):
        ax1 = f.add_subplot(spec2[1, 0])
        ax1.plot('time', 'membrane_voltage', data=data_structure, label='Voltage')
        if t_limits:
            ax1.set_xlim(t_limits)
        ax1.set_ylabel('Membrane\nvoltage\n(V)', fontsize = 10)
        ax1.tick_params(labelsize = 10)
        #ax1.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax2 = f.add_subplot(spec2[2, 0])
    ax2.plot('time', 'Ca_conc', data=data_structure, label='Ca concentration')
    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylabel('Ca Concentration\n[M]', fontsize = 10)
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax2.tick_params(labelsize = 10)
    #ax2.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)


    ax3 = f.add_subplot(spec2[3, 0])
    ax3.plot('time', 'n_on', data=data_structure, label='N_on')
    ax3.plot('time', 'n_off', data=data_structure, label='N_off')
    ax3.plot('time', 'n_bound', data=data_structure, label='N_bound')
    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylim([0, 1.0])
    ax3.set_ylabel('Thin filament', fontsize = 10)
    ax3.tick_params(labelsize = 10)
    ax3.legend(bbox_to_anchor=(1.05, 1),fontsize = 7)

    ax4 = f.add_subplot(spec2[4, 0])
    ax4.plot('time', 'M_OFF', data=data_structure, label='M_OFF')
    ax4.plot('time', 'M_ON', data=data_structure, label='M_ON')
    ax4.plot('time', 'M_bound', data=data_structure, label='M_bound')
    if t_limits:
        ax4.set_xlim(t_limits)
    ax4.set_ylim([0, 1.0])
    ax4.set_ylabel('Thick filament', fontsize = 10)
    ax4.tick_params(labelsize = 10)
    ax4.legend(bbox_to_anchor=(1.05, 1),fontsize = 7)

    ax5 = f.add_subplot(spec2[0, 1])
    ax5.plot('time', 'hs_force', data=data_structure, label='Total force')
    ax5.plot('time', 'cb_force', data=data_structure, label='Crossbridge force')
    ax5.plot('time', 'pas_force', data=data_structure, label='Passive force')
    if t_limits:
        ax5.set_xlim(t_limits)
    ax5.set_ylabel('Force / unit area\n (N/m2)', fontsize = 10)
    ax5.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax5.tick_params(labelsize = 10)
    ax5.legend(bbox_to_anchor=(1.05, 1),fontsize = 7)

    ax6 = f.add_subplot(spec2[1, 1])
    ax6.plot('time', 'hs_length', data=data_structure, label='hs_length')

    if t_limits:
        ax6.set_xlim(t_limits)
    ax6.set_ylabel('half_sarcomere\nLength (nm)', fontsize = 10)
    ax6.tick_params(labelsize = 10)
    #ax6.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax7 = f.add_subplot(spec2[2, 1])
    ax7.plot('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    #ax10.plot('time','LVEDV','r-',data=data_structure, label="EDV")
    #ax10.plot('time','LVESV','r-',data=data_structure, label="ESV")
    if t_limits:
        ax7.set_xlim(t_limits)
    ax7.set_ylabel('Ventricle Volume\n (L)', fontsize = 10)
    ax7.tick_params(labelsize = 10)
    #ax7.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax8 = f.add_subplot(spec2[3, 1])
    ax8.plot('time', 'pressure_aorta', data=data_structure, label='Aorta')
    ax8.plot('time', 'pressure_arteries', data=data_structure, label='Arteries')
    ax8.plot('time', 'pressure_arterioles', data=data_structure, label='Arterioles')
    ax8.plot('time', 'pressure_capillaries', data=data_structure, label='Capillaries')
    ax8.plot('time', 'pressure_veins',  data=data_structure, label='Veins')
    ax8.plot('time', 'pressure_ventricle',  data=data_structure, label='Ventricle')
    ax8.set_ylabel('Pressure \n(mmHg)', fontsize = 10)
    ax8.tick_params(labelsize = 10)
    if t_limits:
        ax8.set_xlim(t_limits)
    ax8.legend(bbox_to_anchor=(1.05, 1),ncol=2,fontsize = 7)
    ax8.set_xlabel('time (s)',fontsize = 10)

    ax9 = f.add_subplot(spec2[4, 1])
    ax9.semilogy('time', 'volume_aorta', data=data_structure, label='Aorta')
    ax9.semilogy('time', 'volume_arteries', data=data_structure, label='Arteries')
    ax9.semilogy('time', 'volume_arterioles', data=data_structure, label='Arterioles')
    ax9.semilogy('time', 'volume_capillaries', data=data_structure, label='Capillaries')
    ax9.semilogy('time', 'volume_veins',  data=data_structure, label='Veins')
    #ax9.semilogy('time', 'volume_ventricle', data=data_structure, label='Ventricle')
    ax9.set_ylabel('log_{10} Volume', fontsize = 10)
    ax9.tick_params(labelsize = 10)
    if t_limits:
        ax9.set_xlim(t_limits)
    ax9.set_ylim([1e-3, 10])
    ax9.set_yticks(np.array([1e-3, 1e-2, 1e-1, 1, 10]))
    ax9.legend(bbox_to_anchor=(1.05, 1),fontsize = 7, ncol=2)
    ax9.set_xlabel('time (s)',fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_active_force(data_structure, output_file_string="", t_limits=[],
                       dpi=None):

    no_of_rows = 4
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    if t_limits:
        time_span = t_limits[1]-t_limits[0]
        plot_width = 46
    else:
        plot_width=46
    f.set_size_inches([10, 15])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    """ax2 = f.add_subplot(spec2[0, 0])
    ax2.plot('time', 'hs_length', data=data_structure, label='hs_length')

    if t_limits:
        ax2.set_xlim(t_limits)
    ax2.set_ylabel('Length', fontsize = 20)
    ax2.tick_params(labelsize = 20)
    ax2.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)"""

    ax1 = f.add_subplot(spec2[0, 0])
    ax1.plot('time', 'Ca_conc', data=data_structure, label='Ca concentration')
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('Ca Concentration\n[M]', fontsize = 20)
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax1.tick_params(labelsize = 10)

    """ax3 = f.add_subplot(spec2[1, 0])
    ax3.plot('time', 'N_overlap', data=data_structure, label='N_overlap')

    if t_limits:
        ax3.set_xlim(t_limits)
    ax3.set_ylabel('Half sarcomere', fontsize = 10)
    ax3.tick_params(labelsize = 10)
    ax3.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)"""

    ax4 = f.add_subplot(spec2[1, 0])
    ax4.plot('time', 'n_on', data=data_structure, label='N_on')
    ax4.plot('time', 'n_off', data=data_structure, label='N_off')
    ax4.plot('time', 'n_bound', data=data_structure, label='N_bound')
    if t_limits:
        ax4.set_xlim(t_limits)
    ax4.set_ylim([0, 1.0])
    ax4.set_ylabel('Thin filament', fontsize = 20)
    ax4.tick_params(labelsize = 20)
    ax4.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax5 = f.add_subplot(spec2[2, 0])
    ax5.plot('time', 'M_OFF', data=data_structure, label='M_OFF')
    ax5.plot('time', 'M_ON', data=data_structure, label='M_ON')
    ax5.plot('time', 'M_bound', data=data_structure, label='M_bound')
    if t_limits:
        ax5.set_xlim(t_limits)
    ax5.set_ylim([0, 1.0])
    ax5.set_ylabel('Thick filament', fontsize = 20)
    ax5.tick_params(labelsize = 20)
    ax5.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax6 = f.add_subplot(spec2[3, 0])
    ax6.plot('time', 'hs_force', data=data_structure, label='Total force')
    ax6.plot('time', 'cb_force', data=data_structure, label='Crossbridge force')
    ax6.plot('time', 'pas_force', data=data_structure, label='Passive force')
    if t_limits:
        ax6.set_xlim(t_limits)
    ax6.set_ylabel('Force', fontsize = 20)
    ax6.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax6.tick_params(labelsize = 20)
    ax6.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_Ca(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 2
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([10, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time', 'membrane_voltage', data=data_structure, label='Voltage')
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('Membrane\nvoltage\n(V)', fontsize = 10)
    ax0.tick_params(labelsize = 10)
    #ax0.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)

    ax1 = f.add_subplot(spec2[1, 0])
    ax1.plot('time', 'Ca_conc', data=data_structure, label='Ca concentration')
    if t_limits:
        ax1.set_xlim(t_limits)
    ax1.set_ylabel('Ca Concentration\n[M]', fontsize = 10)
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax1.tick_params(labelsize = 10)
    #ax1.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)
    ax1.set_xlabel('time (s)', fontsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_N_overlap(data_structure, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([5, 3])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time', 'n_on', data=data_structure, label='N_on')
    ax0.plot('time', 'n_off', data=data_structure, label='N_off')
    ax0.plot('time', 'N_overlap', data=data_structure, label='N_overlap')
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('Thin filament', fontsize = 10)
    ax0.set_xlabel('time (s)', fontsize = 10)
    ax0.tick_params(labelsize = 10)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

#def display_r4(data_structure, output_file_string="", t_limits=[],
#                       dpi=None):
def display_r4(x,y, output_file_string="", t_limits=[],
                       dpi=None):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([10, 5])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)

    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot(x,y)
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.set_ylabel('detachment rate factor', fontsize = 10)
    ax0.set_xlabel('time (s)', fontsize = 10)
    ax0.tick_params(labelsize = 10)
    ax0.legend(bbox_to_anchor=(1.05, 1),fontsize = 10,ncol=4)

    if (output_file_string):
        save_figure_to_file(f, output_file_string, dpi)

def display_activation_pulse(data_structure, output_file_string="", t_limits=[],
                       dpi=150):
    no_of_rows = 1
    no_of_cols = 1

    f = plt.figure(constrained_layout=True)
    f.set_size_inches([5, 2])
    spec2 = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                              figure=f)
    ax0 = f.add_subplot(spec2[0, 0])
    ax0.plot('time','activation',data=data_structure)
    if t_limits:
        ax0.set_xlim(t_limits)
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)
    ax0.set_ylim([0,1])
    ax0.set_yticks([0,1])
    ax0.set_ylabel('Activation', fontsize = 10,rotation=0)
    ax0.yaxis.set_label_coords(-0.1,0.5)
    ax0.set_xlim([-0.1,5])
    ax0.set_xticks([0,5])
    ax0.set_xlabel('Time (s)')
    ax0.tick_params(labelsize = 10)
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
