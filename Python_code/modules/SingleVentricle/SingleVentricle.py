import numpy as np
import pandas as pd
import cProfile
from openpyxl import Workbook
from lxml import etree
from scipy import signal
from scipy.integrate import solve_ivp
from scipy.constants import mmHg as mmHg_in_pascals

from modules.MyoSim.half_sarcomere import half_sarcomere as hs
from modules.SystemControl import system_control as syscon

class single_circulation():
    """Class for a single ventricle circulation"""

    def __init__(self, single_circulation_simulation, xml_file_string=None):

        from .implement import return_lv_circumference,return_lv_pressure
        # Pull off stuff
#        self.input_xml_file_string = xml_file_string

        self.baroreflex = \
            single_circulation_simulation["baroreflex"]

        self.output_parameters = \
            single_circulation_simulation["output_parameters"]

        self.output_buffer_size = \
            int(self.baroreflex["simulation"]["no_of_time_points"][0])
        self.dt= float(self.baroreflex["simulation"]["time_step"][0])
        self.T=\
            float(self.baroreflex["simulation"]["basal_heart_period"][0])


        self.activation_level=0.0
        #self.output_buffer_size = \
        #    int(single_circulation_simulation.baroreflex.
        #        no_of_time_points.cdata)



        # Initialize circulation object using data from the sim_object
        circ_params = single_circulation_simulation["circulation"]

        self.no_of_compartments = int(circ_params["no_of_compartments"][0])
        self.blood_volume = float(circ_params["blood"]["volume"][0])

        self.aorta_resistance = float(circ_params["aorta"]["resistance"][0])
        self.aorta_compliance = float(circ_params["aorta"]["compliance"][0])

        self.arteries_resistance = float(circ_params["arteries"]["resistance"][0])
        self.arteries_compliance = float(circ_params["arteries"]["compliance"][0])

        self.arterioles_resistance = float(circ_params["arterioles"]["resistance"][0])
        self.arterioles_compliance = float(circ_params["arterioles"]["compliance"][0])

        self.capillaries_resistance = float(circ_params["capillaries"]["resistance"][0])
        self.capillaries_compliance = float(circ_params["capillaries"]["compliance"][0])

        self.veins_resistance = float(circ_params["veins"]["resistance"][0])
        self.veins_compliance = float(circ_params["veins"]["compliance"][0])

        self.ventricle_resistance = \
            float(circ_params["ventricle"]["resistance"][0])
        self.ventricle_wall_volume = \
            float(circ_params["ventricle"]["wall_volume"][0])
        self.ventricle_slack_volume = \
            float(circ_params["ventricle"]["slack_volume"][0])

        # Initialise the resistance and compliance arrays for calcuations
        self.resistance = np.array([self.aorta_resistance,
                                    self.arteries_resistance,
                                    self.arterioles_resistance,
                                    self.capillaries_resistance,
                                    self.veins_resistance,
                                    self.ventricle_resistance])
        self.compliance = np.array([self.aorta_compliance,
                                    self.arteries_compliance,
                                    self.arterioles_compliance,
                                    self.capillaries_compliance,
                                    self.veins_compliance,
                                    0])

        # Look for perturbations
        self.volume_perturbation = np.zeros(self.output_buffer_size+1)
        self.aorta_compliance_perturbation=\
        np.zeros(self.output_buffer_size+1)
        self.capillaries_compliance_perturbation=\
        np.zeros(self.output_buffer_size+1)
        self.venous_compliance_perturbation =\
        np.zeros(self.output_buffer_size+1)
        self.aorta_resistance_perturbation=\
        np.zeros(self.output_buffer_size+1)
        self.capillaries_resistance_perturbation=\
        np.zeros(self.output_buffer_size+1)
        self.venous_resistance_perturbation =\
        np.zeros(self.output_buffer_size+1)
        self.ventricle_resistance_perturbation =\
        np.zeros(self.output_buffer_size+1)
        if 'perturbations' in single_circulation_simulation:
            pert = single_circulation_simulation['perturbations']
            if 'volume' in pert:
                temp_vol=pert["volume"]
                start_index = int(temp_vol["start_index"][0])
                stop_index = int(temp_vol["stop_index"][0])
                increment = float(temp_vol["increment"][0])
                self.volume_perturbation[(start_index+1):(stop_index+1)] =\
                    increment
            if 'compliance' in pert:
                temp_c = pert["compliance"]
                if 'aorta' in temp_c:
                    temp_ac = temp_c['aorta']
                    start_index = int(temp_ac["start_index"][0])
                    stop_index = int(temp_ac["stop_index"][0])
                    increment = float(temp_ac["increment"][0])
                    self.aorta_compliance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment
                if 'capillaries' in temp_c:
                    temp_cc = temp_c['capillaries']
                    start_index = int(temp_cc["start_index"][0])
                    stop_index = int(temp_cc["stop_index"][0])
                    increment = float(temp_cc["increment"][0])
                    self.capillaries_compliance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment
                if 'venous' in temp_c:
                    temp_vc = temp_c['venous']
                    start_index = int(temp_vc["start_index"][0])
                    stop_index = int(temp_vc["stop_index"][0])
                    increment = float(temp_vc["increment"][0])
                    self.venous_compliance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment

            if "resistance" in pert:
                temp_r = pert["resistance"]
                if 'aorta' in temp_r:
                    temp_ar = temp_r['aorta']
                    start_index = int(temp_ar["start_index"][0])
                    stop_index = int(temp_ar["stop_index"][0])
                    increment = float(temp_ar["increment"][0])
                    self.aorta_resistance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment

                if 'capillaries' in temp_r:
                    temp_cr = temp_r['capillaries']
                    start_index = int(temp_cr["start_index"][0])
                    stop_index = int(temp_cr["stop_index"][0])
                    increment = float(temp_cr["increment"][0])
                    self.capillaries_resistance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment
                if 'venous' in temp_r:
                    temp_vr = temp_r['venous']
                    start_index = int(temp_vr["start_index"][0])
                    stop_index = int(temp_vr["stop_index"][0])
                    increment = float(temp_vr["increment"][0])
                    self.venous_resistance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment
                if 'ventricle' in temp_r:
                    temp_vtr = temp_r['ventricle']
                    start_index = int(temp_vtr["start_index"][0])
                    stop_index = int(temp_vtr["stop_index"][0])
                    increment = float(temp_vtr["increment"][0])
                    self.ventricle_resistance_perturbation[(start_index+1):(stop_index+1)]=\
                    increment
        # Pull off the half_sarcomere parameters
        hs_params = single_circulation_simulation["half_sarcomere"]
        self.hs = hs.half_sarcomere(hs_params, self.output_buffer_size)

        # Deduce the hsl where force is zero and set the hsl to that length
        self.slack_hsl = self.hs.myof.return_hs_length_for_force(0.0)
        self.delta_hsl = self.slack_hsl - self.hs.hs_length
        self.hs.update_simulation(0.0,self.delta_hsl, 0.0)

        # Deduce the slack circumference of the ventricle and set that

        self.lv_circumference =\
         return_lv_circumference(self,self.ventricle_slack_volume)
        self.n_hs = 10e9*self.lv_circumference / self.slack_hsl

        internal_r = np.power((3.0 * 0.001 * 1.5*self.ventricle_slack_volume)/
                    (2.0 * np.pi), (1.0 / 3.0))

        internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
        self.wall_thickness = 0.001 * self.ventricle_wall_volume /internal_area


        # Look for growth module
        self.growth_activation_array = np.full(self.output_buffer_size+1,False)
        self.growth_activation = self.growth_activation_array[0]

        if 'growth' in single_circulation_simulation:
            # do this
            from modules.Growth import growth as gr
            self.growth = True
            growth_params = single_circulation_simulation["growth"]

            start_time_second = int(growth_params["start_time_seconds"][0])
            start_index=\
            int(start_time_second/self.dt)

            self.driven_signal = growth_params["driven_signal"][0]

            if self.driven_signal != "stress" and "strain":
                print('Growth driven signal is not defined correctly!')

            if self.driven_signal == "strain":
                self.strain = self.delta_hsl/self.slack_hsl

