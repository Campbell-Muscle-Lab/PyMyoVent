import numpy as np
import pandas as pd

from .membranes import membranes as memb
from .energetics import energetics as ener
from .myofilaments import myofilaments as myof


class half_sarcomere():
    """Class for a half-sarcomere"""

    def __init__(self, hs_struct, parent_circulation):

        # Store the parent circulation
        self.parent_circulation = parent_circulation

        # Create a dict to store half-sarcomere specific data
        self.data = dict()
        self.data['hs_length'] = hs_struct['initial_hs_length']
        self.data['slack_hs_length'] = 0
        self.data['cpt_cb_stress'] = 0
        self.data['cpt_int_pas_stress'] = 0
        self.data['cpt_ext_pas_stress'] = 0
        self.data['cpt_myofil_stress'] = 0
        self.data['cb_stress'] = 0
        self.data['int_pas_stress'] = 0
        self.data['ext_pas_stress'] = 0
        self.data['hs_stress'] = 0

        # Pull off membrane parameters
        membrane_struct = hs_struct["membranes"]
        self.memb = memb.membranes(membrane_struct, self)

        # Pull off the mofilament_params
        myofil_struct = hs_struct["myofilaments"]
        self.myof = myof.myofilaments(myofil_struct, self)

        # Pull of energetics parameters if appropriate
        if ('energetics' in hs_struct):
            energetics_struct = hs_struct["energetics"]
            self.ener = ener.energetics(energetics_struct, self)


    def update_simulation(self, time_step, delta_hsl,
                          activation):

        if (time_step > 0.0):
            # Need to do some kinetics stuff

            # Update calcium
            self.memb.implement_time_step(time_step,
                                           activation)

            # Update energetics if appropriate
            if hasattr(self, 'ener'):
                self.ener.implement_time_step(time_step)

            # Myofilaments
            self.myof.evolve_kinetics(time_step,
                                      self.memb.data['Ca_cytosol'])

        if (np.abs(delta_hsl) > 0.0):
            # Need to move some things
            self.myof.move_cb_distributions(delta_hsl)
            self.data['hs_length'] = self.data['hs_length'] + delta_hsl

        # Update forces
        self.myof.set_myofilament_stresses()
        self.hs_stress = self.myof.hs_stress
        
    def update_data(self, new_beat):
        # First update own object data
        f = self.myof.check_myofilament_stresses(0)
        for key in f.keys():
            self.data[key] = f[key]
        
        # Now update other components
        self.memb.update_data()
        if hasattr(self, 'ener'):
            self.ener.update_data()
        self.myof.update_data()
