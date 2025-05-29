#  Pre-requisite: Setting up the scripts 

To run the plotting script, two files are first needed: `files.json` and `regions.json`. 

## files.json

This file defines the samples, with each entry defined as the example below
```
"VBF": {
    "sampletype": "signal",
    "filepath": "/afs/cern.ch/work/y/yygao/public/DarkPhoton/data/miniT/vbfskim/signal/DAOD_TRUTH1.600001_0.pool.root",
    "treename": "miniT",
    "colour": "4",
    "blind": "False",
    "unitynorm": "True",
    "scalefactor": 1,
    "includeweights": "scale1fb",
    "excludeweights": ""
}
```
* `VBF` here is the name of the used-defined name. 
* `sampletype` has three options; "background", "signal" and "data". This determines if a sample is added to the "background stack, plotted as data points in black or as an overlaid line for signal. 
* `filepath` gives the full path to the file. "treename" tells the script where the variables are located that you wish to plot. 
* `colour` defines the plotting colour (see ROOT TColor).
* `blind` can either be "False" or "True"; if set to false this sample will be included in the plot, if true it will be excluded or "blinded". 
* `unitynorm` can either be "False" or "True"; if set to false this sample uses the weights specified below, if true the sample will be normalised to unity after the selection.
* `scalefactor` allows a sample to be scaled by a  overall numerical factor
* `includeweights` allows to use event level weights present in the input ntuples 
* `excludeweights` is not yet function 

## `regions.json`

This file defines selections at different stages of the analysis, such as `vbffilter`, `preselection`, and different regions of interest such  as signal regions or control regions. All selections in this file must be structed as below:

```
"vbffilter": {
    "cuts": "(nJets30>1) * (mjj>750e3) * (detajj>2)",
    "blinding_cuts": "",
    "blind": "True",
    "forcebins": "",
    "bkgerrors": ""
},            
 
```

* unique region name, e.g. "vbffilter"
* `cuts` - defines the region in terms of selections. NOTE - the structure of cuts must be '(CONDITION-1) * (CONDITION-2) * ... * (CONDITION-N)'. For each condition, you can have more than one selections implemented. 
* `blinding_cuts` - allows selections to be on data while not entirely blinding the plot of all data. "blind" can either be "True" or "False", and will blind the plot of all data if set to true. 

## To make a plot, add a line to plotter.py

```
self.newplot(files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 0, PLOTSIGNALS = False, ratioplot = '',forcebins=False):
```

The arguments are as follows:

* `files` - name and location of the json file, e.g. "files.json"    
* `variable` - name of the variable you wish to plot from your ttree. You can scale the variables here if you wish, e.g. 'met\*0.001' would plot the 'met' variable with a scaling of 0.001 applied, thus going from MeV to GeV.    
* `variablename` - more readable name, for example "Leading Jet pT" instead of the branchname "jet1_pt"
* `units` - the units to use for the x axis label    
* `region` - the name of the region in which you wish to make the plot, for example "vbffilter" defined in `regions.json`
* `nbins` - how many bins in x you wish your histograms to have    
* `xmin, xmax` - the x range of your histogram     
* `ymin = 0, ymax = 0` -  if set, these determine the y range of your histogram. If plotting in log, you should always set ymin to be > 0.    
* ratioplot = '' - can either be left blank or set to 'datamc', which plots the data/MC ratio in the bottom pad    

# Running the scripts

If everything is defined and checked, you can run by:

```
python3 plotter.py
```

# Hints for technical problems:

Important: requires python3, instead of python in Cutflow.
* python3 exists at lxplus. If it doesn't work, you can logout and login again in a new terminal.
* Note for ATLAS users: python version may be in conflict with the enviorment settings after running "setupATLAS". If problem arises, make sure you do not have this in your  bash profile.  
