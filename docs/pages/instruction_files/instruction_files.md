---
Title: Instruction File
nav_order: 3
has_children: False
---
## Instruction File
{:.no_toc}

* TOC
{:toc}
## Overview
**PyMyoVent** uses [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value).) files as the input files where an individual user can have control every single modules.

PyMyoVent's instruction files are placed at:
`path_to_PyMyoVent_repo\demo_files`


Here we explain the instruction file for [Getting Started](../pages/models/getting_started/getting_started.html) model.


## output_parameters

````
"output_parameters": {
    "excel_file": ["..\\temp\\baroreceptor\\baroreceptor.xlsx"],
    "input_file": ["..\\temp\\baroreceptor\\baroreceptor.json"],
    "summary_figure": ["..\\temp\\baroreceptor\\baroreceptor_summary.png"],
    "force_length": ["..\\temp\\baroreceptor\\baroreceptor_F_L.png"],
    "pv_figure": ["..\\temp\\baroreceptor\\baroreceptor_pv.png"],
    "baro_figure": ["..\\temp\\baroreceptor\\baroreceptor_baro.png"],
    "flows_figure": ["..\\temp\\baroreceptor\\baroreceptor_flows.png"],
    "hs_fluxes_figure": ["..\\temp\\baroreceptor\\baroreceptor_hs_fluxes.png"],
    "multi_threading":["..\\temp\\baroreceptor\\baroreceptor_multi_thread.png"]
  },
````
- `"output_parameters":` This block contains the output directory path for output figures.
    - `"excel_file":` Output directory path for the spread sheet including all data.
    - `"input_file":` Output directory path for making a copy of input instruction file.
    - `"summary_figure":` Output directory path for the simulation summary figure.
    - `"pv_figure":` Output directory path for the pressure-volume loop figure.
    - `"baro_figure":` Output directory path for the baroreceptor module's results figure.
    - `"flows_figure":` Output directory path for the blood flow circulation figure.
    - `"hs_fluxes_figure":` Output directory path for MyoSim fluxes figure.
    - `"multi_threading":` Output directory path for multi threading simulation output figure.

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
        "br_max": [2],
        "br_min": [0],
        "S": [15,"mmHg"],
        "P_n": [90,"mmHg"]
      },
      "regulation":{
        "heart_period":{
          "G_T": [0.03]
        },
        "k_1":{
          "G_k1": [-0.03]
        },
        "k_3":{
          "G_k3": [-0.03]
        },
        "ca_uptake":{
          "G_up": [-0.02]
        },
        "G_cal":{
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
        - `"br_max":` The maximum baroreceptor output signal
        - `"br_min":` The minimum baroreceptor output signal
        - `"S":` The sensitivity constant factor of the baroreceptor output signal in response to any change in the arterial pressure from the mean arterial pressure. 
        - `"P_n":` The targeted mean arterial pressure.
    - `"regulation":` This block contains the parameters for the regulation of controlled parameteres.
        - `"heart_period":` The heart period block.
            - `"G_T":` The gain factor for the heart period.
        - `"k_1":` The *k_1* constant factor block.
            - `"G_k1":` The gain factor for the *k_1* factor of MyoSim module.
        - `"k_3":` The *k_3* constant factor block.
            - `"G_k3":` The gain factor for the *k_3* factor of MyoSim module.
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
    - `"max_rate":` The maximum constant rate for the MyoSim fluxes. 
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
    - `"bin_min":` The minimum range of length in which a myosin head can be placed with respect to its resting position. 
    - `"bin_max":` The maximum range of length in which a myosin head can be placed with respect to its resting position. 
    - `"bin_width":` The resolution of myosin head's position range. 
    - `"filament_compliance_factor":` The compliance factor of myofilaments. 
    - `"thick_filament_length":` 
    - `"thin_filament_length":` 
    - `"bare_zone_length":` 
    - `"k_falloff":` 
    - `"passive_mode":` 
    - `"passive_exp_sigma":` 
    - `"passive_exp_L":` 
    - `"passive_l_slack":` 
    
## growth

## profiling

## saving_to_spreadsheet

## multi_threads