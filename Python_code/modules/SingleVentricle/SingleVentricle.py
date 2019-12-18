import numpy as np
import pandas as pd
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
        self.input_xml_file_string = xml_file_string

        self.baroreflex = \
            single_circulation_simulation.baroreflex

        self.output_parameters = \
            single_circulation_simulation.output_parameters

        self.output_buffer_size = \
            int(self.baroreflex.simulation.no_of_time_points.cdata)
        self.T=\
            float(self.baroreflex.simulation.basal_heart_period.cdata)

        self.activation_level=0.0
        #self.output_buffer_size = \
        #    int(single_circulation_simulation.baroreflex.
        #        no_of_time_points.cdata)

        # Look for perturbations
        self.volume_perturbation = np.zeros(self.output_buffer_size+1)
        if (hasattr(single_circulation_simulation, 'perturbations')):
            if hasattr(single_circulation_simulation.perturbations, 'volume'):
                temp = single_circulation_simulation.perturbations.volume
                start_index = int(temp.start_index.cdata)
                stop_index = int(temp.stop_index.cdata)
                increment = float(temp.increment.cdata)
                self.volume_perturbation[(start_index+1):(stop_index+1)] =\
                    increment

        # Look for baroreceptor module
        """if (hasattr(single_circulation_simulation, 'baroreceptor')):
            self.baroreceptor_active = 1
            baroreceptor_max_memory = \
                int(single_circulation_simulation.baroreceptor.
                    max_memory.cdata)
            self.baroreceptor_pressure_array = \
                np.zeros(baroreceptor_max_memory)
            self.baroreceptor_target_aorta_pressure = \
                float(single_circulation_simulation.baroreceptor.
                      target_aorta_pressure.cdata)
            self.baroreceptor_hr_gain = \
                float(single_circulation_simulation.baroreceptor.
                      hr_gain.cdata)
        else:
             self.baroreceptor_active= 0"""

        # Look for growth module
        if (hasattr(single_circulation_simulation, 'growth_module')):
            # do this
            temp = 1

        # Initialize circulation object using data from the sim_object
        circ_params = single_circulation_simulation.circulation

        self.no_of_compartments = int(circ_params.no_of_compartments.cdata)
        self.blood_volume = float(circ_params.blood.volume.cdata)

        self.aorta_resistance = float(circ_params.aorta.resistance.cdata)
        self.aorta_compliance = float(circ_params.aorta.compliance.cdata)

        self.arteries_resistance = float(circ_params.arteries.resistance.cdata)
        self.arteries_compliance = float(circ_params.arteries.compliance.cdata)

        self.arterioles_resistance = float(circ_params.arterioles.resistance.cdata)
        self.arterioles_compliance = float(circ_params.arterioles.compliance.cdata)

        self.capillaries_resistance = float(circ_params.capillaries.resistance.cdata)
        self.capillaries_compliance = float(circ_params.capillaries.compliance.cdata)

        self.veins_resistance = float(circ_params.veins.resistance.cdata)
        self.veins_compliance = float(circ_params.veins.compliance.cdata)

        self.ventricle_resistance = \
            float(circ_params.ventricle.resistance.cdata)
        self.ventricle_wall_volume = \
            float(circ_params.ventricle.wall_volume.cdata)
        self.ventricle_slack_volume = \
            float(circ_params.ventricle.slack_volume.cdata)

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
        # Baro
        self.baro_params = single_circulation_simulation.baroreflex
        self.baro_scheme = self.baro_params.baro_scheme.cdata
        self.syscon=syscon.system_control(self.baro_params, self.output_buffer_size)
        #self.P_tilda=[100.0]
        #self.delta_Ts=1.0
        #self.delta_Tv=1.0
        # Pull off the half_sarcomere parameters
        hs_params = single_circulation_simulation.half_sarcomere
        self.hs = hs.half_sarcomere(hs_params, self.output_buffer_size)

        # Deduce the hsl where force is zero and set the hsl to that length
        slack_hsl = self.hs.myof.return_hs_length_for_force(0.0)
        self.hs.update_simulation(0.0,(slack_hsl - self.hs.hs_length), 0.0)

        # Deduce the slack circumference of the ventricle and set that

        self.lv_circumference =\
         return_lv_circumference(self,self.ventricle_slack_volume)

        print("hsl: %f" % self.hs.hs_length)
        print("slack hsl: %f" % slack_hsl)
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
                                  'ventricle_wall_volume':
                                      np.zeros(self.output_buffer_size)})

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

        self.data.at[0, 'ventricle_wall_volume'] = self.ventricle_wall_volume


    def run_simulation(self):
        # Run the simulation
        from .implement import implement_time_step, update_data_holders
        from .display import display_simulation, display_flows, display_pv_loop,display_baro_results
        #baro_params = single_circulation_simulation.baroreflex
        # Set up some values for the simulation
        no_of_time_points = \
            int(self.baro_params.simulation.no_of_time_points.cdata)

        dt = float(self.baro_params.simulation.time_step.cdata)

        #activation_frequency = \
        #    float(self.baro_params.activation.activation_frequency.cdata)

        activation_duty_ratio = \
            float(self.baro_params.simulation.duty_ratio.cdata)

        t = dt*np.arange(1, no_of_time_points+1)

        # Run the simulation
        for i in np.arange(np.size(t)):
            # Apply volume perturbation to veins
            self.v[-2] = self.v[-2] + self.volume_perturbation[i]
            #if 50<=(100*i/np.size(t))and (100*i/np.size(t))<=60:
                #self.v[-2] = 1.01*self.v[-2]
            #    self.v[-2] = 0.9998*self.v[-2]

                #self.compliance[1]=0.5*self.compliance[1]
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

        # Concatenate data structures
        self.data = pd.concat([self.data, self.hs.hs_data, self.syscon.sys_data], axis=1)
        #self.data = pd.concat([self.data, self.syscon.sys_data], axis)

        # Make plots
        # Circulation
        display_simulation(self.data,
                           self.output_parameters.summary_figure.cdata)
        display_flows(self.data,
                      self.output_parameters.flows_figure.cdata)
        display_pv_loop(self.data,
                        self.output_parameters.pv_figure.cdata)
        if(hasattr(self.data,'heart_period')):
            display_baro_results(self.data,
                            self.output_parameters.heart_period.cdata)

        # Half-sarcomere
        hs.half_sarcomere.display_fluxes(self.data,
                               self.output_parameters.hs_fluxes_figure.cdata)

        if (self.output_parameters.data_file.cdata):
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
