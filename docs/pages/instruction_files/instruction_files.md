---
Title: Instruction File
nav_order: 4
has_children: False
---
# Instruction File
{:.no_toc}

* TOC
{:toc}
## Overview
**PyMyoVent** uses [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value).) files as the input files where an individual user can have control every single modules.

PyMyoVent's instruction files are placed at:
`path_to_PyMyoVent_repo\demo_files`


Here we explain the instruction file for [Getting Started](../demos/getting_started/getting_started.html) model.


## output_parameters

````
"output_parameters": {
    "excel_file": ["..\\temp\\getting_started\\getting_started.xlsx"],
    "csv_file": ["..\\temp\\getting_started\\getting_started.csv"],
    "input_file": ["..\\temp\\getting_started\\getting_started.json"],
    "summary_figure": ["..\\temp\\getting_started\\getting_started_summary.png"],
    "pv_figure": ["..\\temp\\getting_started\\getting_started_pv.png"],
    "baro_figure": ["..\\temp\\getting_started\\getting_started_baro.png"],
    "flows_figure": ["..\\temp\\getting_started\\getting_started_flows.png"],
    "hs_fluxes_figure": ["..\\temp\\getting_started\\getting_started_hs_fluxes.png"],
    "multi_threading":["..\\temp\\getting_started\\getting_started_multi_thread.png"]
  },
````
- `"output_parameters":` This block contains the output directory path for output figures.
    - `"excel_file":` Directory path for the output data spread sheet in .xlsx format.
    - `"csv_file":`  Directory path for the output data spread sheet in .csv format.
    - `"input_file":` Directory path for making a copy of input instruction file.
    - `"summary_figure":` Directory path for the simulation summary figure.
    - `"pv_figure":` Directory path for the pressure-volume loop figure.
    - `"baro_figure":` Directory path for the baroreceptor module's results figure.
    - `"flows_figure":` Directory path for the blood flow circulation figure.
    - `"hs_fluxes_figure":` Directory path for MyoSim fluxes figure.
    - `"multi_threading":` Directory path for multi threading simulation output figure.

## baroreflex

````
"baroreflex": {
    "baro_scheme": ["simple_baroreceptor"],
},
````
- `"baroreflex":` This block controls how the simulation runs.
    - `"baro_scheme":` It governs what type of simulation should be used. 
        - So far there are two types of simulation:
            1. `fixed_heart_rate`
            2. `simple_baroreceptor`

````
"fixed_heart_rate":{
      "simulation":{
        "no_of_time_points": [10000],
        "time_step": [0.001],
        "duty_ratio": [0.3],
        "basal_heart_period": [1,"s"]
      }
    },
````
- `"fixed_heart_rate":` This enforces the simulation to be run with a constat heart rate. 
    - `"simulation":` This block contains the simulation's parameters for `"fixed_heart_rate"`.
        - `"no_of_time_points":` Number of time steps the simulation need to be run.
        - `"time_step":` The resolution of simulation.
        - `"duty_ratio":` The fraction of one period of cycle that the action potential is activated. 
        - `"basal_heart_period":` The period of the beating heart.

````
"simple_baroreceptor":{
      "simulation":{
        "start_index":[2000],
        "memory":[2,"s"],
        "no_of_time_points": [150000],
        "time_step": [0.001],
        "duty_ratio": [0.003],
        "basal_heart_period": [1,"s"]
      },
      "afferent": {
        "b_max": [2],
        "b_min": [0],
        "S": [0.067,"mmHg"],
        "P_n": [90,"mmHg"]
      },
      "regulation":{
        "heart_period":{
          "G_T": [0.03]
        },
        "k_1":{
          "G_k1": [-0.05]
        },
        "k_on":{
          "G_k_on":[0.02]
        },
        "ca_uptake":{
          "G_up": [-0.02]
        },
        "g_cal":{
          "G_gcal": [-0.03]
        }
      }
    }
