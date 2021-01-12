---
Title: Protocol
nav_order: 2
has_children: False
parent: Structures
---
# Protocol
{:.no_toc}

* TOC
{:toc}


## Protocol

- Protocol file handles how a simulation runs. In the simplest way, the user needs to define the number of time steps, `no_of_time_steps`, and the resolution of simulation, `time_step`. Additionally, an individual user can define different types of perturbation (e.g. blood volume perturbation), or activation time slots for supplementary modules like `baroreflex` and/or `growth`.

- For example, the following protocol file enforces a simulation of 100 seconds with `no_of_time_steps: 10000` and `time_step: 0.001`. Furthermore, this file contains a perturbation block that implies a perturbation of blood volume from starting time of `t_start_s: 25` up to `t_stop_s: 30` with `total_change: 1` liter.

- The `baroreflex` block in this file accounts for activation time slot for the baroreflex module. An individual user can change the protocol file according to his/her research protocol.

````
{
    "protocol":{
        "no_of_time_steps": 100000,
        "time_step": 0.001
    },
    "perturbations":
    {
        "perturbation":
        [
            {
                "variable": "blood_volume",
                "t_start_s": 25,
                "t_stop_s": 30,
                "total_change": 1
            }
        ]
    },
    "baroreflex":
    {
        "activations":
        [
            {
                "t_start_s": 10,
                "t_stop_s": 100
            }
        ]
    }
}
````
