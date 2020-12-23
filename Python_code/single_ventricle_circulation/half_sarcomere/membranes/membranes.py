import numpy as np
from scipy.integrate import solve_ivp

# from functools import partial

# from .Ten_Tusscher_2004 import computeRates_with_activation as \
# tt_computeRates_with_activation
# from .Ten_Tusscher_2004 import initConsts_with_adjustments as \
# tt_initConsts_with_adjustments
# from .Ten_Tusscher_2004 import compureRatesonly as tt_computeRatesonly
# from .Shannon_Bers_2004 import initConsts as sb_initConsts
# from .Shannon_Bers_2004 import computeRates as sb_computeRates
# #from .Grandi_2009 import initConsts as g_initConsts
# #from .Grandi_2009 import computeRates as g_coputeRates

class membranes():
    """ Class for membranes """

    def __init__(self, membrane_struct, parent_half_sarcomere):
        self.parent_hs = parent_half_sarcomere;

        # Set up a dict for the membranes
        self.model = dict()

        # Load in the model
        params = list(membrane_struct.keys())
        for p in params:
            self.model[p] = membrane_struct[p]

        # Create structures to store data. These will be filled
        # by model appropriate fields and values
        self.data = dict()
        self.flux_fields = []
        self.y = []
        
        # Model specific setup
        if (self.model['kinetic_scheme'] == 'simple_2_compartment'):
            self.set_up_simple_2_compartment()

    def implement_time_step(self, time_step, activation):
        """ Evolve kinetics and then update data """
        self.evolve_kinetics(time_step, activation)
        self.update_data()

    def set_up_simple_2_compartment(self):
       # Set up data fields
        data_fields = ['membrane_activation', 'Ca_cytosol', 'Ca_SR', 't_act_left']
        self.flux_fields = ['J_release', 'J_uptake']
        data_fields = data_fields + self.flux_fields
    
        # Initialise the y vector
        self.y_length = 2
        self.y = np.zeros(self.y_length)
        # Start with Ca in SR
        self.y[1] = self.model['Ca_content']

        # Initialise the data dict        
        for f in data_fields:
            self.data[f] = 0
        self.fluxes = dict()
        for f in self.flux_fields:
            self.fluxes[f] = 0
        self.update_data()
        
    def update_data(self):
        # Update model dict for reporting back to half_sarcomere
        
        if (self.model['kinetic_scheme'] == 'simple_2_compartment'):
            self.data['Ca_cytosol'] = self.y[0]
            self.data['Ca_SR'] = self.y[1]
            
            for f in self.flux_fields:
                self.data[f] = self.fluxes[f] 
                
    def evolve_kinetics(self, time_step, activation):
        """ evolves kinetics """

        if (self.model['kinetic_scheme'] == "simple_2_compartment"):
            # Pull out the v vector
            y = self.y

            if (activation > 0):
                self.data['t_act_left'] = self.model['t_open']

            def derivs(t, y):
                fluxes = self.return_fluxes(y)
                dy = np.zeros(np.size(y))
                dy[0] = fluxes['J_release'] - fluxes['J_uptake']
                dy[1] = -dy[0]
                
                return dy

            # Evolve
            sol = solve_ivp(derivs, [0, time_step], y, method = 'RK23')
            self.y = sol.y[:, -1]
            
            # Decrement t_act_left
            self.data['t_act_left'] = self.data['t_act_left'] - time_step
            if (self.data['t_act_left'] < 0):
                self.data['t_act_left'] = 0
                
            # Update activation
            self.data['membrane_activation'] = activation
       
            
    def return_fluxes(self, y):
        """ Return fluxes """
        
        if (self.model['kinetic_scheme'] == 'simple_2_compartment'):
            
            Ca_cytosol = y[0]
            Ca_SR = y[1]
            
            if (self.data['t_act_left'] > 0):
                act = 1
            else:
                act = 0;
            
            J_release = ((self.model['k_leak'] +
                         (act * self.model['k_act'])) * Ca_SR)
            J_uptake = self.model['k_serca'] * Ca_cytosol

            fluxes = dict()
            fluxes['J_release'] = J_release
            fluxes['J_uptake'] = J_uptake
            
            return fluxes