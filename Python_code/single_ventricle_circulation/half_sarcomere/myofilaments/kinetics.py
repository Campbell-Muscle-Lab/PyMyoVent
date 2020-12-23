# Functions for myofilament kinetics
import numpy as np
import scipy.constants as scipy_constants
from scipy.integrate import solve_ivp

def evolve_kinetics(self, time_step, Ca_conc):
    """Updates kinetics, switches to different sub-functions as required"""
    if (self.model['kinetic_scheme'] == '3_state_with_SRX'):
        update_3_state_with_SRX(self, time_step, Ca_conc)


def update_3_state_with_SRX(self, time_step, Ca_conc):
    """ Updates kinetics for thick and thin filaments """

    # Pull out the myofilaments vector
    y = self.y

    # Get the overlap
    self.n_overlap = self.return_f_overlap()

    def derivs(t, y):
        dy = np.zeros(np.size(y))

        fluxes = return_fluxes(self, y, Ca_conc)

        # Calculate the derivs
        dy[0] = -fluxes['J_1'] + fluxes['J_2']
        dy[1] = (fluxes['J_1'] + np.sum(fluxes['J_4'])) - \
            (fluxes['J_2'] + np.sum(fluxes['J_3']))
        J_3 = fluxes['J_3']
        J_4 = fluxes['J_4']
        for i in np.arange(0, self.no_of_x_bins):
            dy[i + 2] = J_3[i] - J_4[i]
        dy[-2] = -fluxes['J_on'] + fluxes['J_off']
        dy[-1] = fluxes['J_on'] - fluxes['J_off']
        return dy

    # Evolve the system
    sol = solve_ivp(derivs, [0, time_step], y, method='RK23')
    self.y = sol.y[:, -1]

    # Do some tidying for extreme situations
    self.y[np.nonzero(self.y > 1.0)] = 1.0
    self.y[np.nonzero(self.y < 0.0)] = 0.0
    sum_of_heads = np.sum(self.y[np.arange(2+self.no_of_x_bins)])
    # These appear in M_off
    self.y[0] = self.y[0] + (1.0-sum_of_heads)

    self.fluxes = return_fluxes(self, self.y, Ca_conc)


def return_fluxes(self, y, Ca_conc):
    # Returns fluxes
    if (self.model['kinetic_scheme'] == '3_state_with_SRX'):

        # Unpack
        M_SRX = y[0]
        M_DRX = y[1]
        M_FG = y[2 + np.arange(self.no_of_x_bins)]
        n_on = y[-1]
        n_bound = np.sum(M_FG)

        r_1 = np.minimum(self.model['max_rate'],
                        self.model['k_1'] * 
                        (1.0 + self.model['k_force'] * self.parent_hs.hs_force))
        J_1 = r_1 * M_SRX

        r_2 = np.minimum(self.model['max_rate'], self.model['k_2'])
        J_2 = r_2 * M_DRX

        r_3 = self.model['k_3'] * \
                np.exp(-self.model['k_cb'] * (self.x**2) /
                    (2.0 * 1e18 * scipy_constants.Boltzmann * 
                         self.model['temperature']))
        r_3[r_3 > self.model['max_rate']] = self.model['max_rate']
        J_3 = r_3 * self.model['bin_width'] * M_DRX * (n_on - n_bound)

        r_4 = self.model['k_4_0'] + (self.model['k_4_1'] * np.power(self.x, 4))
        r_4[r_4 > self.model['max_rate']] = self.model['max_rate']
        J_4 = r_4 * M_FG
        if (self.n_overlap > 0.0):
            J_on = (self.model['k_on'] * Ca_conc * (self.n_overlap - n_on) *
                (1.0 + self.model['k_coop'] * (n_on / self.n_overlap)))
        else:
            J_on = 0.0

        if (self.n_overlap > 0.0):
            J_off = self.model['k_off'] * (n_on - n_bound) * \
                (1.0 + self.model['k_coop'] * ((self.n_overlap - n_on) /
                                      self.n_overlap))
        else:
            J_off = 0.0

        fluxes = dict()
        fluxes['J_1'] = J_1
        fluxes['J_2'] = J_2
        fluxes['J_3'] = J_3
        fluxes['J_4'] = J_4
        fluxes['J_on'] = J_on
        fluxes['J_off'] = J_off

        return fluxes


# def return_ATPase(self,wall_volume):

#     N0 = self.parent_hs.cb_number_density
#     delta_G = self.parent_hs.delta_G

#     L0 = 1e-9*self.parent_hs.L0
#     N_A = self.parent_hs.N_A

#     fluxes = return_fluxes(self,self.y,self.parent_hs.Ca_conc)
#     J4 = np.sum(fluxes['J4'])
#     # convert liter to meter^3
#     w_vol = wall_volume*0.001

#     self.ATPase = (N0 * w_vol * delta_G * J4)/(L0 * N_A)

#     return self.ATPase
