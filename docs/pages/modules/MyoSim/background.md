### Overview

MyoSim is software that [Ken Campbell](http://www.campbellmusclelab.org) originally wrote to simulate the mechanical properties of half-sarcomeres. It extends [Huxley-based cross-bridge distribution techniques](https://www.ncbi.nlm.nih.gov/pubmed/4449057) with Ca<sup>2+</sup> activation and cooperative effects.

This repository contains an implementation of MyoSim written in Python. Other versions of MyoSim have been written in [C++](http://www.myosim.org) and [MATLAB](https://Campbell-Muscle-Lab.github.io/MATLAB_MyoSim). None of the versions are completely interchangeable. All have strengths and weaknesses. The C++ code is the fastest, but also (by far) the most complicated.

### Theory

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

