import numpy as np


class myofilaments():
    """Class for myofilaments"""

    from .kinetics import evolve_kinetics, return_fluxes
    from .move import move_cb_distributions
    from .forces import set_myofilament_forces, check_myofilament_forces, \
        return_hs_length_for_force, return_passive_force

    def __init__(self, myofil_struct, parent_half_sarcomere):
        self.parent_hs = parent_half_sarcomere

        # Set up a dict for the myofilaments
        self.model = dict()
        
        params = myofil_struct.keys()
        for p in params:
            self.model[p] = myofil_struct[p]
        
        self.x = np.arange(self.model['bin_min'],
                           self.model['bin_max']+
                               self.model['bin_width'],
                           self.model['bin_width'])
        self.no_of_x_bins = np.size(self.x)
        self.f_overlap = self.return_f_overlap()

        # Set up the rates and the y vector which are kinetics specific
        if (self.model['kinetic_scheme'] == '3state_with_SRX'):
            self.set_up_3state_with_SRX()
            
                
            

        # Initialise forces and then update
        self.cb_force = 0.0
        self.pas_force = 0.0
        self.total_force= 0.0
        self.set_myofilament_forces()
    
    def set_up_3state_with_SRX(self):
        # Set up data fields and variables
        
        self.data_fields = ['M_SRX', 'M_DRX', 'M_FG',
                       'n_off', 'n_on', 'n_bound',
                       'N_overlap']
        self.flux_fields = ['J_1','J_2','J_3','J_4','J_on','J_off']
        self.data_fields = self.data_fields + self.flux_fields
        
        print(self.data_fields)
        
        self.y_length = self.no_of_x_bins + 4
        self.y = np.zeros(self.y_length)
        # Start with all myosins in M1 and all binding sites off
        self.y[0] = 1.0
        self.y[-2] = 1.0
        
        # Create a dict to monitor status
        self.data=dict()
        for f in self.data_fields:
            self.data[f] = 0
        self.fluxes = dict()
        for f in self.flux_fields:
            self.fluxes[f] = 0
        self.n_overlap = self.return_f_overlap()
        self.update_data()        
        
            
    def update_data(self):
    
        if (self.model['kinetic_scheme'] == '3state_with_SRX'):
            self.data['M_SRX'] = self.y[0]
            self.data['M_DRX'] = self.y[1]
            self.data["M_FG"] = np.sum(self.y[np.arange(2+self.no_of_x_bins)])
            self.data['n_off'] = self.y[-2]
            self.data['n_on'] = self.y[-1]
            self.data["n_overlap"] = self.n_overlap
      
            for f in self.flux_fields:
                self.data[f] = self.fluxes[f]


    def return_f_overlap(self):
        """ returns n_overlap """
        x_no_overlap = self.parent_hs.hs_length - \
            self.model['thick_filament_length']
        x_overlap = self.model['thin_filament_length'] - \
            x_no_overlap
        max_x_overlap = self.model['thick_filament_length'] - \
            self.model['bare_zone_length']

        if (x_overlap < 0.0):
            f_overlap = 0.0

        if ((x_overlap > 0.0) & (x_overlap <= max_x_overlap)):
            f_overlap = x_overlap / max_x_overlap

        if (x_overlap > max_x_overlap):
            f_overlap = 1.0

        protrusion = self.model['thin_filament_length'] - \
            (self.parent_hs.hs_length + self.model['bare_zone_length'])
            
        if (protrusion > 0.0):
            x_overlap = (max_x_overlap - protrusion)
            f_overlap = x_overlap / max_x_overlap

        return f_overlap
