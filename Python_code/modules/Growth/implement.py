import numpy as np
import pandas as pd

def steady_state_identifier(self,avg_total_force):

    #avg_total_force should be an array which includes
    # the avg_total_force for the last #memoory cardiac cycle

    if len(set(self.avg_total_force_array))==1:
        self.steady_state = True
    else:
        self.steady_state = False

def avg_total_force (self):
    if self.avg_counter =< self.memory:

        self.avg_total_force_array[self.avg_counter] =\
         self.total_force_array/self.force_counter
    else:
        self.avg_total_force_array = \
        np.roll(self.avg_total_force_array,-1)
        self.avg_total_force_array[self.memory] =\
         self.total_force_array/self.force_counter

def return_force_array_per_cycle(self,time_step,heart_period,total_force):


    if self.counter < 0:
        avg_total_force(self.total_force_array)
        self.force_counter=heart_period/time_step
        self.counter = self.force_counter

        self.total_force_array=np.zeros(self.force_counter)
        return
    i=self.force_counter - self.counter
    self.total_force_array[i] = total_force
    self.counter -= 1
