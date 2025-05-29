# HEP-Python

This directory contains a number of baseline python scripts to perform simplified analyses in experimental particle physics. 
Many have been developed by Matthew Sullivan from the University of Liverpool

## Setup

Clone the repository
```
git clone https://github.com/yanyangao/hep-python 
```

If you need to switch to other branch than master, do

```
cd hep-python/
git checkout branchname
```

branchname is by default main

### Cutflow

Based on existing ROOT TTrees, output nubmer of events after specified selections. 

### Plotting

Based on existing ROOT TTrees, output distributions overlaying signal, background and data. 

### TMVA

Based o existing ROOT TTrees, perform an example supervised training based on BDT and apply the training  output at analysis level.

### scripts

A few example scripts in handling TTrees
