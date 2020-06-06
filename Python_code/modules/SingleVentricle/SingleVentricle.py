import sys
import os
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
from modules.Perturbation import perturbation as pert
from modules.Growth import growth as gr

class single_circulation():
    """Class for a single ventricle circulation"""
    from .implement import implement_time_step, update_data_holders,analyze_data
    from .display import display_simulation, display_flows, display_pv_loop

    def __init__(self, single_circulation_simulation, xml_file_string=None):

        from .implement import return_lv_circumference,return_lv_pressure, return_ATPase
        # Pull off stuff
#        self.input_xml_file_string = xml_file_string
        self.multithreading_activation = \
            single_circulation_simulation["multi_threads"]["multithreading_activation"][0]

        self.output_parameters = \
            single_circulation_simulation["output_parameters"]

        self.baro_params = single_circulation_simulation["baroreflex"]
        self.baro_scheme = self.baro_params["baro_scheme"][0]

        self.output_buffer_size = \
            int(self.baro_params[self.baro_scheme]["simulation"]["no_of_time_points"][0])
        self.dt= float(self.baro_params[self.baro_scheme]["simulation"]["time_step"][0])
        self.T=\
            float(self.baro_params[self.baro_scheme]["simulation"]["basal_heart_period"][0])

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
        self.ventricle_wall_density = \
            float(circ_params["ventricle"]["wall_density"][0])
        self.ventricle_slack_volume = \
            float(circ_params["ventricle"]["slack_volume"][0])
        self.body_surface_area = \
            float(circ_params["ventricle"]["body_surface_area"][0])

        self.lv_mass = \
                    self.ventricle_wall_volume*self.ventricle_wall_density
        self.lv_mass_indexed = \
                    self.lv_mass/self.body_surface_area

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
        self.pert_activation = \
        single_circulation_simulation["perturbations"]["perturbation_activation"][0]
        if self.pert_activation:

            pert_params = single_circulation_simulation['perturbations']
            self.pert = pert.perturbation(pert_params,self.output_buffer_size)
            self.volume_perturbation = self.pert.volume_perturbation

            self.aortic_valve_perturbation =\
            self.pert.aortic_valve_perturbation

            self.mitral_valve_perturbation =\
            self.pert.mitral_valve_perturbation

            self.aorta_compliance_perturbation = \
            self.pert.aorta_compliance_perturbation

            self.capillaries_compliance_perturbation=\
            self.pert.capillaries_compliance_perturbation

            self.venous_compliance_perturbation =\
            self.pert.venous_compliance_perturbation

            self.aorta_resistance_perturbation=\
            self.pert.aorta_resistance_perturbation

            self.capillaries_resistance_perturbation=\
            self.pert.capillaries_resistance_perturbation

            self.venous_resistance_perturbation =\
            self.pert.venous_resistance_perturbation

            self.ventricle_resistance_perturbation =\
            self.pert.ventricle_resistance_perturbation

            self.k_1_perturbation = self.pert.k_1_perturbation

            self.k_2_perturbation = self.pert.k_2_perturbation

            self.k_4_0_perturbation = self.pert.k_4_0_perturbation

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
        growth_params = single_circulation_simulation["growth"]

        if growth_params["growth_activation"][0]:

            from modules.Growth import growth as gr

            start_index = int(growth_params["start_index"][0])

            self.driven_signal = growth_params["driven_signal"][0]

            if self.driven_signal != "stress" and self.driven_signal!="ATPase":
                print('Growth driven signal is not defined correctly!')

            initial_numbers_of_hs = self.n_hs
            self.gr = \
            gr.growth(growth_params,initial_numbers_of_hs,self.hs,circ_params,
                            self.output_buffer_size)

            self.growth_activation_array[start_index:] = True
            self.growth_activation = self.growth_activation_array[0]
            #self.growth_switch = True

        # Baro
        self.syscon=syscon.system_control(self.baro_params,hs_params,circ_params,
                                    self.output_buffer_size)

        print("hsl: %f" % self.hs.hs_length)
        print("slack hsl: %f" % self.slack_hsl)
        print("slack_lv_circumference %f" % self.lv_circumference)

        # Set the initial volumes with most of the blood in the veins
        initial_ventricular_volume = 1.5 * self.ventricle_slack_volume
        self.v = np.zeros(self.no_of_compartments)
        self.v[4] = self.blood_volume - initial_ventricular_volume
        self.v[-1] = initial_ventricular_volume

        # Deduce the pressures
        self.p = np.zeros(self.no_of_compartments)
        for i in np.arange(0, self.no_of_compartments-1):
            self.p[i] = self.v[i] / self.compliance[i]
        self.p[-1] = return_lv_pressure(self,self.v[-1])

        #Valve leakages
        self.vl = np.zeros(2)

        # ATPase
#        self.ATPase_activation = \
#            single_circulation_simulation["ATPase"][0]

        # saving data