#            internal_r = np.power((3.0 * 0.001 * 1.5*self.ventricle_slack_volume)/
#                        (2.0 * np.pi), (1.0 / 3.0))

#            internal_area = 2.0 * np.pi * np.power(internal_r, 2.0)
#            self.wall_thickness = 0.001 * self.ventricle_wall_volume /internal_area

            initial_numbers_of_hs = self.n_hs#10e9*self.lv_circumference / self.slack_hsl
            self.gr = \
            gr.growth(growth_params,initial_numbers_of_hs,self.output_buffer_size,start_index)

            self.growth_activation_array[start_index:] = True
            self.growth_activation = self.growth_activation_array[0]
            #self.growth_switch = True

        # Baro
        self.baro_params = single_circulation_simulation["baroreflex"]
        self.baro_scheme = self.baro_params["baro_scheme"][0]
        self.syscon=syscon.system_control(self.baro_params, self.output_buffer_size)



        print("hsl: %f" % self.hs.hs_length)
        print("slack hsl: %f" % self.slack_hsl)
        print("slack_lv_circumference %f" % self.lv_circumference)


        # Set the initial volumes with most of the blood in the veins
        initial_ventricular_volume = 1.5 * self.ventricle_slack_volume
        self.v = np.zeros(self.no_of_compartments)
        self.v[-2] = self.blood_volume - initial_ventricular_volume
        self.v[-1] = initial_ventricular_volume

        # Deduce the pressures
        self.p = np.zeros(self.no_of_compartments)
        for i in np.arange(0, self.no_of_compartments-1):
            self.p[i] = self.v[i] / self.compliance[i]
        self.p[-1] = return_lv_pressure(self,self.v[-1])

        # Create a pandas data structure to store data
        self.sim_time = 0.0
        self.data_buffer_index = 0
        self.data = pd.DataFrame({'time': np.zeros(self.output_buffer_size),
                                  'pressure_aorta':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_arteries':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_arterioles':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_capillaries':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_veins':
                                      np.zeros(self.output_buffer_size),
                                  'pressure_ventricle':
                                      np.zeros(self.output_buffer_size),
                                  'volume_aorta':
                                      np.zeros(self.output_buffer_size),
                                  'volume_arteries':
                                      np.zeros(self.output_buffer_size),
                                  'volume_arterioles':
                                      np.zeros(self.output_buffer_size),
                                  'volume_capillaries':
                                      np.zeros(self.output_buffer_size),
                                  'volume_veins':
                                      np.zeros(self.output_buffer_size),
                                  'volume_ventricle':
                                      np.zeros(self.output_buffer_size),
                                  'flow_ventricle_to_aorta':
                                      np.zeros(self.output_buffer_size),
                                  'flow_aorta_to_arteries':
                                      np.zeros(self.output_buffer_size),
                                  'flow_arteries_to_arterioles':
                                      np.zeros(self.output_buffer_size),
                                  'flow_arterioles_to_capillaries':
                                      np.zeros(self.output_buffer_size),
                                  'flow_capillaries_to_veins':
                                      np.zeros(self.output_buffer_size),
                                  'flow_veins_to_ventricle':
                                      np.zeros(self.output_buffer_size),
                                  'volume_perturbation':
                                      np.zeros(self.output_buffer_size),
                                  'ventricle_wall_thickness':
                                     np.zeros(self.output_buffer_size),
                                  'ventricle_wall_volume':
                                    np.full(self.output_buffer_size,self.ventricle_wall_volume)})
