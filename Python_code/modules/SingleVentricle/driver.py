# Code for driving simulations
from modules.untangle import untangle as ut
from modules.SingleVentricle.SingleVentricle import single_circulation
import json

def return_sim_struct_from_xml_file(xml_file_string):
    xml_struct = ut.parse(xml_file_string)
    sim_struct = xml_struct.single_circulation_simulation
    return sim_struct

def run_simulation_from_xml_file(xml_file_string):
    # First get the data struct for the model
    sim_struct = return_sim_struct_from_xml_file(xml_file_string)

    # Now create a single circulation object
    sim_object = single_circulation(sim_struct, xml_file_string)
    # Now run the simulation
    sim_object.run_simulation()

def run_simulation_from_json_file(json_file_string):

    with open(json_file_string,'r') as f:
        json_input_data = json.load(f)

    sim_object = single_circulation(json_input_data)
    sim_object.run_simulation()
