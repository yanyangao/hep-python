This scripts produces simple event selection cut flow tables. 


Run these two commands in sequence

```
python3 Cutflow.py
python3 maketable.py
```

First code creates the root files needed for the second code to run to make tables
This automatically prints out a table in latex form, you can use LatexIt for example to process.

Before running this code, make sure you modify the Cutflow.py to specify the contents for
files, trees, names, cuts, and weights 

```
files = ['/afs/cern.ch/work/e/epender/public/postprocess_out/p15/T500757_p15_TruthMatching.root', '/afs/cern.ch/work/y/yygao/public/DarkPhoton/data/miniT/vbfskim/multijet/qcd_main.root']
trees = ['miniT', 'miniT']
names = ['signal', 'background']
cuts = ['MET>225e3', 'abs(detajj)>4.', 'abs(dphijj)<2.']
weights = ['scale1fb', '140']
```

* `files` contains a list of all of the files you wish to run a cutflow on. 
* `trees` contains a list of the tree names in the respective files.
* `names` allows custom names to be specified for each file that a cutflow is run over, for example, 'signal'.
* `cuts` is a list of the cuts you wish to include in the cutflow. These cuts will be sequentially included, so the first index in this list is the minimal amount of cuts, whereas the last index in the list includes all previous cuts. '
* `weights` is simply a list of the weights you wish to use to normalise each sample. All weights will be multiplied for each sample.  

