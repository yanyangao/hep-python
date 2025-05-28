# HEP-Python

This directory contains a number of baseline python scripts to perform simplified analyses in experimental particle physics. Many have been developed by Matthew Sullivan from the University of Liverpool, https://gitlab.cern.ch/msulliva/hep-python.

## Setup

Clone the repository
```
git clone https://gitlab.cern.ch/yygao/hep-python.git
```

If you need to switch to other branch than master, do

```
cd hep-python/
git checkout branchname
```

### Cutflow

Based on existing ROOT TTrees, output nubmer of events after specified selections. 

### Plotting

Based on existing ROOT TTrees, output distributions overlaying signal, background and data. 

### XGBoost

Based on existing ROOT TTrees, perform an example supervised training based on BDT and apply the training  output at analysis level.

### scripts

A few example scripts in handling TTrees
