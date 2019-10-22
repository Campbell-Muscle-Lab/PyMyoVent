## Model files

## Overview

Here is PyMyoVent's default model. You can find the file in
`<repo>demo_files\demo_1\demo_1_model.xml`

It's written in [xml format](https://en.wikipedia.org/wiki/XML). The different components are described below.

````
<?xml version="1.0" encoding="windows-1252"?>
<single_circulation_simulation>

<simulation_parameters>
	<no_of_time_points>3000</no_of_time_points>
	<time_step>0.001</time_step>
	<activation_frequency>1</activation_frequency>
	<duty_ratio>0.3</duty_ratio>
</simulation_parameters>

<output_parameters>
	<data_file>..\temp\demo_1\demo_1.xlsx</data_file>
	<summary_figure>..\temp\demo_1\demo_1_summary.png</summary_figure>
	<pv_figure>..\temp\demo_1\demo_1_pv.png</pv_figure>
	<flows_figure>..\temp\demo_1\demo_1_flows.png</flows_figure>
	<hs_fluxes_figure>..\temp\demo_1\demo_1_hs_fluxes.png</hs_fluxes_figure>
</output_parameters>

<circulation>
	<no_of_compartments>6</no_of_compartments>
	<blood>
		<volume units="liters">5</volume>
	</blood>
	<aorta>
		<resistance units="s">20</resistance>
		<compliance units="liter_per_mmHg">0.002</compliance>
	</aorta>
	<arteries>
		<resistance units="g">40</resistance>
		<compliance units="g2">0.001</compliance>
	</arteries>
	<arterioles>
		<resistance units="g">200</resistance>
		<compliance units="g2">0.001</compliance>
	</arterioles>
	<capillaries>
		<resistance units="g">100</resistance>
		<compliance units="g2">0.005</compliance>
	</capillaries>
	<veins>
		<resistance units="g">100</resistance>
		<compliance units="liters_per_mmHg">0.35</compliance>
	</veins>
	<ventricle>
		<resistance units="g">20</resistance>
		<wall_volume units="liters">0.03</wall_volume>
		<slack_volume units = "liters">0.08</slack_volume>
	</ventricle>
</circulation>

<half_sarcomere>
	<max_rate>5000</max_rate>
	<temperature>288</temperature>
	
	<cb_number_density>6.9e16</cb_number_density>
	<initial_hs_length>900</initial_hs_length>

	<myofilaments>
		<kinetic_scheme>3state_with_SRX</kinetic_scheme>
		<k_1>2</k_1>
		<k_force>1e-3</k_force>
		<k_2>200</k_2>
		<k_3>200</k_3>
		<k_4_0>500</k_4_0>
		<k_4_1>0.1</k_4_1>
		<k_cb>0.001</k_cb>
		<x_ps>5</x_ps>
		<k_on>1e8</k_on>
		<k_off>300</k_off>
		<k_coop>5</k_coop>
		<bin_min>-10</bin_min>
		<bin_max>10</bin_max>
		<bin_width>1</bin_width>
		<filament_compliance_factor>0.5</filament_compliance_factor>
		<thick_filament_length>815</thick_filament_length>
		<thin_filament_length>1120</thin_filament_length>
		<bare_zone_length>80</bare_zone_length>
		<k_falloff>0.0024</k_falloff>
		<passive_mode>exponential</passive_mode>
		<passive_exp_sigma>500</passive_exp_sigma>
		<passive_exp_L>80</passive_exp_L>
		<passive_l_slack>900</passive_l_slack>
	</myofilaments>
	
	<membranes>
		<kinetic_scheme>simple_2_compartment</kinetic_scheme>
		<Ca_content>1e-3</Ca_content>
		<k_leak>2e-3</k_leak>
		<k_act>5e-2</k_act>
		<k_serca>10.0</k_serca>
	</membranes>
</half_sarcomere>

</single_circulation_simulation>
````

### Simulation parameters

+ no_of_time_points:
  + an integer > 0, specifying the number of time-points in the simulation
+ time_step:
  + a float > 0, the time-step in s for the simulation
    + simulation time = no_of_time_points x time_step
+ activation_frequency
  + the rate (in Hz) that stimuli are applied
+ duty_ratio
  + the proportion of the stimulus cycle that stimuli are applied (note, this is a to-do item in the Project time-line)

### Output parameters

+ data_file
  + Output file (*.xlsx format) holding results of simulation
    + data goes in Data sheet
    + model xml text goes in Model sheet
+ summary_figure
  + Figure showing summary of the entire simulation
    + assumes *.png format
+ pv_figure
  + Figure showing ventricular pressure plotted against ventricular volume
    + assumes *.png format
+ flows_figure
  + Figure showing flows between different compartments
    + assumes *.png format
+ hs_fluxes_figure_figure
  + Figure showing fluxes between different MyoSim states
    + assumes *.png format

### Circulation

Entries show
+ resistance
+ compliance
of each vascular compartment

For the ventricle
+ slack_volume
  + volume in liters when passive pressure is 0

### Half-sarcomere

#### Myofilaments

The parameters depend on the kinetic scheme as follows:

+ 3state_with_SRX
  + See [Force-dependent recruitment from the myosin OFF state contributes to length-dependent activation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6084639/) for a complete description of each parameter.

#### Membranes

The parameters depend on the kinetic scheme as follows:

+ simple_2_compartment
  + this is a very simple model in which Ca<sup>2+</sup> is continually pumped into the sarcoplasmic reticulum, only to continually leak out. The rate of Ca<sup>2+</sup> release increases when the muscle is active. This model is quick to calculate but does not include molecular detail.
    + Ca_content
      + total Ca2+ concentration (M) in model
    + k_leak
      + rate (M<sup>-1</sup> s<sup>-1</sup>) for Ca<sup>2+</sup> leaking from the sarcoplasmic reticulum. (This leak is continual).
    + k_act
      + additional rate (M<sup>-1</sup> s<sup>-1</sup>) for Ca<sup>2+</sup> leaking from the sarcoplasmic reticulum when the membranes are activated.
    + k_serca
      + rate (M<sup>-1</sup> s<sup>-1</sup>) at which Ca<sup>2+</sup> is pumped back into the sarcoplasmic reticulum. This pump is always active.