import numpy as np
import pandas as pd

def steady_state_identifier(self):

    #avg_total_force should be an array which includes
    # the avg_total_force for the last #memoory cardiac cycle

    if len(set(self.avg_total_force_array[-self.memory:]))==1:
        self.steady_state = True
    else:
        self.steady_state = False
    #print(self.steady_state)
def avg_total_force (self):
    print('self.avg_counter',self.avg_counter)

    self.avg_total_force_array=np.append(self.avg_total_force_array,
                                np.mean(self.total_force_array))
    self.avg_counter +=1
    """if self.avg_counter <= self.memory:

        self.avg_total_force_array[self.avg_counter] =\
         np.mean(self.total_force_array)
        self.avg_counter += 1

    else:

        self.avg_total_force_array = \
        np.roll(self.avg_total_force_array,-1)

        self.avg_total_force_array[self.memory] =\
         np.mean(self.total_force_array)

        self.avg_counter +=1"""
    #print(self.avg_total_force_array)
def return_force_array_per_cycle(self,time_step,heart_period,total_force):


    if self.counter < 0:
        avg_total_force(self)
        self.force_counter=int(heart_period/time_step)
        self.counter = self.force_counter

        self.total_force_array=np.zeros(self.force_counter+1)
        return
    i=self.force_counter - self.counter
    #print(i)
    self.total_force_array[i] = total_force

    self.counter -= 1

def update_data_holder(self,time_step):

    self.sys_time = self.sys_time + time_step
    self.data_buffer_index += 1
    self.gr_data.at[self.data_buffer_index, 'average_force']=\
                                    self.avg_total_force_array[-1]
    self.gr_data.at[self.data_buffer_index, 'cycle_counter']= self.avg_counter
