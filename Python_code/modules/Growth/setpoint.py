import numpy as np
import pandas as pd

def growth_driver(self):
    if self.growth["driven_signal"][0] == "stress":
        self.passive_stress_null = 1.06*np.mean(self.hs.hs_data["pas_force"][:self.start_index+1])
        self.gr_data['pas_force_null'] =\
        pd.Series(np.full(self.data_buffer_size,self.passive_stress_null))

        self.cb_stress_null = 1.105*np.mean(self.hs.hs_data["cb_force"][:self.start_index+1])
        self.gr_data['cb_force_null'] = \
        pd.Series(np.full(self.data_buffer_size,self.cb_stress_null))
        print('***')
        print('Growth module is activated!')
        print('with passive force_null of ',self.passive_stress_null)
        print('and active force_null of',self.cb_stress_null)
        print('***')

    if self.growth["driven_signal"][0] == "strain":
        self.strain_null = np.mean(self.data["cell_strain"][:self.start_index+1])
        self.data['cell_strain_null'] = \
        pd.Series(np.full(self.output_buffer_size,self.cell_strain_null))
        print('cell_strain_null',self.cell_strain_null)
        self.wall_thickness = \
        self.gr.return_lv_wall_thickness_strain(time_step,self.strain,self.cell_strain_null)
        #eccentric
        #new_number_of_hs = \
        self.n_hs = \
        self.gr.return_number_of_hs_strain(time_step,self.strain,
        self.cell_strain_null)

    #return setpoint
