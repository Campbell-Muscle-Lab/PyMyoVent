# Analyse segment
import os, glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy import stats
import xlrd
import re

def sensitivity_analysis(analysis_data, parameter_strings):
    # Create a pandas structure to hold analysis results
    sensitivity_results = pd.DataFrame()
    results_index = 0

    # Get the working directory
    working_directory = analysis_data['root_folder']
    print(working_directory)

    for par_string in parameter_strings:

        # Switch to the folder containing the data for the chosen parameter
        test_folder = \
            analysis_data['root_folder'] + '/' + \
            analysis_data['base_sim_data_folder'] + '/' + \
            par_string.replace('/', '_') + '/' + \
            analysis_data['data_folder']
        os.chdir(test_folder)

        # Find the filenames for the simulation data files
        data_file_names = \
            glob.glob("*.%s" % analysis_data['data_file_extension'])

        # Switch back to the working directory
        os.chdir(working_directory)

        # Pull out the tag we are looking for
        tag_string = par_string.rsplit('/', 1)[-1]

        print("par_string: %s" % par_string)

        for i in range(0, len(data_file_names)):
            full_data_file_name = test_folder + '/' + data_file_names[i]

            # Read in xml from the simulation data file
            excel_file = xlrd.open_workbook(full_data_file_name)
            sheet = excel_file.sheet_by_name('Simulation parameters')
            sim_xml = sheet.cell(0, 0)
            sim_xml = ("%s" % sim_xml)

            # Deduce the parameter value
            search_query = ("<%s>(.*?)</%s>" % (tag_string, tag_string))
            search_result = re.search(search_query, sim_xml).group(1)
            par_value = float(search_result)

            # Read in the simulation data
            d = pd.read_excel(full_data_file_name, 'Data')

            # Steady-state beat analysis
            # Generate file name
            fig_name = ("steady_state_beat_%f" % par_value)
            fig_name = build_figure_filename(
                    analysis_data, par_string,
                    fig_name.replace('.', '_'))
            
            steady_state_results = analyze_single_beat(
                    d,
                    t_limits=analysis_data['steady_state_beat_t_span'],
                    output_file_string = fig_name)

            # ESPVR analysis
            # Generate a filename
            fig_name = ("espvr_analysis_%f" % par_value)
            fig_name = build_figure_filename(
                    analysis_data, par_string,
                    fig_name.replace('.', '_'))

            espvr_results = analyze_espvr(
                    d,
                    t_limits=analysis_data['espvr_t_span'],
                    output_file_string=fig_name)

            # Store data
            sensitivity_results.at[results_index, 'test_parameter'] = \
                par_string
            sensitivity_results.at[results_index, 'parameter_value'] = \
                par_value
            sensitivity_results.at[results_index, 'pressure_ventricle_max'] = \
                steady_state_results['pressure_ventricle_max']
            sensitivity_results.at[results_index, 'pressure_ventricle_min'] = \
                steady_state_results['pressure_ventricle_min']
            sensitivity_results.at[results_index, 'volume_ventricle_max'] = \
                steady_state_results['volume_ventricle_max']
            sensitivity_results.at[results_index, 'volume_ventricle_min'] = \
                steady_state_results['volume_ventricle_min']
            sensitivity_results.at[results_index, 'stroke_volume'] = \
                steady_state_results['stroke_volume']
            sensitivity_results.at[results_index, 'espvr'] = \
                espvr_results['espvr_slope']
            results_index = results_index+1
            break
        break

    # Build the output file
    sensitivity_results_filename = analysis_data['root_folder'] + '/' + \
            analysis_data['base_sim_data_folder'] + '/' + \
            analysis_data['sensitivity_results_file']
    sensitivity_results.to_excel(sensitivity_results_filename)


def build_figure_filename(analysis_data, parameter_string, fig_name):
    # Returns a custom-built file string for an image
    return analysis_data['root_folder'] + '/' + \
           analysis_data['base_sim_data_folder'] + '/' + \
           parameter_string.replace('/', '_') + '/' + \
           analysis_data['fig_folder'] + '/' + \
           fig_name + '.' + \
           analysis_data['fig_extension']