````
- `"simple_baroreceptor":` This enforces the simulation to be run while having the baroreceptor module activated.
    - `"simulation":` This block contains the simulation's parameters for the `"simple_baroreceptor"`.
        - `"start_index":` The start index for activating of the `"simple_baroreceptor"`.
        - `"memory":` The memory in seconds in which the rate of controlled parameters become averged over. 
        - `"no_of_time_points":` Number of time steps the simulation need to be run.
        - `"time_step":` The resolution of simulation.
        - `"duty_ratio":` The fraction of one period of cycle that the action potential is activated. 
        - `"basal_heart_period":` The basal value for the period of the beating heart.
    - `"afferent":` This block contains the parameters for the afferent pathway of the baroreceptor module.
        - `"b_max":` The maximum threshold baroreceptor output signal
        - `"b_min":` The minimum threshold baroreceptor output signal
        - `"S":` The sensitivity constant factor of the baroreceptor output signal in response to any change in the arterial pressure from the mean arterial pressure. 
        - `"P_n":` The targeted mean arterial pressure (i.e. set-point level).
    - `"regulation":` This block contains the parameters for the regulation of controlled parameteres.
        - `"heart_period":` The heart period block.
            - `"G_T":` The gain factor for the heart period.
        - `"k_1":` The *k_1* constant factor block.
            - `"G_k1":` The gain factor for the *k_1* factor of MyoSim module.
        - `"k_on":` The *k_on* constant factor block.
            - `"G_k_on":` The gain factor for the *k_on* factor of MyoSim module.
        - `"ca_uptake":` The maximal *SERCA_uptake* current block.
            - `"G_up":` The gain factor for the maximal *SERCA_uptake* current.
        - `"G_cal":` The maximal *Ca_current* through the L-type channel.
            - `"G_gcal":` The gain factor for the maximal *Ca_current* through the L-type channel.

## perturbations

````
"perturbations": {
    "perturbation_activation":[false],
````
- `"perturbations":` This block controls different types of perturbation to the simulation. 
    - `"perturbation_activation":` The activation switch control for the perturbation class. 

````
"volume":{
      "start_index": [],
      "stop_index": [],
      "increment": [0]
    },
````
- `"volume":` The blood volume perturbation block through the venous compartment.
    - `"start_index":` The start index for the blood volume perturbation. 
    - `"stop_index":` The stop index for the blood volume perturbation. 
    - `"increment":` The incremental magnitude of change in the blood volume. 

````
"valve":{
      "aortic":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "mitral":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      }
    },
````
- `"valve":` The valvular regurgitation block.
    - `"aortic":` The aortic valve regurgitaion block.
        - `"start_index":` The start index for the aortic valve regurgitation perturbation. 
        - `"stop_index":` The stop index for the aortic valve regurgitation perturbation. 
        - `"increment":` The incremental magnitude of change in the aortic valve regurgitation.
    - `"mitral":` The mitral valve regurgitaion block.
        - `"start_index":` The start index for the mitral valve regurgitation perturbation. 
        - `"stop_index":` The stop index for the mitral valve regurgitation perturbation. 
        - `"increment":` The incremental magnitude of change in the mitral valve regurgitation . 

````
"compliance": {
      "aorta":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "capillaries": {
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "venous":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      }
    },
````
- `"compliance":` The compliance factor perturbation block.
    - `"aorta":` The aortic compliance factor perturbation block.
        - `"start_index":` The start index for the aortic compliance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the aortic compliance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the aortic compliance factor perturbation.
    - `"capillaries":` The capillaries compliance factor perturbation block.
        - `"start_index":` The start index for the capillaries compliance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the capillaries compliance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the capillaries compliance factor perturbation.
    - `"venous":` The venous compliance factor perturbation block.
        - `"start_index":` The start index for the venous compliance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the venous compliance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the venous compliance factor perturbation.

````
"resistance": {
      "aorta":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "capillaries": {
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "venous":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "ventricle":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      }
},
````
- `"resistance":` The resistance factor perturbation block.
    - `"aorta":` The aortic resistance factor perturbation block.
        - `"start_index":` The start index for the aortic resistance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the aortic resistance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the aortic resistance factor perturbation.
     - `"capillaries":` The capillaries resistance factor perturbation block.
        - `"start_index":` The start index for the capillaries resistance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the capillaries resistance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the capillaries resistance factor perturbation.
    - `"venous":` The venous resistance factor perturbation block.
        - `"start_index":` The start index for the venous resistance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the venous resistance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the venous resistance factor perturbation.
    - `"ventricle":` The ventricular resistance factor perturbation block.
        - `"start_index":` The start index for the ventricular resistance factor perturbation perturbation. 
        - `"stop_index":` The stop index for the ventricular resistance factor perturbation perturbation. 
        - `"increment":` The incremental magnitude of change in the ventricular resistance factor perturbation.

````
"myosim":{
      "k_1":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "k_2":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "k_4_0":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      }
    },
