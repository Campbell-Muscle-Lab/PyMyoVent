import numpy as np
import pandas as pd

def growth_driver(self):

    i=self.start_index
#0.88, 0.95
    self.pass_array = np.array(self.hs.hs_data["pas_force"][:i+1])

    self.passive_stress_null =\
        1*((self.hs.hs_data["pas_force"].iloc[int(i/2):i+1]).mean())
    self.gr_data['pas_force_null'] =\
    pd.Series(np.full(self.data_buffer_size,self.passive_stress_null))


    print('***')
    print('Growth module is activated!')
    print('with passive force_null of ',self.passive_stress_null)

    if self.growth["driven_signal"][0] == "stress":
#1.23, 1.1
        self.cb_array = np.array(self.hs.hs_data["cb_force"][:i+1])
        self.cb_stress_null =\
            1*self.hs.hs_data["cb_force"].iloc[int(i/2):i+1].mean()
        self.gr_data['cb_force_null'] = \
        pd.Series(np.full(self.data_buffer_size,self.cb_stress_null))

        print('and active force_null of',self.cb_stress_null)
        print('***')

    if self.growth["driven_signal"][0] == "ATPase":

        self.ATPase_array = np.array(self.hs.hs_data["ATPase"][:i+1])
        self.ATPase_null = \
            ((self.hs.hs_data["ATPase"][int(i/2):i+1]).mean())
        self.gr_data["ATPase_null"] = \
            pd.Series(np.full(self.data_buffer_size,self.ATPase_null))

        print('and ATPase_null of',self.ATPase_null)
        print('***')