def analyze_single_beat(data_structure, t_limits=None, display_figure=True,
                        output_file_string=""):

    if t_limits:
        t = data_structure['time']
        vi = np.nonzero((t >= t_limits[0]) & (t <= t_limits[1]))
        data_structure = data_structure.iloc[vi]

    t = data_structure['time'].values
    pressure_ventricle = data_structure['pressure_ventricle'].values
    volume_ventricle = data_structure['volume_ventricle'].values
    no_of_time_points = len(t)

    out = dict()

    vi, peak_data = find_peaks(pressure_ventricle)
    out['t_pressure_max'] = t[vi[0]]
    out['pressure_ventricle_max'] = pressure_ventricle[vi[0]]

    vi, peak_data = find_peaks(-pressure_ventricle)
    out['t_pressure_min'] = t[vi[0]]
    out['pressure_ventricle_min'] = pressure_ventricle[vi[0]]

    vi, peak_data = find_peaks(volume_ventricle)
    out['t_volume_max'] = t[vi[0]]
    out['volume_ventricle_max'] = volume_ventricle[vi[0]]

    vi, peak_data = find_peaks(-volume_ventricle)
    out['t_volume_min'] = t[vi[0]]
    out['volume_ventricle_min'] = volume_ventricle[vi[0]]

    out['stroke_volume'] = out['volume_ventricle_max'] - \
                           out['volume_ventricle_min']

    end_phase_data = return_end_phase_data(data_structure, t_limits)

    out['end_systolic_volume_ventricle'] = \
        end_phase_data['end_systolic_volume_ventricle']
    out['end_systolic_pressure_ventricle'] = \
        end_phase_data['end_systolic_pressure_ventricle']
    out['end_diastolic_volume_ventricle'] = \
        end_phase_data['end_diastolic_volume_ventricle']
    out['end_diastolic_pressure_ventricle'] = \
        end_phase_data['end_diastolic_pressure_ventricle']

    # Get dP/dt values
    if (end_phase_data['end_systolic_index'] >
            end_phase_data['end_diastolic_index']):
        systolic_indices = list(range(end_phase_data['end_diastolic_index'],
                                      end_phase_data['end_systolic_index']))
        diastolic_indices = list(range(0,
                                end_phase_data['end_diastolic_index'])) + \
                            list(range(end_phase_data['end_systolic_index'],
                                no_of_time_points))
    else:
        systolic_indices = list(range(end_phase_data['end_systolic_index'],
                                      end_phase_data['end_diastolic_index']))
        diastolic_indices = list(range(end_phase_data['end_diastolic_index'],
                                       no_of_time_points)) + \
                            list(range(0,
                                end_phase_phase_data['end_systolic_index']))
    pressure_systolic_phase = pressure_ventricle[systolic_indices]
    dpdt = np.diff(pressure_systolic_phase, n=1)
    dpdt = np.pad(dpdt, (0, 1), 'constant', constant_values=(0, 0))
    out['dpdt_max_ventricle'] = np.amax(dpdt)
    out['dpdt_max_ventricle_index'] = int(np.argmax(dpdt) + systolic_indices[0])


    if ((display_figure) or (output_file_string)):
        no_of_rows = 3
        no_of_cols = 1

        f = plt.figure(constrained_layout=True)
        f.set_size_inches([4, 8])
        spec = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                                 figure=f)

        ax1 = f.add_subplot(spec[0, 0])
        ax1.plot(t[systolic_indices],
                 pressure_ventricle[systolic_indices], 'r-')
        ax1.plot(t[diastolic_indices],
                 pressure_ventricle[diastolic_indices], 'b-')
        ax1.set_ylabel('Ventricular pressure')
        ax1.plot(out['t_pressure_max'], out['pressure_ventricle_max'], 'ro')
        ax1.plot(out['t_pressure_min'], out['pressure_ventricle_min'], 'ms')
        ax1.plot(t[out['dpdt_max_ventricle_index']],
                 pressure_ventricle[out['dpdt_max_ventricle_index']], 'c^')

        ax2 = f.add_subplot(spec[1, 0])
        ax2.plot(t, volume_ventricle)
        ax2.set_ylabel('Ventricular volume')
        ax2.plot(out['t_volume_max'], out['volume_ventricle_max'], 'yo')
        ax2.plot(out['t_volume_min'], out['volume_ventricle_min'], 'ks')

        ax3 = f.add_subplot(spec[2, 0])
        ax3.plot(volume_ventricle, pressure_ventricle)
        ax3.plot(out['end_systolic_volume_ventricle'],
                 out['end_systolic_pressure_ventricle'], 'go')
        ax3.plot(out['end_diastolic_volume_ventricle'],
                 out['end_diastolic_pressure_ventricle'], 'cs')
        ax3.set_ylabel('Ventricular volume')
        ax3.set_ylabel('Ventricular pressure')

        if (output_file_string):
            print(output_file_string)
            f.savefig(output_file_string)
            plt.close()

    return out


