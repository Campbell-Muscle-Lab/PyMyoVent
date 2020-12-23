import numpy as np
import pandas as pd
from .myofilaments import myofilaments as myof
from .membranes import membranes as memb


class half_sarcomere():
    """Class for a half-sarcomere"""

    from .display import display_fluxes
    #from .update_contractility import update_contractility

    def __init__(self, hs_struct):
        
        # Create a dict to store data
        self.data = dict()
        self.data['hs_length'] = hs_struct['initial_hs_length']
        self.data['slack_hs_length'] = 0
        self.data['hs_force'] = 0
        self.data['cb_force'] = 0
        self.data['pas_force'] = 0        

        # Pull of membrane parameters
        membrane_struct = hs_struct["membranes"]
        self.memb = memb.membranes(membrane_struct, self)

        # Pull off the mofilament_params
        myofil_struct = hs_struct["myofilaments"]
        self.myof = myof.myofilaments(myofil_struct, self)

    def update_simulation(self, time_step, delta_hsl, activation):

        if (time_step > 0.0):
            # Need to do some kinetics stuff
    
            # Update calcium
            self.memb.implement_time_step(time_step,
                                           activation)
    
            # Myofilaments
            self.myof.evolve_kinetics(time_step,
                                      self.memb.data['Ca_cytosol'])
    
        if (np.abs(delta_hsl) > 0.0):
            # Need to move some things
            self.myof.move_cb_distributions(delta_hsl)
            self.hs_length = self.hs_length + delta_hsl
    
        # Update forces
        self.myof.set_myofilament_forces()
        self.hs_force = self.myof.total_force
        
    def update_data(self):
        # First update own object data
        f = self.myof.check_myofilament_forces(0)
        self.data['hs_force'] = f['total_force']
        self.data['pas_force'] = f['pas_force']
        self.data['cb_force'] = f['cb_force']
        
        # Now update membrane and myofilaments
        self.memb.update_data()
        self.myof.update_data()
