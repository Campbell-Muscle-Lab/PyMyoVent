---
Title: Model
nav_order: 1
has_children: False
parent: Structures
---
# Model
{:.no_toc}

* TOC
{:toc}


- Model file contains the model parameters that are essential for each module. These parameters can either change (due to applied perturbation) or be constant throughout a simulation.

- The three essential block structures for each simulation are `circulation`, `heart_rate`, and `half_sarcomere`. So all model files **SHOULD** include these block structures. Other supplementary block structures like `baroreflex`, or `growth` are optional and can be added or removed based on the purpose of the simulation.

- The following is an example of `model_file.json` including only the three main blocks. The user can change the parameter values optionally.
- The parameters for each block are explained in the following of this page.

````
{
    "circulation":{
        "blood_volume": 3.65,
        "compartments":
        [
            {
                "name": "aorta",
                "resistance": 40,
                "compliance": 5e-4
            },
            {
                "name": "arteries",
                "resistance": 40,
                "compliance": 5e-4
            },
            {
                "name": "arterioles",
                "resistance": 800,
                "compliance": 1e-4
            },
            {
                "name": "capillaries",
                "resistance": 200,
                "compliance": 2e-4
            },
            {
                "name": "venules",
                "resistance": 30,
                "compliance": 0.05
            },
            {
                "name": "veins",
                "resistance": 30,
                "compliance": 0.3
            },
            {
                "name": "ventricle",
                "resistance": 20,
                "wall_volume": 0.1,
                "slack_volume": 0.03,
                "wall_density": 1055
            }
        ]
    },
    "heart_rate": {
        "t_active_period": 0.003,
        "t_quiescent_period": 0.854,
        "t_first_activation": 0.1
    },
    "half_sarcomere":{
        "initial_hs_length": 900,
        "reference_hs_length": 1100,
        "membranes": {
            "Ca_content": 1e-3,
            "k_leak": 5e-4,
            "k_act": 1.5e-2,
            "k_serca": 10.0,
            "t_open": 0.1,
            "implementation":{
                "kinetic_scheme": "simple_2_compartment"
            }
        },
        "myofilaments":{
            "cb_number_density": 6.9e16,
            "k_1": 2,
            "k_force": 1e-3,
            "k_2": 200,
            "k_3": 100,
            "k_4_0": 150,
            "k_4_1": 0.1,
            "k_cb": 0.001,
            "x_ps": 5,
            "k_on": 2e8,
            "k_off": 200,
            "k_coop": 5,
            "passive_exp_sigma": 200,
            "passive_exp_L": 70,
            "passive_l_slack": 900,
            "implementation":
            {
                "kinetic_scheme": "3_state_with_SRX",
                "passive_mode": "exponential",
                "max_rate": 5000,
                "temperature": 310,
                "bin_min": -10,
                "bin_max": 10,
                "bin_width": 1,
                "filament_compliance_factor": 0.5,
                "thick_filament_length": 815,
                "thin_filament_length": 1120,
                "bare_zone_length": 80
            }
        }
    }
}
````

## circulation

This block contains the model parameters for the systemic circulation module.

- `blood_volume` : Total blood volume in the systemic circulatory system in liters.
- `compartments` : List of included compartments with their relative `resistance` and `compliance` factors.
- Note: For `ventricle` compartment, user needs to define `wall_volume` in liters, ventricle `slack_volume` in liters, and `wall_density` in g/liters.

## heart_rate

This block contains the required parameters for calculating the heart rate.

- `t_active_period` : Duration of activation pulse in seconds.
- `t_quiescent_period` : Duration of non-activated phase of a cardiac cycle in seconds.
- `t_first_activation` : Activating time of the initiative pulse in seconds.

## half_sarcomere

This block contains model parameters for MyoSim model of contraction.

- `initial_hs_length` : Initial length of a half-sarcomere embedded in the circumference of the ventricle. .
- `reference_hs_length` : Reference length of a half-sarcomere.
- `membranes` : This sub-block contains model parameters for model of the membrane electrophysiology.
    -  `Ca_content` : Total Ca content in the myocardial cell.
    -  `k_leak` : Rate factor of Ca leak current from Sarcoplasmic Reticulum.
    -  `k_act` : Rate factor of Ca activation current from Sarcoplasmic Reticulum.
    -  `k_serca` : Rate factor of SERCA Ca current back to Sarcoplasmic Reticulum.
    -  `t_open` : Time duration in which the RyR channel is open.
    -  `implementation` :
        -  `kinetic_scheme` : Kinetic scheme for the electrophysiology model.

- `myofilaments`: This sub-block contains model parameters for dynamically-coupled interaction of myofilaments.
    - `cb_number_density` : Number of myosin heads in a hypothetical cardiac half-sarcomere with a cross-sectional area of 1 m^2.
    - `k_1` : Activation rate factor of myosin heads from SRX to DRX states.
    - `k_force` : Force dependent activation rate factor of myosin heads.
    - `k_2` : Deactivation rate factor of myosin heads from DRX to SRX states.
    - `k_3` : Attachment rate factor of myosin heads from SRX to Force Generating states.
    - `k_4_0` : Detachment rate factor of myosin heads from Force Generating to SRX states.
    - `k_4_1` : Strain dependent detachment rate factor of myosin heads from Force Generating to SRX states.
    - `k_cb` : The cross-bridge stiffness factor.
    - `x_ps` : The power stroke of an attached cross-bridge.
    - `k_on` : The activation rate factor of binding sites on thin filaments.
    - `k_off` : The deactivation rate factor of binding sites on thin filaments.
    - `k_coop` : The cooperativity factor of thin filaments.
    - `passive_exp_sigma` : The sigma constant factor.
    - `passive_exp_L` : The constant factor that sets the curvature of the relationship.
    - `passive_l_slack` : Slack length of half-sarcomere.
    - `implementation` :
        - `kinetic_scheme` : Kinetic scheme of myofilaments interaction.
        - `passive_mode` : Switch control for the passive behavior of half-sarcomeres.
        - `max_rate` : A float defining the maximum rate considered in the simulations. Rate values above this will be limited to max_rate.
        - `temperature` : The temperature in Kelvin
        - `bin_min` : The minimum possible value of x in nm for the cross-bridge distribution.
        - `bin_max` : The maximum possible value of x in nm for the cross-bridge distribution.
        - `bin_width` : The width of bins in the cross-bridge distribution. Smaller values of bin_width give cross-bridge distributions with finer resolution but take longer to calculate.
        - `filament_compliance_factor` : The compliance factor of myofilaments.
        - `thick_filament_length` : The length of thick myofilament in nm.
        - `thin_filament_length` : The length of thin myofilament in nm.
        - `bare_zone_length` :  The length of bare zone.
