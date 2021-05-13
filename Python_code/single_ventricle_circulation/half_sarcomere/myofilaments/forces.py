# Functions relating to forces
import numpy as np
import scipy.optimize as opt


def set_myofilament_stress(self):
    """ Sets initial values """

    d = self.check_myofilament_forces(0.0)
    self.myofil_stress = d['myofil_stress']
    self.hs_force = d['hs_force']

def check_myofilament_forces(self, delta_hsl):

    d = dict()
    d['cb_stress'] = return_cb_stress(self, delta_hsl)
    d['int_pas_stress'] = return_intracellular_passive_stress(self, delta_hsl)
    d['ext_pas_stress'] = return_extracellular_passive_stress(self, delta_hsl)

    d['myofil_stress'] = d['cb_stress'] + d['int_pas_stress']

    d['cb_force'] = (1.0 - self.data['prop_fibrosis']) * \
                        self.data['prop_myofilaments'] * d['cb_stress']
    d['int_pas_force'] = (1.0 - self.data['prop_fibrosis']) * \
                        self.data['prop_myofilaments'] * d['int_pas_stress']
    d['ext_pas_force'] = self.data['prop_fibrosis'] * d['ext_pas_stress']

    d['hs_force'] = d['cb_force'] + d['int_pas_force'] + d['ext_pas_force']

    return d


def return_cb_stress(self, delta_hsl):

    if (self.implementation['kinetic_scheme'] == '3_state_with_SRX' or \
        self.implementation['kinetic_scheme'] == '3_state_with_SRX_and_exp_detach'):
        bin_pops = self.y[2 + np.arange(0, self.no_of_x_bins)]
        cb_stress = \
            self.data['cb_number_density'] * \
            self.data['k_cb'] * 1e-9 * \
            np.sum(bin_pops *
                   (self.x + self.data['x_ps'] +
                    (self.implementation['filament_compliance_factor'] *
                     delta_hsl)))
        return cb_stress

    elif (self.implementation['kinetic_scheme'] == '4_state_with_SRX' or \
        self.implementation['kinetic_scheme'] == '4_state_with_SRX_and_exp_detach'):
        pre_ind = 2 + np.arange(0, self.no_of_x_bins)
        post_ind = 2 + self.no_of_x_bins + np.arange(0, self.no_of_x_bins)
        
        cb_stress = \
            self.data['cb_number_density'] * self.data['k_cb'] * 1e-9 * \
                (np.sum(self.y[pre_ind] *
                        (self.x + 
                         (self.implementation['filament_compliance_factor']
                          * delta_hsl))) +
                 np.sum(self.y[post_ind] * \
                        (self.x + self.data['x_ps'] +
                         (self.implementation['filament_compliance_factor'] *
                          delta_hsl))))

        return cb_stress


def return_intracellular_passive_stress(self, delta_hsl):

    if (self.implementation['int_passive_mode'] == 'linear'):
        pas_force = self.data['int_passive_linear_k_p'] * \
            (self.parent_hs.data['hs_length'] + delta_hsl -
             self.data['int_passive_l_slack'])

    if (self.implementation['int_passive_mode'] == 'exponential'):
        x = self.parent_hs.data['hs_length'] + delta_hsl - \
                self.data['int_passive_l_slack']
        if (x > 0):
            pas_force = self.data['int_passive_exp_sigma'] * \
                (np.exp(x / self.data['int_passive_exp_L']) - 1.0)
        else:
            pas_force = -self.data['int_passive_exp_sigma'] * \
                (np.exp(np.abs(x) / 
                        self.data['int_passive_exp_L']) - 1.0)

    return pas_force

def return_extracellular_passive_stress(self, delta_hsl):

    if (self.implementation['ext_passive_mode'] == 'linear'):
        pas_force = self.data['ext_passive_linear_k_p'] * \
            (self.parent_hs.data['hs_length'] + delta_hsl -
             self.data['ext_passive_l_slack'])

    if (self.implementation['ext_passive_mode'] == 'exponential'):
        x = self.parent_hs.data['hs_length'] + delta_hsl - \
                self.data['ext_passive_l_slack']
        if (x > 0):
            pas_force = self.data['ext_passive_exp_sigma'] * \
                (np.exp(x / self.data['ext_passive_exp_L']) - 1.0)
        else:
            pas_force = -self.data['ext_passive_exp_sigma'] * \
                (np.exp(np.abs(x) / 
                        self.data['ext_passive_exp_L']) - 1.0)

    return pas_force

def return_hs_length_for_force(self, force):
    
    def f(dx):
        d = check_myofilament_forces(self, dx)
        return d['hs_force']
    
    sol = opt.brentq(f,-500, 500)
    return self.parent_hs.data['hs_length'] + sol