def return_end_phase_data(data_structure, t_limits=None):

    if t_limits:
        t = data_structure['time']
        vi = np.nonzero((t >= t_limits[0]) & (t <= t_limits[1]))
        data_structure = data_structure.iloc[vi]

    t = data_structure['time'].values
    pressure_ventricle = data_structure['pressure_ventricle'].values
    volume_ventricle = data_structure['volume_ventricle'].values

    p_norm = pressure_ventricle - np.min(pressure_ventricle)
    p_norm = p_norm / np.max(p_norm)

    v_norm = volume_ventricle - np.min(volume_ventricle)
    v_norm = v_norm / np.max(v_norm)

    mean_p = np.mean(p_norm)
    mean_v = np.mean(v_norm)

    # Find End Systole
    r = np.hypot((v_norm - mean_v), (p_norm - mean_p))
    r[np.nonzero(p_norm < mean_p)] = 0
    r[np.nonzero(v_norm > mean_v)] = 0
    vi, peak_data = find_peaks(r, prominence=0.5*np.max(r))
    if (len(vi) == 0):
        # special case where we didn't find a peak
        vi = np.zeros(1)
        vi[0] = np.argmax(r)

    out = dict()
    out['end_systolic_index'] = vi[0]
    out['end_systolic_time'] = t[int(vi[0])]
    out['end_systolic_volume_ventricle'] = volume_ventricle[int(vi[0])]
    out['end_systolic_pressure_ventricle'] = pressure_ventricle[int(vi[0])]

    # Find Diastolic
    r2 = np.hypot((v_norm - mean_v), (p_norm - mean_p))
    r2[np.nonzero(p_norm > mean_p)] = 0
    r2[np.nonzero(v_norm < mean_v)] = 0
    vi, peak_data = find_peaks(r2, prominence=0.5*np.max(r2))
    if (len(vi) == 0):
        # special case where we didn't find a peak
        vi = np.zeros(1)
        vi[0] = np.argmax(r2)

    out['end_diastolic_index'] = vi[0]
    out['end_diastolic_time'] = t[int(vi[0])]
    out['end_diastolic_volume_ventricle'] = volume_ventricle[int(vi[0])]
    out['end_diastolic_pressure_ventricle'] = pressure_ventricle[int(vi[0])]

#    f = plt.figure()
#    plt.plot(volume_ventricle,pressure_ventricle)
#    plt.plot(out['end_diastolic_volume_ventricle'],out['end_diastolic_pressure_ventricle'],'gs')
#    plt.plot(out['end_systolic_volume_ventricle'],out['end_systolic_pressure_ventricle'],'gs')

    return out