#                                  'ventricle_radius':
#                                     np.zeros(self.output_buffer_size)})
        if self.growth_activation_array[-1] == True and self.driven_signal == "strain":
            self.data['cell_strain'] = pd.Series(np.zeros(self.output_buffer_size))
            self.data.at[0, 'cell_strain'] = self.strain
        # Store the first values
        self.data.at[0, 'pressure_aorta'] = self.p[0]
        self.data.at[0, 'pressure_arteries'] = self.p[1]
        self.data.at[0, 'pressure_arterioles'] = self.p[2]
        self.data.at[0, 'pressure_capillaries'] = self.p[3]
        self.data.at[0, 'pressure_veins'] = self.p[4]
        self.data.at[0, 'pressure_ventricle'] = self.p[5]

        self.data.at[0, 'volume_aorta'] = self.v[0]
        self.data.at[0, 'volume_arteries'] = self.v[1]
        self.data.at[0, 'volume_arterioles'] = self.v[2]
        self.data.at[0, 'volume_capillaries'] = self.v[3]
        self.data.at[0, 'volume_veins'] = self.v[4]
        self.data.at[0, 'volume_ventricle'] = self.v[5]


        self.data.at[0, 'ventricle_wall_thickness'] = self.wall_thickness
#        self.data.at[0, 'ventricle_radius'] = self.internal_r
#        self.data.at[0, 'cell_strain'] = 1
#        self.data.at[0, 'self.slack_hsl'] = self.slack_hsl
#        self.data.at[0, 'lv_circumference'] = self.lv_circumference
#        self.data.at[0, 'slack_lv_circumference'] = self.lv_circumference
#        self.data.at[0, 'ventricle_slack_volume'] = self.ventricle_slack_volume

    def run_simulation(self):
        # Run the simulation
        from .implement import implement_time_step, update_data_holders
        from .display import display_simulation, display_flows, display_pv_loop
        from .display import display_baro_results,display_growth, display_force_length

        #baro_params = single_circulation_simulation.baroreflex
        # Set up some values for the simulation
        no_of_time_points = \
            int(self.baro_params["simulation"]["no_of_time_points"][0])

        dt = self.dt#float(self.baro_params["simulation"]["time_step"][0])

        #activation_frequency = \
        #    float(self.baro_params.activation.activation_frequency.cdata)

        activation_duty_ratio = \
            float(self.baro_params["simulation"]["duty_ratio"][0])

        t = dt*np.arange(1, no_of_time_points+1)
        # Apply profiling befor running the simulation
        pr = cProfile.Profile()
        pr.enable()
        # Run the simulation
        for i in np.arange(np.size(t)):
            # Apply volume perturbation to veins
            self.v[-2] = self.v[-2] + self.volume_perturbation[i]
            # Apply perturbation to compliances
            self.compliance[0]=self.compliance[0]+\
                            self.aorta_compliance_perturbation[i]
            self.compliance[2]=self.compliance[2] +\
                            self.capillaries_compliance_perturbation[i]
            self.compliance[-2]=self.compliance[-2] +\
                            self.venous_compliance_perturbation[i]
            # Apply perturbation to resistances
            self.resistance[0]=self.resistance[0]+\
                            self.aorta_resistance_perturbation[i]
            self.resistance[2]=self.resistance[2] +\
                            self.capillaries_resistance_perturbation[i]
            self.resistance[-2]=self.resistance[-2] +\
                            self.venous_resistance_perturbation[i]
            self.resistance[-1] = self.resistance[-1] +\
                            self.ventricle_resistance_perturbation[i]



            # Apply growth activation
            self.growth_activation = self.growth_activation_array[i]
            # Apply heart rate activation
            activation_level=self.syscon.return_activation()

            # Display
            if ( (i % 200) == 0):
                print("Blood volume: %.3g, %.0f %% complete" %
                      (np.sum(self.v), (100*i/np.size(t))))

            implement_time_step(self, dt, activation_level,i)
            update_data_holders(self, dt, activation_level)

            if (i==50000):
                self.baroreceptor_target_aorta_pressure = 80

            if (i==70000):
                self.baroreceptor_target_aorta_pressure = 120
        pr.disable()
        pr.print_stats()

        # Concatenate data structures
        self.data = pd.concat([self.data, self.hs.hs_data, self.syscon.sys_data],axis=1)
        if self.growth_activation:
            self.data =pd.concat([self.data,self.gr.gr_data],axis=1)

        #self.data = pd.concat([self.data, self.syscon.sys_data], axis)

        # Make plots
        # Circulation
        display_simulation(self.data,
                           self.output_parameters["summary_figure"][0])
        display_flows(self.data,
                      self.output_parameters["flows_figure"][0])
        display_pv_loop(self.data,
                        self.output_parameters["pv_figure"][0])
        display_force_length(self.data,
                        self.output_parameters["force_length"][0])
        if(hasattr(self.data,'heart_period')):
            display_baro_results(self.data,
                            self.output_parameters["baro_figure"][0])

        # Half-sarcomere
        hs.half_sarcomere.display_fluxes(self.data,
                               self.output_parameters["hs_fluxes_figure"][0])
        #Growth
        if self.growth_activation:
            display_growth(self.data,
            self.output_parameters["growth_figure"][0],self.driven_signal)
        if "data_file" in  self.output_parameters.values():
        #if not (self.output_parameters["data_file"]):
            # Write data to disk
            # Read xml input as a string
            wb = Workbook()
            ws_parameters = wb.active
            ws_parameters.title = 'Simulation parameters'

            tree = etree.parse(self.input_xml_file_string)
            root = tree.getroot()

            def build_xml_string(input_object, current_string, indent):

                def indent_string(indent):
                    ind_string = ""
                    for i in np.arange(0,indent):
                        ind_string = ("%s    " % ind_string)
                    return ind_string

                for child in input_object:
                    current_string = ("%s\n%s<%s>" %
                                      (current_string, indent_string(indent), child.tag))
                    if (len(list(child))>0):
                        current_string = build_xml_string(child, current_string, indent+1)
                    else:
                        current_string = ("%s%s%s" %
                                         (current_string, indent_string(0), child.text))
                    if (len(list(child))==0):
                        current_string = ("%s%s</%s>" %
                                          (current_string, indent_string(0), child.tag))
                    else:
                        current_string = ("%s\n%s</%s>" %
                                          (current_string, indent_string(indent), child.tag))
                return current_string

            xml_string = build_xml_string(root,"",0)


            if (self.input_xml_file_string):
                f = open(self.input_xml_file_string, mode='r')
                input_xml = f.read()
                f.close
                ws_parameters['A1'] = input_xml
            wb.save(self.output_parameters.data_file.cdata)

            # Append data as a new sheet
            append_df_to_excel(self.output_parameters.data_file.cdata,self.data,
                               sheet_name='Data')

