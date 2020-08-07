---
Title: MyoSim
nav_order: 3
has_children: False
parent: Modules

---
# MyoSim
{:.no_toc}

* Toc 
{:toc}
## Overview

MyoSim is software that [Ken Campbell](http://www.campbellmusclelab.org) originally wrote to simulate the mechanical properties of half-sarcomeres. It extends [Huxley-based cross-bridge distribution techniques](https://www.ncbi.nlm.nih.gov/pubmed/4449057) with Ca<sup>2+</sup> activation and cooperative effects.

This repository contains an implementation of MyoSim written in Python. Other versions of MyoSim have been written in [C++](http://www.myosim.org) and [MATLAB](http://campbell-muscle-lab.github.io/MATMyoSim/). None of the versions are completely interchangeable. All have strengths and weaknesses. The C++ code is the fastest, but also (by far) the most complicated.

## Theory

MyoSim calculates the force produced by populations of cycling cross-bridges by tracking the number of myosin heads attached to actin with different strains. This approach was originally developed by [Andrew Huxley](https://www.ncbi.nlm.nih.gov/pubmed/4449057).

The techniques required to simulate cross-bridge distributions using a computer (solving differential equations and interpolation) were described in some of Ken Campbell's earlier papers.

- [A cross-bridge mechanism can explain the thixotropic short-range elastic component of relaxed frog skeletal muscle](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2231083/)
- [A thixotropic effect in contracting rabbit psoas muscle: prior movement reduces the initial tension response to stretch](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2269955/)
- [History-dependent mechanical properties of permeabilized rat soleus muscle fibers](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1301901/)

The models described in these papers only simulated half-sarcomeres held at a fixed level of activation (i.e. they were not sensitive to the intracellular Ca<sup>2+</sup> concentration). MyoSim overcame this limitation by coupling cycling cross-bridges to a population of binding sites that were activated by Ca<sup>2+</sup> and cooperativity. The original paper explained the theory and showed how the software could be used to simulate myosin heads cycling through a variety of different kinetic schemes.

- [Dynamic coupling of regulated binding sites and cycling myosin heads in striated muscle](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3933939/)

Additional papers building on this technique include:

- [Compliance Accelerates Relaxation in Muscle by Allowing Myosin Heads to Move Relative to Actin](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4744171/)
- [Myocardial relaxation is accelerated by fast stretch, not reduced afterload](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5347980/)

MyoSim can also simulate dynamic transitions within the thick filament (OFF to ON states of myosin). The first paper investigating these transitions was:

- [Force-Dependent Recruitment from the Myosin Off State Contributes to Length-Dependent Activation](https://www.ncbi.nlm.nih.gov/pubmed/30054031)

## Parameters 

```
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
      "k_force": [1e-3, "(N^-1)(m^2)"],
      "k_2": [200, "s^-1"],
      "k_3": [110, "(nm^-1)(s^-1)"],
      "k_4_0": [200, "s^-1"],
      "k_4_1": [0.3, "nm^-4"],
      "k_cb": [0.001, "N*m^-1"],
      "x_ps": [5, "nm"],
      "k_on": [6e8, "(M^-1)(s^-1)"],
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
```