---
Title: Growth Aortic Stenosis (pressure overload)
nav_order: 2
has_children: False
parent: Growth
grand_parent : Demos
---
# Growth Aortic Stenosis (pressure overload)
{:.no_toc}

* TOC
{:toc}


## Instruction

* Lunch [Anaconda](http://anaconda.org) prompt.

* Navigate to **Python_code** folder in PyMyoVent's repository directory:
    * `$ cd path_to_PyMyoVent_repo\Python_code`

* Use the following command to run the `growth_AS` demo with no perturbation in ventricular loading applied to the system.
    * `$ python PyMyoVent.py run_defined_model ..\demo_files\growth_AS\growth_AS_model.json`
    * After around one and half an hour, the simulation would be finished.


## Note

* The baroreceptor module starts to regulate the arterial pressure at `"start_index":[5000]`, which can be modified by the user.  

* The baroreceptor module tries to maintain the mean arterial pressure at `87.7 mm Hg`, as a normal level for healthy human, by regulating heart rate, myofilaments contractility, intracellular Ca handling, and vascular tone.

* This model uses an electrophysiology model proposed by [ten Tusscher](http://models.physiomeproject.org/exposure/c7f7ced1e002d9f0af1b56b15a873736/tentusscher_noble_noble_panfilov_2004_a.cellml/view).

* The ventricular loading is perturbed to simulate the aortic stenosis condition.

* The growth module is set to be activated at `"start_index": [150000]`, and is able to capture any sort of ventricular growth. But in response to pressure overload condition (aortic stenosis), the ventricular wall thickness increases more than chamber dilation and hence concentric growth happens.

## Instruction file

````
{
  "output_parameters": {
    "input_file": ["..\\temp\\growth_AS\\growth_AS.json"],
    "csv_file": ["..\\temp\\growth_AS\\growth_AS.csv"],
    "summary_figure": ["..\\temp\\growth_AS\\growth_AS_summary.png"],
    "pv_figure": ["..\\temp\\growth_AS\\growth_AS_pv.png"],
    "flows_figure": ["..\\temp\\growth_AS\\growth_AS_flows.png"],
    "hs_fluxes_figure": ["..\\temp\\growth_AS\\growth_AS_hs_fluxes.png"],
    "baro_figure": ["..\\temp\\growth_AS\\growth_AS_baro.png"],
    "circulatory": ["..\\temp\\growth_AS\\growth_AS_arterial.png"],
    "growth_figure": ["..\\temp\\growth_AS\\growth_AS_growth.png"],
    "growth_summary": ["..\\temp\\growth_AS\\growth_AS_growth_sum.png"]
  },

  "system_control":{
    "simulation":{
      "no_of_time_points": [1500000],
      "time_step": [0.001],
      "duty_ratio": [0.003],
      "basal_heart_period": [0.857,"s"]
    },
    "baroreceptor":{
      "start_index":[50000],
      "N_t":[5000],
      "afferent": {
        "b_max": [2],
        "b_min": [0],
        "S": [0.067,"mmHg"],
        "P_set": [87.7,"mmHg"]
      },
      "efferent":{
        "heart_period":{
          "G_T": [0.07]
        },
        "k_1":{
          "G_k1": [-0.1]
        },
        "k_on":{
          "G_k_on":[0.08]
        },
        "ca_uptake":{
          "G_up": [-0.05]
        },
        "g_cal":{
          "G_gcal": [-0.07]
        },
        "c_venous":{
          "G_c_venous": [0.1]
        },
        "r_arteriolar":{
          "G_r_arteriolar": [-0.1]
        }
      }
    }
  },
  "perturbations": {
    "perturbation_activation":[true],
    "volume":{
      "start_index": [150000],
      "stop_index": [160000],
      "increment": [0]
    },
    "valve":{
      "aortic":{
        "start_index": [0],
        "stop_index": [505000],
        "increment": [0.0]
      },
      "mitral":{
        "start_index": [500000],
        "stop_index": [1000000],
        "increment": [0.0]
      }
    },
    "compliance": {
      "aorta":{
        "start_index": [200000],
        "stop_index": [205000],
        "increment": [0]
      },
      "capillaries": {
        "start_index": [200000],
        "stop_index": [205000],
        "increment": [0]
      },
      "venous":{
        "start_index": [500000],
        "stop_index": [505000],
        "increment": [0]
      }
    },
    "resistance": {
      "aorta":{
        "start_index": [450000],
        "stop_index": [460000],
        "increment": [0.012]
      },
      "capillaries": {
        "start_index": [500000],
        "stop_index": [505000],
        "increment": [0]
      },
      "venous":{
        "start_index": [80000],
        "stop_index": [85000],
        "increment": [0.0]
      },
      "ventricle":{
        "start_index": [500000],
        "stop_index": [505000],
        "increment": [0]
      }
    },
    "myosim":{
      "k_1":{
        "start_index": [25000],
        "stop_index": [25001],
        "increment": [0]
      },
      "k_2":{
        "start_index": [25000],
        "stop_index": [35000],
        "increment": [0.0]
      },
      "k_4_0":{
        "start_index": [200000],
        "stop_index": [210000],
        "increment": [0]
      }
    },
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
  },
  "circulation":{
    "no_of_compartments": [6],
    "blood":{
      "volume":[5,"liters"]
    },
    "aorta":{
      "resistance": [40,"s"],
      "compliance": [0.0004,"liter_per_mmHg"]
    },
    "arteries":{
      "resistance": [80,"s"],
      "compliance": [0.0009,"liter_per_mmHg"]
    },
    "arterioles":{
      "resistance": [400,"s"],
      "compliance": [0.005,"liter_per_mmHg"]
    },
    "capillaries":{
      "resistance": [340,"s"],
      "compliance": [0.03,"liter_per_mmHg"]
    },
    "veins":{
      "resistance": [330,"s"],
      "compliance": [0.5,"liter_per_mmHg"]
    },
    "ventricle":{
      "resistance": [10,"s"],
      "wall_volume": [0.1,"liters"],
      "slack_volume": [0.08,"liters"],
      "wall_density": [1055,"g/l"],
      "body_surface_area": [1.90,"m^2"]
    }
  },
  "half_sarcomere":{
    "max_rate": [5000,"s^-1"],
    "temperature": [288, "Kelvin"],
    "cb_number_density": [6.9e16, "number of cb's/m^2"],
    "initial_hs_length": [900, "nm"],
    "ATPase_activation":[false],
    "delta_energy":[70,"kJ/mol"],
    "avagadro_number":[6.02e23,"mol^-1"],
    "reference_hs_length":[1100,"nm"],

    "myofilaments":{
      "kinetic_scheme": ["3state_with_SRX"],
      "k_1": [2,"s^-1"],
      "k_force": [0.6e-3, "(N^-1)(m^2)"],
      "k_2": [200, "s^-1"],
      "k_3": [100, "(nm^-1)(s^-1)"],
      "k_4_0": [200, "s^-1"],
      "k_4_1": [0.3, "nm^-4"],
      "k_cb": [0.001, "N*m^-1"],
      "x_ps": [5, "nm"],
      "k_on": [5e8, "(M^-1)(s^-1)"],
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
      "passive_exp_sigma": [300],
      "passive_exp_L": [80],
      "passive_l_slack": [900, "nm"]
    },
    "membranes": {
      "kinetic_scheme": ["Ten_Tusscher_2004"],
      "simple_2_compartment":{
        "Ca_content": [1e-3],
        "k_leak": [2e-3],
        "k_act": [5e-2],
        "k_serca": [10.0]
      },
      "Ten_Tusscher_2004":{
        "g_to_factor": [1],
        "g_Kr_factor": [1],
        "g_Ks_factor": [1],
        "Ca_a_rel_factor": [1],
        "Ca_V_leak_factor": [1],
        "Ca_Vmax_up_factor": [1],
        "g_CaL_factor": [1]
    }
  }
},
  "growth": {
    "start_index": [150000],
    "moving_average_window": [10000],
    "driven_signal": ["stress"],
    "concenrtric":{
      "G_stress_driven":[10e-6],
      "G_ATPase_driven":[1]
    },
    "eccentric":{
      "G_number_of_hs":[-5e-6],
      "G_ATPase_driven":[-2]
    }
  },
  "profiling":{
    "profiling_activation":[false]
  },
  "saving_to_spreadsheet":{
    "saving_data_activation":[false],
    "output_data_format":["csv"],
    "start_index":[0],
    "stop_index":[2000000]
  }
}
````

## Outputs