````
- `"myosim":` The MyoSim parameters perturbation block.
    - `"k_1":` The `k_1` factor perturbation block.
        - `"start_index":`  The start index for `k_1` factor perturbation.
        - `"stop_index":` The stop index for `k_1` factor perturbation.
        - `"increment":` The incremental magnitude of change in `k_1` factor perturbation.
    - `"k_2":` The `k_2` factor perturbation block.
        - `"start_index":`  The start index for `k_2` factor perturbation.
        - `"stop_index":` The stop index for `k_2` factor perturbation.
        - `"increment":` The incremental magnitude of change in `k_2` factor perturbation.
    - `"k_4_0":` The `k_4_0` factor perturbation block.
        - `"start_index":`  The start index for `k_4_0` factor perturbation.
        - `"stop_index":` The stop index for `k_4_0` factor perturbation.
        - `"increment":` The incremental magnitude of change in `k_4_0` factor perturbation.

````
"ca_handling":{
      "ca_uptake":{
        "start_index": [40000],
        "stop_index": [41000],
        "increment": [0]
      },
      "ca_leak":{
        "start_index": [40000],
        "stop_index": [41000],
        "increment": [0]
      },
      "g_cal":{
        "start_index": [40000],
        "stop_index": [41000],
        "increment": [0]
      }
    }
````

- `"ca_handling":` The calcium handling parameters perturbation block.
    - `"ca_uptake":` The maximal SERCA uptake current perturbation block.
        - `"start_index":`  The start index for the maximal SERCA uptake current perturbation.
        - `"stop_index":` The stop index for the maximal SERCA uptake current perturbation.
        - `"increment":` The incremental magnitude of change in the maximal SERCA uptake current perturbation.
    - `"ca_leak":` The maximal SR leak current perturbation block.
        - `"start_index":`  The start index for the maximal SR leak current perturbation.
        - `"stop_index":` The stop index for the maximal SR leak current perturbation.
        - `"increment":` The incremental magnitude of change in the maximal maximal SR leak current perturbation.
    - `"g_cal":` The maximal L-type calcium current perturbation block.
        - `"start_index":`  The start index for the maximal L-type calcium current perturbation.
        - `"stop_index":` The stop index for the maximal L-type calcium current perturbation.
        - `"increment":` The incremental magnitude of change in the maximal maximal L-type calcium current perturbation.

## circulation

