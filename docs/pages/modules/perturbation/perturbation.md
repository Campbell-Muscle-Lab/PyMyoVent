---
Title: Perturbation
nav_order: 6
has_children: False
parent: Modules

---
# Perturbation
{:.no_toc}

* Toc 
{:toc}

## Overview

This module is developed to control different types of perturbation and the way they are being applied to a simulation.

## Theory

- The **Perturbation** module can perturb a simulation from molecular level (e.g. the attachment rate constant of myosin heads to the binding sites in actin, *k_3*) to the organ level (e.g. blood volume perturbation and hemorrhage condition).

- Each type of perturbation is defined with three parameters:
    1. `start_index`: Starting time index for the perturbation to be applied.
    2. `stop_index`: Stopping time index for the perturbation to be applied.
    3. `increment`: The inceremental value to be added at each time step during perturbation time.

### Parameters

````
"perturbations": {
    "perturbation_activation":[false],
    "volume":{
      "start_index": [],
      "stop_index": [],
      "increment": [0]
    },
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
    "ca_handling":{
      "ca_uptake":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "ca_leak":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      },
      "g_cal":{
        "start_index": [],
        "stop_index": [],
        "increment": [0]
      }
    }
  },
````