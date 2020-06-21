import numpy as np
import pandas as pd
import sys
import os
import json
import nested_lookup as nl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathos.multiprocessing import ProcessingPool as Pool

from modules.SingleVentricle.SingleVentricle import single_circulation as sc
from modules.SingleVentricle.SingleVentricle import append_df_to_excel
from modules.MyoSim.half_sarcomere import half_sarcomere as hs

def run_multi_processing(main_inputs):
    p=Pool()

    def return_objects(inputs):
        obj = [0]*len(inputs)
        print('len obj',len(obj))
        for i in range(len(inputs)):
            obj[i]=sc(inputs[i])
        return obj

    inputs=return_input_data(main_inputs)
    obj = return_objects(inputs)

    #print(obj)
    def start_simulation(objc):
        data=objc.run_simulation()
        return data

    results = p.map(start_simulation,obj)
    p.close()
    p.join()

    #plot multi threading results
    final_output_data = process_data(main_inputs,results)

    # normal post processing of data
    sim=sc(main_inputs)
    final_output_data = sim.analyze_data(final_output_data)
    output_temp = main_inputs["output_parameters"]
    sc.display_simulation(final_output_data,output_temp["summary_figure"][0])
    sc.display_flows(final_output_data,output_temp["flows_figure"][0])
    sc.display_pv_loop(final_output_data,output_temp["pv_figure"][0])

    if(hasattr(final_output_data,'heart_period')):
        sc.display_baro_results(final_output_data,output_temp["baro_figure"][0])

    hs.half_sarcomere.display_fluxes(final_output_data,
                                    output_temp["hs_fluxes_figure"][0])
    if sim.growth_activation:
        sc.display_growth(final_output_data,output_temp["growth_figure"][0],
                        sc.driven_signal)
        sc.display_ventricular_dimensions(final_output_data,output_temp["ventricular"][0])

    sc.display_systolic_function(final_output_data,output_temp["sys_fig"][0])

    #append data to an excel sheet
    append_df_to_excel(output_temp['excel_file'][0],final_output_data,
                       sheet_name='Data',startrow=0)

def process_data(main_inputs,output_data):
    organized_dataframe = pd.DataFrame({})

    params = main_inputs["multi_threads"]["parameters_in"]
    num_of_params = len(params.keys())
    plot_temp = main_inputs["output_parameters"]["multi_threading"][0]
    index_counter = 0

    for i in range(num_of_params):

        affecting_param=list(params.keys())[i]
        multiplier = params[affecting_param]["values"]
        affected_param = params[affecting_param]["param_out"][0]


        for j in range(len(multiplier)):
            multiplier_value = float(multiplier[j])

            if i==0 and int(multiplier_value)==100:
                main_data = output_data[index_counter]

            new_affected_data_name = \
                create_param_data_name(affected_param,multiplier_value)
            new_affected_data_value = \
                extract_data(output_data[index_counter],affected_param)
            print('new_affected_data_name',new_affected_data_name)

            #dumping output data into organized data frame
            organized_dataframe[new_affected_data_name]= new_affected_data_value

            index_counter += 1
    # Concatenate data structures
    organized_dataframe = pd.concat([main_data,organized_dataframe],axis=1)
    display_multithreading(organized_dataframe,plot_temp)

    return organized_dataframe
def return_input_data(main_input):

    temp = \
        main_input["multi_threads"]["output_main_folder"][0]
    params = main_input["multi_threads"]["parameters_in"]
    num_of_params = len(params.keys())
    plot_temp = main_input["output_parameters"]["multi_threading"][0]
    data=pd.DataFrame({})
    inputs=[]
    for i in range(num_of_params):
#                print('n',n)
        affecting_param=list(params.keys())[i]
        multiplier = params[affecting_param]["values"]
        affected_param = params[affecting_param]["param_out"][0]


        #num_of_param_values = len(multiplier)
        section_name = params[affecting_param]['section'][0]

        main_input_data = main_input
        section_dict = main_input_data[section_name]
        param_main_value = nl.nested_lookup(affecting_param,section_dict)[0][0]

        for j in range(len(multiplier)):
        #create different output folder with a different json input file
            multiplier_value = float(multiplier[j])
            new_param_value = multiplier_value*param_main_value/100

            new_section_dict =\
            nl.nested_update(section_dict, key = affecting_param,value =[new_param_value])

            new_input_data = \
            nl.nested_update(main_input_data, key = section_name,value =new_section_dict)

            inputs.append(new_input_data)

            path = temp.replace("demo_i_j","demo_%s_%s" %(i,j))

            dir_path = os.path.dirname(path)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
                print('Saving inputs to to %s' % path)

            with open(path,'w') as fo:
                json.dump(new_input_data,fo)
    #print(len(inputs))
    return inputs

def create_param_data_name (affected_param,affecting_param_value):

        added_part = "_%%%dG" %(affecting_param_value)
        new_name = "%s" %(affected_param)+added_part

        return new_name

def extract_data (data,to_be_pulled):

    pulled_data = data[to_be_pulled]
    return pulled_data

def dump_data_to_dict (data,key,value):
    data[key]=value

def display_multithreading(data,output_file_string="",t_limits=[],
                            dpi=None):

    num_of_rows = 2
    num_of_cols = 1

    plot_width = 8
    plot_height = 2.5 * num_of_rows
    f = plt.figure(constrained_layout=True)

    f.set_size_inches([plot_width,plot_height])
    spec = gridspec.GridSpec(nrows=num_of_rows, ncols=num_of_cols,figure=f)

    ax0 = f.add_subplot(spec[0,0])
    ax0.plot('time','ventricle_wall_thickness',data=data,label='G')
    ax0.plot('time','ventricle_wall_thickness_%25G',data=data,label='0.25G')
    ax0.plot('time','ventricle_wall_thickness_%50G',data=data,label='0.5G')
    ax0.plot('time','ventricle_wall_thickness_%200G',data=data,label='2G')
    ax0.plot('time','ventricle_wall_thickness_%300G',data=data,label='3G')
    ax0.set_ylabel('LVW_t(mm)')
    ax0.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)
    ax0.tick_params(labelsize=10)

    ax1 = f.add_subplot(spec[1,0])
    ax1.plot('time','number_of_hs',data=data,label='G')
    ax1.plot('time','number_of_hs_%25G',data=data,label='0.25G')
    ax1.plot('time','number_of_hs_%50G',data=data,label='0.5G')
    ax1.plot('time','number_of_hs_%200G',data=data,label='2G')
    ax1.plot('time','number_of_hs_%300G',data=data,label='3G')
    ax1.set_ylabel('nhs')
    ax1.set_xlabel('time (s)')
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax1.legend(bbox_to_anchor=(1.05, 1),fontsize = 10)
    ax1.tick_params(labelsize=10)

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