def append_df_to_excel(filename, df, sheet_name='Sheet1', startrow=None,
                       truncate_sheet=False,
                       **to_excel_kwargs):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn't exist, then this function will create it.

    Parameters:
      filename : File path or existing ExcelWriter
                 (Example: '/path/to/file.xlsx')
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: 'Sheet1')
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...
      truncate_sheet : truncate (remove and recreate) [sheet_name]
                       before writing DataFrame to Excel file
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be dictionary]

    Returns: None
    """
    from openpyxl import load_workbook

    import pandas as pd

    # ignore [engine] parameter if it was passed
    if 'engine' in to_excel_kwargs:
        to_excel_kwargs.pop('engine')

    writer = pd.ExcelWriter(filename, engine='openpyxl')

    # Python 2.x: define [FileNotFoundError] exception if it doesn't exist
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError


    try:
        # try to open an existing workbook
        writer.book = load_workbook(filename)

        # get the last row in the existing Excel sheet
        # if it was not specified explicitly
        if startrow is None and sheet_name in writer.book.sheetnames:
            startrow = writer.book[sheet_name].max_row

        # truncate sheet
        if truncate_sheet and sheet_name in writer.book.sheetnames:
            # index of [sheet_name] sheet
            idx = writer.book.sheetnames.index(sheet_name)
            # remove [sheet_name]
            writer.book.remove(writer.book.worksheets[idx])
            # create an empty sheet [sheet_name] using old index
            writer.book.create_sheet(sheet_name, idx)

        # copy existing sheets
        writer.sheets = {ws.title:ws for ws in writer.book.worksheets}
    except FileNotFoundError:
        # file does not exist yet, we will create it
        pass

    if startrow is None:
        startrow = 0

    # write out the new sheet
    df.to_excel(writer, sheet_name, startrow=startrow, **to_excel_kwargs)

    # save the workbook
    writer.save()
