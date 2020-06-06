# Functions for myofilament kinetics
import numpy as np
import scipy.constants as scipy_constants
from scipy.integrate import solve_ivp


def evolve_kinetics(self, time_step, Ca_conc):
    """Updates kinetics, switches to different sub-functions as required"""
    if (self.kinetic_scheme == '3state_with_SRX'):
        update_3state_with_SRX(self, time_step, Ca_conc)

def return_fluxes(self, y, Ca_conc):
    # Returns fluxes
    if (self.kinetic_scheme == '3state_with_SRX'):

        # Unpack
        M_OFF = y[0]
        M_ON = y[1]
        M_bound = y[2 + np.arange(self.no_of_x_bins)]
        n_off = y[-2]
        n_on = y[-1]
        n_bound = np.sum(M_bound)

        r1 = np.minimum(self.parent_hs.max_rate,
                        self.k_1 *(1.0 + self.k_force * self.parent_hs.hs_force))
        J1 = r1 * M_OFF

        r2 = np.minimum(self.parent_hs.max_rate, self.k_2)
        J2 = r2 * M_ON

        r3 = self.k_3 * \
                np.exp(-self.k_cb * (self.x**2) /
                    (2.0 * 1e18 * scipy_constants.Boltzmann * self.parent_hs.temperature))
        r3[r3 > self.parent_hs.max_rate] = self.parent_hs.max_rate
        J3 = r3 * self.bin_width * M_ON * (n_on - n_bound)

        r4 = self.k_4_0 + (self.k_4_1 * np.power(self.x, 4))
        r4[r4 > self.parent_hs.max_rate] = self.parent_hs.max_rate
        J4 = r4 * M_bound

        if (self.n_overlap > 0.0):
            Jon = (self.k_on * Ca_conc * (self.n_overlap - n_on) *
                (1.0 + self.k_coop * (n_on / self.n_overlap)))
        else:
            Jon = 0.0

        if (self.n_overlap > 0.0):
            Joff = self.k_off * (n_on - n_bound) * \
                (1.0 + self.k_coop * ((self.n_overlap - n_on) /
                                      self.n_overlap))
        else:
            Joff = 0.0

        fluxes = dict()
        fluxes['J1'] = J1
        fluxes['J2'] = J2
        fluxes['J3'] = J3
        fluxes['J4'] = J4
        fluxes['Jon'] = Jon
        fluxes['Joff'] = Joff

        return fluxes


def update_3state_with_SRX(self, time_step, Ca_conc):
    """ Updates kinetics for thick and thin filaments """

    # Pull out the myofilaments vector
    y = self.y

    # Get the overlap
    self.n_overlap = self.return_n_overlap()

    def derivs(t, y):
        dy = np.zeros(np.size(y))

        fluxes = return_fluxes(self, y, Ca_conc)

        # Calculate the derivs
        dy[0] = -fluxes['J1'] + fluxes['J2']
        dy[1] = (fluxes['J1'] + np.sum(fluxes['J4'])) - \
            (fluxes['J2'] + np.sum(fluxes['J3']))
        J3 = fluxes['J3']
        J4 = fluxes['J4']
        for i in np.arange(0, self.no_of_x_bins):
            dy[i + 2] = J3[i] - J4[i]
        dy[-2] = -fluxes['Jon'] + fluxes['Joff']
        dy[-1] = fluxes['Jon'] - fluxes['Joff']
        return dy

    # Evolve the system
    sol = solve_ivp(derivs, [0, time_step], y, method='RK23')
    self.y = sol.y[:, -1]
    self.n_on = y[-1]
    self.n_bound = np.sum(self.y[2 + np.arange(0, self.no_of_x_bins)])

    # Do some tidying for extreme situations
    self.y[np.nonzero(self.y > 1.0)] = 1.0
    self.y[np.nonzero(self.y < 0.0)] = 0.0
    sum_of_heads = np.sum(self.y[np.arange(2+self.no_of_x_bins)])
    # These appear in M_off
    self.y[0] = self.y[0] + (1.0-sum_of_heads)

#    print("Total: %f" % np.sum(self.y[np.arange(0, self.no_of_x_bins+2)]))
#    if any(self.y < -1e-2):
#        print(self.y)
#        print("self.y is less than 0")
#        quit()
    #
def return_ATPase(self,wall_volume):

    N0 = self.parent_hs.cb_number_density
    delta_G = self.parent_hs.delta_G

    L0 = 1e-9*self.parent_hs.L0
    N_A = self.parent_hs.N_A

    fluxes = return_fluxes(self,self.y,self.parent_hs.Ca_conc)
    J4 = np.sum(fluxes['J4'])
    # convert liter to meter^3
    w_vol = wall_volume*0.001

    self.ATPase = (N0 * w_vol * delta_G * J4)/(L0 * N_A)

    return self.ATPase