def isolate_beats(data_structure, t_limits=None, display_figure=False):
    # Returns number of beats and start and stop times for each beat

    # Prune data
    if t_limits:
        t = data_structure['time']
        vi = np.nonzero((t >= t_limits[0]) & (t <= t_limits[1]))
        data_structure = data_structure.iloc[vi]

    t = data_structure['time'].values
    act = data_structure['activation'].values
    diff_act = np.diff(act, n=1)
    diff_act = np.pad(diff_act, (0, 1), 'constant', constant_values=(0, 0))
    vi, peak_data = find_peaks(diff_act)

    out = dict()

    if (len(vi) <= 2):
        out['no_of_beats'] = 1
        out['start_index'] = 0
        out['start_time'] = t[0]
        out['stop_index'] = len(t)
        out['stop_time'] = t[-1]
    else:
        out['no_of_beats'] = (len(vi)-1)
        # Allocate space
        out['start_index'] = np.zeros(out['no_of_beats'])
        out['start_time'] = np.zeros(out['no_of_beats'])
        out['stop_index'] = np.zeros(out['no_of_beats'])
        out['stop_time'] = np.zeros(out['no_of_beats'])
        for i in np.arange(0, out['no_of_beats']):
            out['start_index'][i] = int(vi[i])
            out['start_time'][i] = t[vi[i]]
            out['stop_index'][i] = int(vi[i+1]-1)
            out['stop_time'][i] = t[int(out['stop_index'][i])]

    if (display_figure):
        no_of_rows = 2
        no_of_cols = 1

        f = plt.figure(constrained_layout=True)
        f.set_size_inches([4, 4])
        spec = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                                 figure=f)

        ax1 = f.add_subplot(spec[0, 0])
        ax1.plot(t, act)

        ax1 = f.add_subplot(spec[1, 0])
        ax1.plot(t, diff_act)
        ax1.plot(out['start_time'],
                 diff_act[out['start_index'].astype(int)], 'go')
        ax1.plot(out['stop_time'],
                 diff_act[out['stop_index'].astype(int)], 'rs')

    return out


def analyze_espvr(data_structure, t_limits=None, display_figure=True,
                  output_file_string=""):

    # Prune data
    if t_limits:
        t = data_structure['time']
        vi = np.nonzero((t >= t_limits[0]) & (t <= t_limits[1]))
        data_structure = data_structure.iloc[vi]

    # Find beats
    beat_data = isolate_beats(data_structure)

    # Cycle through each beat
    out = dict()
    out['no_of_beats'] = beat_data['no_of_beats']
    out['end_systolic_pressure_ventricle'] = np.zeros(out['no_of_beats'])
    out['end_systolic_volume_ventricle'] = np.zeros(out['no_of_beats'])
    out['end_diastolic_pressure_ventricle'] = np.zeros(out['no_of_beats'])
    out['end_diastolic_volume_ventricle'] = np.zeros(out['no_of_beats'])

    for i in np.arange(0, out['no_of_beats']):
        end_phase_data = return_end_phase_data(data_structure,
                              t_limits=[beat_data['start_time'][i],
                                        beat_data['stop_time'][i]])
        out['end_systolic_pressure_ventricle'][i] = \
            end_phase_data['end_systolic_pressure_ventricle']
        out['end_systolic_volume_ventricle'][i] = \
            end_phase_data['end_systolic_volume_ventricle']
        out['end_diastolic_pressure_ventricle'][i] = \
            end_phase_data['end_diastolic_pressure_ventricle']
        out['end_diastolic_volume_ventricle'][i] = \
            end_phase_data['end_diastolic_volume_ventricle']

    # Fit the straight line
    slope, intercept, r, p, std_err = stats.linregress(
            out['end_systolic_volume_ventricle'],
            out['end_systolic_pressure_ventricle'])
    out['espvr_slope'] = slope
    print("espvr_slope %f" % out['espvr_slope'])
    out['espvr_intercept'] = intercept
    out['espvr_r'] = r
    out['espv_p'] = p
    out['espv_std_err'] = std_err
    out['espvr_fit_x'] = np.linspace(
            np.amin(out['end_systolic_volume_ventricle']),
            np.amax(out['end_systolic_volume_ventricle']))
    out['espvr_fit_y'] = out['espvr_intercept'] + \
                            out['espvr_fit_x'] * out['espvr_slope']

    if ((display_figure) or (output_file_string)):
        no_of_rows = 1
        no_of_cols = 1

        f = plt.figure(constrained_layout=True)
        f.set_size_inches([4, 4])
        spec = gridspec.GridSpec(nrows=no_of_rows, ncols=no_of_cols,
                                 figure=f)

        ax1 = f.add_subplot(spec[0, 0])
        ax1.plot('volume_ventricle', 'pressure_ventricle',
                 data=data_structure)
        ax1.plot(out['end_systolic_volume_ventricle'],
                 out['end_systolic_pressure_ventricle'], 'go')
        ax1.plot(out['espvr_fit_x'], out['espvr_fit_y'], 'r-')
        ax1.set_xlabel('Ventricular_volume')
        ax1.set_ylabel('Ventricular pressure')

        if (output_file_string):
            print(output_file_string)
            f.savefig(output_file_string)
            plt.close()

    return out