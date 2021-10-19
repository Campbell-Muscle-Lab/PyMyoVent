---
title: Installation
has_children: false
nav_order: 2
---

# Installation

PyMyoVent is written in Python 3 and uses Anaconda for managing environments.

## 1) Install Anaconda

+ Install Python 3.8 from <https://www.anaconda.com/products/individual#windows>, and download the “Python 3.8 version.”
  + Accept all default settings.

## 2) Download the PyMyoVent package

There are two options:
+ Pull the repository from <https://campbell-muscle-lab.github.io/PyMyoVent>
    + If you need help with GitHub, try <http://campbell-muscle-lab.github.io/howtos_Python>
+ Download and unzip a release

Either way, create a structure to hold the source. It might look like this.

```
C:\Users\<user-name>\Documents\PyMyoVent
                      |- demo_files\
                      |- docs\
                      |- environment\
                      |- manuscripts\           
                      |- Python_code\
                      |- README.md               
```

## 3) Activate the environment 

+ Open an Acaconda prompt by typing `Anaconda Prompt` in the Windows Start Menu
+ Change directory to `<PyMyoVent_dir>/environment`
  + Use the `cd` command
+ Run the command `conda env create -f environment.yml`
  + Anaconda will handle the download and installation of all dependencies.

## 4) Use the FiberSim environment

Each time you want to run PyMyoVent simulations, you need to launch an Anaconda Prompt to write the command lines. Your first command line should always be to *activate* the PyMyoVent environment. To do so:

+ Open an Anaconda Prompt
+ Type `conda activate PyMyoVent`

## 5) Run simulations

You are now ready to try the [demos](../demos/demos.html)