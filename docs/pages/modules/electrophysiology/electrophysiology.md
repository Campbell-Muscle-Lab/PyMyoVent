---
Title: Electrophysiology
nav_order: 4
has_children: False
parent: Modules

---
# Electrophysiology
{:.no_toc}

* Toc 
{:toc}

## Overview

The **PyMyoVent** framework can be implemented using several different electrophysiology modules. As of now, the [ten Tusscher](http://journals.physiology.org/doi/full/10.1152/ajpheart.00794.2003) model of human ventricular cells was used in the model.

The [ten Tusscher](http://journals.physiology.org/doi/full/10.1152/ajpheart.00794.2003) model uses 17 differential equations for different variable states and has 46 free parameters representing different constant factors.

The intracellular Ca2+ concentration calculated by this module drives the [MyoSim](../MyoSim/background.html) model of contractile system.

## Note

- The [ten Tusscher source code](http://journals.physiology.org/doi/full/10.1152/ajpheart.00794.2003) can be downloaded from [CellML](http://models.physiomeproject.org/exposure/c7f7ced1e002d9f0af1b56b15a873736/tentusscher_noble_noble_panfilov_2004_a.cellml/view) website.

- The [ten Tusscher](http://journals.physiology.org/doi/full/10.1152/ajpheart.00794.2003) model's parmeters were not chnaged in the original **PyMyoVent** simulation while running under fixed heart rate condition.

- Only when the [simple baroreceptor](../system_control/system_control.html) model is activated, the baroreceptor module regulates the *V<sub>max,up</sub>* (i.e. maximal SERCA uptake current) and *G<sub>CaL</sub>* (i.e. maximal L-type calcium current).

- Normally, The [ten Tusscher source code](http://models.physiomeproject.org/exposure/c7f7ced1e002d9f0af1b56b15a873736/tentusscher_noble_noble_panfilov_2004_a.cellml/view) takes several hundreds heart beats to reach to the steady state. Therefore, the steady state solution is used in **PyMyoVent** framework as the initial condition for the electrophysiology model. 