#        self.saving_data_activation = False
        self.saving_data_activation =  \
            single_circulation_simulation["saving_to_spreadsheet"]["saving_data_activation"][0]
        if self.saving_data_activation:
            self.save_data_start_index = \
                single_circulation_simulation["saving_to_spreadsheet"]["start_index"][0]
            self.save_data_stop_index= \
                single_circulation_simulation["saving_to_spreadsheet"]["stop_index"][0]
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
                                  'volume_aortic_regurgitation':
                                      np.zeros(self.output_buffer_size),
                                  'volume_mitral_regurgitation':
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
#                                  'ATPase':
#                                     np.zeros(self.output_buffer_size),
                                  'ventricle_wall_volume':
                                    np.full(self.output_buffer_size,1000*self.ventricle_wall_volume),
                                    'ventricle_wall_mass':
                                    np.full(self.output_buffer_size,self.lv_mass),
                                    'ventricle_wall_mass_i':
                                    np.full(self.output_buffer_size,self.lv_mass_indexed)})

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
        self.data.at[0, 'volume_ventricle'] = self.v[-1]

        self.data.at[0, 'volume_aortic_regurgitation'] = self.vl[0]
        self.data.at[0, 'volume_mitral_regurgitation'] = self.vl[1]

        """if self.hs.ATPase_activation:
            self.ATPase = return_ATPase(self)
            self.data.at[0, 'ATPase'] = self.ATPase"""

        self.prof_activation = \
            single_circulation_simulation["profiling"]["profiling_activation"][0]

    def run_simulation(self):
        # Run the simulation
        from .implement import implement_time_step, update_data_holders,analyze_data
        from .display import display_simulation, display_flows, display_pv_loop
        from .display import display_Ca,display_pres,display_simulation_publish

        # Set up some values for the simulation
        no_of_time_points = \
            int(self.baro_params[self.baro_scheme]["simulation"]["no_of_time_points"][0])

        activation_duty_ratio = \
            float(self.baro_params[self.baro_scheme]["simulation"]["duty_ratio"][0])

        t = self.dt*np.arange(1, no_of_time_points+1)

        # Apply profiling befor running the simulation
        if self.prof_activation:
            pr = cProfile.Profile()
            pr.enable()

        # Run the simulation
        for i in np.arange(np.size(t)):

            if self.pert_activation:
                # Apply volume perturbation to veins
                self.v[-2] = self.v[-2] + self.volume_perturbation[i]
                # Apply valve perturbation
                    #aortic
                self.aortic_valve_perturbation_factor = \
                self.aortic_valve_perturbation[i]
                    #mitral
                self.mitral_valve_perturbation_factor = \
                self.mitral_valve_perturbation[i]
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
                # Apply perturbation to myosim
                self.hs.myof.k_1 = self.hs.myof.k_1 + self.k_1_perturbation[i]
                self.hs.myof.k_2 = self.hs.myof.k_2 + self.k_2_perturbation[i]
                self.hs.myof.k_4_0 = self.hs.myof.k_4_0 +self.k_4_0_perturbation[i]

            # Apply growth activation
            self.growth_activation = self.growth_activation_array[i]
            # Apply heart rate activation
            activation_level=self.syscon.return_activation()

            # Display
            if ( (i % 200) == 0):
                print("Blood volume: %.3g, %.0f %% complete" %
                      (np.sum(self.v), (100*i/np.size(t))))

            implement_time_step(self, self.dt, activation_level,i)
            update_data_holders(self, self.dt, activation_level)

        # Concatenate data structures
        self.data = pd.concat([self.data, self.hs.hs_data, self.syscon.sys_data],axis=1)

        if self.growth_activation:
            self.data =pd.concat([self.data,self.gr.gr_data],axis=1)

        # Get output for multithreading
        if self.multithreading_activation:
            return self.data




        if self.prof_activation:
            pr.disable()
            pr.print_stats()
        # Make plots
        # Circulation
        display_simulation(self.data,
                           self.output_parameters["summary_figure"][0],[41.4,43.4])#,[81.6,82.6])
        #display_simulation_publish(self.data,
        #                   self.output_parameters["summary_figure"][0],[8.4,9.4])
        display_flows(self.data,
                      self.output_parameters["flows_figure"][0])
        display_pv_loop(self.data,
                        self.output_parameters["pv_figure"][0],[41.4,42.4])
        display_pres(self.data,
                    self.output_parameters["pres"][0],[41.4,43.4])
        syscon.system_control.display_arterial_pressure(self.data,
                        self.output_parameters["arterial"][0])

        if self.baro_scheme !="fixed_heart_rate":
            syscon.system_control.display_baro_results(self.data,
                            self.output_parameters["baro_figure"][0])

        # Half-sarcomere
        hs.half_sarcomere.display_fluxes(self.data,
                               self.output_parameters["hs_fluxes_figure"][0])
    #    display_Ca(self.data,self.output_parameters["Ca"][0])

        #Growth
        if self.growth_activation:

            self.data = analyze_data(self,self.data)

            gr.growth.display_growth(self.data,
            self.output_parameters["growth_figure"][0],self.driven_signal)

            gr.growth.display_growth_summary(self.data,
            self.output_parameters["growth_summary"][0],self.driven_signal)



            gr.growth.display_ventricular_dimensions(self.data,
            self.output_parameters["ventricular"][0])

            gr.growth.display_systolic_function(self.data,
                    self.output_parameters["sys_fig"][0])

        if self.hs.ATPase_activation:
            gr.growth.display_ATPase(self.data,self.output_parameters["ATPase"][0])
#        display_regurgitation(self.data,
#                self.output_parameters["regurg_fig"][0])
        if self.saving_data_activation:
            print("Data is saving to an excel spread sheet!")

            data_to_be_saved = \
                self.data.loc[self.save_data_start_index:self.save_data_stop_index,:]

            append_df_to_excel(self.output_parameters['excel_file'][0],data_to_be_saved,
                           sheet_name='Data',startrow=0)

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
