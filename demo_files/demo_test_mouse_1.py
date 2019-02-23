# Code for testing growth
import numpy as np
import pandas as pd
try:
    import Python_single_ventricle as sc
    import Python_MyoSim.half_sarcomere as myosim
    import untangle as ut
except:
    import sys
    print(sys.path)
    sys.path.append('c:\\ken\\github\\campbellmusclelab\\python\\modules')
    import Python_single_ventricle as sc
    import Python_MyoSim.half_sarcomere as myosim

# Set path to xml file
xml_file_string = 'input_data\\test_mouse_1.xml'

# Run simulation
sc.run_simulation_from_xml_file(xml_file_string)