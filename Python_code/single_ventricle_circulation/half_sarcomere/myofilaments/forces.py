# Functions relating to forces
import numpy as np
import scipy.optimize as opt


def set_myofilament_forces(self):
    self.cb_force = self.return_cb_force(0.0)
    self.pas_force = self.return_passive_force(0.0)
    self.total_force = self.cb_force + self.pas_force


def check_myofilament_forces(self, delta_hsl):
    d = dict()
    d['cb_force'] = return_cb_force(self, delta_hsl)
    d['pas_force'] = return_passive_force(self, delta_hsl)
    d['total_force'] = d['cb_force'] + d['pas_force']
    return d


def return_cb_force(self, delta_hsl):
    if (self.model['kinetic_scheme'] == '3_state_with_SRX'):
        bin_pops = self.y[2 + np.arange(0, self.no_of_x_bins)]
        cb_force = \
            self.model['cb_number_density'] * \
            self.model['k_cb'] * 1e-9 * \
            np.sum(bin_pops * (self.x + self.model['x_ps'] +
                               (self.model['filament_compliance_factor']
                                    * delta_hsl)))
        return cb_force


def return_x(self,x):
    return x


def return_passive_force(self, delta_hsl):

    if (self.model['passive_mode'] == 'linear'):
        pas_force = self.model['passive_linear_k_p'] * \
            (self.parent_hs.data['hs_length'] + delta_hsl -
             self.model['passive_l_slack'])

    if (self.model['passive_mode'] == 'exponential'):
        x = self.parent_hs.data['hs_length'] + delta_hsl - \
                self.model['passive_l_slack']
        if (x > 0):
            pas_force = self.model['passive_exp_sigma'] * \
                (np.exp(x / self.model['passive_exp_L']) - 1.0)
        else:
            pas_force = -self.model['passive_exp_sigma'] * \
                (np.exp(np.abs(x) / 
                        self.model['passive_exp_L']) - 1.0)

    return pas_force


def return_hs_length_for_force(self, force):
    
    def f(dx):
        d = check_myofilament_forces(self, dx)
        return d['total_force']
    
    sol = opt.brentq(f,-500, 500)
    return self.parent_hs.data['hs_length'] + sol
