

def write_complete_data_to_sim_data(self, index):
    """ Writes full data to data frame """

    for f in list(self.data.keys()):
        if (f not in ['p', 'v', 's', 'compliance', 'resistance', 'f']):
            self.sim_data.at[self.write_counter, f] = self.data[f]
    for f in list(self.hr.data.keys()):
        self.sim_data.at[self.write_counter, f] = self.hr.data[f]
    for f in list(self.hs.data.keys()):
        self.sim_data.at[self.write_counter, f] = self.hs.data[f]
    for f in list(self.hs.memb.data.keys()):
        self.sim_data.at[self.write_counter, f] = self.hs.memb.data[f]
    for f in list(self.hs.myof.data.keys()):
        self.sim_data.at[self.write_counter, f] = self.hs.myof.data[f]
    if (self.br):
        for f in list(self.br.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.br.data[f]
    if (self.gr):
        for f in list(self.gr.data.keys()):
            self.sim_data.at[self.write_counter, f] = self.gr.data[f]
    self.sim_data.at[self.write_counter, 'write_mode'] = 'complete'
    self.write_counter = self.write_counter + 1


def write_complete_data_to_envelope_data(self, index):
    """ Writes full data to envelope frame """

    for f in list(self.data.keys()):
        if (f not in ['p', 'v', 's', 'compliance', 'resistance', 'f']):
            self.envelope_data.at[self.envelope_counter, f] = self.data[f]
    for f in list(self.hr.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hr.data[f]
    for f in list(self.hs.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.data[f]
    for f in list(self.hs.memb.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.memb.data[f]
    for f in list(self.hs.myof.data.keys()):
        self.envelope_data.at[self.envelope_counter, f] = self.hs.myof.data[f]
    if (self.br):
        for f in list(self.br.data.keys()):
            self.envelope_data.at[self.envelope_counter, f] = self.br.data[f]
    if (self.gr):
        for f in list(self.gr.data.keys()):
            self.envelope_data.at[self.envelope_counter, f] = self.gr.data[f]
    self.envelope_data.at[self.envelope_counter, 'write_mode'] = 'complete'
    self.envelope_counter = self.envelope_counter + 1
    # Reset counter at limit
    if (self.envelope_counter == self.so.data['n_envelope_points']):
        self.envelope_counter = 0


def write_envelope_data_to_sim_data(self, index):
    """ Writes envelope data to data frame """

    # Cycle through picking off min and max values in envelope
    for f in list(self.data.keys()):
        if (f not in ['p', 'v', 's', 'compliance', 'resistance', 'f']):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hr.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.memb.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    for f in list(self.hs.myof.data.keys()):
        min_value, max_value = self.return_min_max(
            self.envelope_data[f])
        self.sim_data.at[self.write_counter, f] = min_value
        self.sim_data.at[self.write_counter+1, f] = max_value
    if (self.br):
        for f in list(self.br.data.keys()):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    if (self.gr):
        for f in list(self.gr.data.keys()):
            min_value, max_value = self.return_min_max(
                self.envelope_data[f])
            self.sim_data.at[self.write_counter, f] = min_value
            self.sim_data.at[self.write_counter+1, f] = max_value
    self.sim_data.at[self.write_counter, 'write_mode'] = 'envelope'
    self.sim_data.at[self.write_counter+1, 'write_mode'] = 'envelope'
    self.write_counter = self.write_counter + 2