````
"circulation":{
    "no_of_compartments": [6],
    "blood":{
      "volume":[5,"liters"]
    },
````
- `"circulation":` The circulation module block.
    - `"no_of_compartments":` Number of compartments used in the circulatory module.
    - `"blood":` The blood's related parameters.
        - `"volume":` The total blood volume circulating in the siumulation.

````
"aorta":{
      "resistance": [40,"s"],
      "compliance": [0.0005,"liter_per_mmHg"]
    },
````
- `"aorta":` The aortic circulatory parameters block.
    - `"resistance":` The resistance factor for the aorta compartment.
    - `"compliance":` The compliance factor for the aorta compartment.

````
"arteries":{
      "resistance": [20,"s"],
      "compliance": [0.0011,"liter_per_mmHg"]
},
````
- `"arteries":` The arteries circulatory parameters block.
    - `"resistance":` The resistance factor for the arteries compartment.
    - `"compliance":` The compliance factor for the arteries compartment.

````
"arterioles":{
      "resistance": [520,"s"],
      "compliance": [0.005,"liter_per_mmHg"]
    },
````
- `"arterioles":` The arterioles circulatory parameters block.
    - `"resistance":` The resistance factor for the arterioles compartment.
    - `"compliance":` The compliance factor for the arterioles compartment.

````
"capillaries":{
      "resistance": [310,"s"],
      "compliance": [0.03,"liter_per_mmHg"]
    },
````
- `"capillaries":` The capillaries circulatory parameters block.
    - `"resistance":` The resistance factor for the capillaries compartment.
    - `"compliance":` The compliance factor for the capillaries compartment.

````
"veins":{
      "resistance": [300,"s"],
      "compliance": [0.5,"liter_per_mmHg"]
    },
````
- `"veins":` The venous circulatory parameters block.
    - `"resistance":` The resistance factor for the veins compartment.
    - `"compliance":` The compliance factor for the veins compartment.

````
"ventricle":{
      "resistance": [10,"s"],
      "wall_volume": [0.1,"liters"],
      "slack_volume": [0.08,"liters"],
      "wall_density": [1055,"g/l"],
      "body_surface_area": [1.90,"m^2"]
    }
````
- `"ventricle":` The ventricular circulatory parameters block.
    - `"resistance":` The resistance factor for the ventricle compartment.
    - `"wall_volume":` The mayocardial volume for the ventricular wall.
    - `"slack_volume":` The slack ventricular volume.
    - `"wall_density":` The density of myocardial wall.
    - `"body_surface_area": `The body surface area of the patient.


## half_sarcomere

````
"half_sarcomere":{
    "max_rate": [5000,"s^-1"],
    "temperature": [288, "Kelvin"],
    "cb_number_density": [6.9e16, "number of cb's/m^2"],
    "initial_hs_length": [900, "nm"],
    "ATPase_activation":[false],
    "delta_energy":[70,"kJ/mol"],
    "avagadro_number":[6.02e23,"mol^-1"],
    "reference_hs_length":[1100,"nm"],
````
- `"half_sarcomere":` MyoSim parameters block.
    - `"max_rate":` A float defining the maximum rate considered in the simulations. Rate values above this will be limited to max_rate.
    - `"temperature":` The tempreture.
    - `"cb_number_density":` The density of myosin heads (Number of myosin heads in a unit cross-section area of half-sarcomeres). 
    - `"initial_hs_length":` Initial length for the half-sarcomeres.
    - `"ATPase_activation":` Switch control for ATPase calculation.
    - `"delta_energy":` The amount of energy become released during myosin ATPase.
    - `"avagadro_number":` Avagadro number.
    - `"reference_hs_length":` The reference length for calculating of ATPase.

````
"myofilaments":{
      "kinetic_scheme": ["3state_with_SRX"],
      "k_1": [1.75,"s^-1"],
      "k_force": [1e-3, "(N^-1)(m^2)"],
      "k_2": [200, "s^-1"],
      "k_3": [100, "(nm^-1)(s^-1)"],
      "k_4_0": [200, "s^-1"],
      "k_4_1": [0.5, "nm^-4"],
      "k_cb": [0.001, "N*m^-1"],
      "x_ps": [5, "nm"],
      "k_on": [1e8, "(M^-1)(s^-1)"],
      "k_off": [200, "s^-1"],
      "k_coop": [5],
      "bin_min": [-10, "nm"],
      "bin_max": [10, "nm"],
      "bin_width": [1, "nm"],
      "filament_compliance_factor": [0.5],
      "thick_filament_length": [815, "nm"],
      "thin_filament_length": [1120, "nm"],
      "bare_zone_length": [80, "nm"],
      "k_falloff": [0.0024],
      "passive_mode": ["exponential"],
      "passive_exp_sigma": [500],
      "passive_exp_L": [80],
      "passive_l_slack": [900, "nm"]
    },
````
- `"myofilaments":` The myofilament parameters block. 
    - `"kinetic_scheme":` The switch control for the kinetic's type of half-sarcomeres. 
    - `"k_1":` The avtivation constant rate of myosin heads from OFF state to ON state. 
    - `"k_force":` The force dependency constant factor of myosin heads during activation.
    - `"k_2":` The deactivation constant rate myosin heads from ON state to OFF state.
    - `"k_3":` The attachment constant rate of myosin heads to the activated binding sites.
    - `"k_4_0":` The detachment constant rate of myosin heads from the activated binding sites.
    - `"k_4_1":` The strain dependency constant factor of myosin heads during detachment.
    - `"k_cb":` The cross-bridge stiffness factor.
    - `"x_ps":` The power stroke of an attached cross-bridge.
    - `"k_on":` The activation constant rate of binding sites.
    - `"k_off":` The deactivation constant rate of binding sites. 
    - `"k_coop":` The cooperativity factor of thin filaments. 
    - `"bin_min":` The minimum possible value of x in nm for the cross-bridge distribution 
    - `"bin_max":` The maximum possible value of x in nm for the cross-bridge distribution 
    - `"bin_width":` The width of bins in the cross-bridge distribution. Smaller values of bin_width give cross-bridge distributions with finer resolution but take longer to calculate
    - `"filament_compliance_factor":` The compliance factor of myofilaments. 

    The following parameters are used to calculate the overlap of the thick and thin filaments, and thus the number of myosin heads that are able to interact with actin 
    - `"thick_filament_length":` The length of thick myofilament in nm.
    - `"thin_filament_length":` The length of thin myofilament in nm.
    - `"bare_zone_length":` The length of bare zone in 
    - `"k_falloff":` A constant factor.
    - `"passive_mode":` The mode type for calculating the passive force in half-sarcomeres. 

    The following parameters are used for `passive_mode` of `exponential`
    - `"passive_exp_sigma":` The sigma constant factor.
    - `"passive_exp_L":` The constant factor that sets the curvature of the relationship.
    - `"passive_l_slack":` Slack length of half-sarcomere.

````
"membranes": {
      "kinetic_scheme": ["simple_2_compartment"],
  }
````
- `"membranes":` This block governs the parameters for an implemented electrophysiology model.
    - `"kinetic_scheme":` The modle's name for the electrophysiology model that play's a "switch control" role in the "membrane" class.
      ````
      "simple_2_compartment":{
        "Ca_content": [1e-3],
        "k_leak": [2e-3],
        "k_act": [5e-2],
        "k_serca": [10.0]
      },
      ````
      - `"simple_2_compartment":` The parameters block for the "simple two compartment" electrophysiology model.
        - `"Ca_content":` Amount of calcium content in the sarcoplasmic reticulum (SR).
        - `"k_leak":` Rate constant factor for calcium leak current from SR.
        - `"k_act":` Rate constant factor for active calcium current from SR during stimulation.
        - `"k_serca":` Rate constant factor SERCA uptake current.
      ````
      "Ten_Tusscher_2004":{
        "g_to_factor": [1],
        "g_Kr_factor": [1],
        "g_Ks_factor": [1],
        "Ca_a_rel_factor": [1],
        "Ca_V_leak_factor": [1],
        "Ca_Vmax_up_factor": [1],
        "g_CaL_factor": [1]
      }
      ````
      - `"Ten_Tusscher_2004":` The parameters' multiplier block for the "ten Tusscher" electrophysiology model.
        - The [ten Tusscher](http://models.physiomeproject.org/exposure/c7f7ced1e002d9f0af1b56b15a873736/tentusscher_noble_noble_panfilov_2004_a.cellml/view) electrophysiology model is a sophisticated model that include a large number of constant factors and state conditions. In this block, only some parameter multiplier can be modifed in order to do something like a sensitivity test on the included parameters. 
      
## growth

````
"growth": {
    "growth_activation": [false],
    "start_index": [200000],
    "moving_average_window": [5000],
    "driven_signal": ["stress"],
  },
````
- `"growth":` This block belngs to the "ventricular growth" class parameters.
  - `"growth_activation":` The activation control parameter for the "growth" module.
  - `"start_index":` The start index for activating the growth module.
  - `"moving_average_window":` The The number of time steps that the growth rates needs to be averaged over.
  - `"driven_signal":` A switch control based on the driving signal for the "growth" module.

  ````
  "concenrtric":{
      "G_stress_driven":[1e-6],
      "G_ATPase_driven":[-2]
    },
  ````
  - `"concenrtric":` The parameters block for "concentric" growth pattern.
    - `"G_stress_driven":` The gain factor for stress driven "concentric" growth pattern.
    - `"G_ATPase_driven":` The gain factor for ATPase driven "concentric" growth pattern.
  
  ````
  "eccentric":{
      "G_number_of_hs":[-3e-6],
      "G_ATPase_driven":[0]
    }
  ````
  - `"eccenrtric":` The parameters block for "eccentric" growth pattern.
    - `"G_stress_driven":` The gain factor for stress driven "eccentric" growth pattern.
    - `"G_ATPase_driven":` The gain factor for ATPase driven "eccentric" growth pattern.

## profiling

````
"profiling":{
    "profiling_activation":[false]
````
- `"profiling":` The profiling block.
  - `"profiling_activation":` The activation control parameter for profiling the simulation. 

## saving_to_spreadsheet

````
"saving_to_spreadsheet":{
    "saving_data_activation":[false],
    "output_data_format":["csv"],
    "start_index":[0],
    "stop_index":[15000]
  },
````
- `"saving_to_spreadsheet":` This block controls dumping output data.
  - `"saving_data_activation":` The activation control parameter for dumping output data.
  - `"output_data_format":` The output dumped data format. This can varies between "csv" and "xlsx" formats.
  - `"start_index":` The start index for dumping data to the output spread sheet.
  - `"stop_index":` The stop index for dumping data to the output spread sheet.

