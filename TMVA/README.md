#  Pre-requisite: Setting up the scripts 

This directory presents simple TMVA based ML analysis
https://root.cern.ch/download/doc/tmva/TMVAUsersGuide.pdf


# Script to training a simple Sig/Bkg classifier in TMVA

`python3 train_LJjet1_BDT.pys

- This example script trains a BDT classifer to distinguish displaced jets from dark photons from prompt jets from Wjets processes 
- Training process depends on the complexity of the training, e.g. the nubmer of variables and the specs in the nodes etc.
This example should take no more than 5 minutes
- After training a directory `LJjet1_BDT_data` will be created where inside, you can find the trained weight file to be used to apply the trained algorithm to any data `LJjet1_BDT_data/weights/TMVAClassification_BoostType=BDTG.weights.xml' 
- You should always inspect the training performance after each training, the easiest is to use the built in TMVAGui (Guide section 2.6), with a root terminal do `TMVA::TMVAGui("lj_bdt.root")`. This can display information such as overla

- There is a similar code to train a BDT based jet classifier to distinguish VBF signal and QCD background using leading jet kinematics `simple_train_event_bdt.py` 

# Scripts to apply existing training (aka weights) to any file


`python3 apply_event_bdt.py -t miniT -i input.root -o outputDir/ -w LJjet1_DT_data/weights/TMVAClassification_BoostType=BDTG.weights.xml
'

Description: Applies the weights of the trained event-level BDT classifier to 
any data with the same input variables (e.g. `input.root`), stores the MVA classifier output (defined in the script)
as a new branch and save as the same name but in a new outputDir

# Analysis level ROC curve 

Once you have applied the trained weights to your chosen signal and background data, you can use this example scripts to evaluate the performance of the new classifier.
This is not the same as the intrinsic ROC curve given in the training. As this would be evaluated on different events and will take account into potentially different selections, differnet MC weights

`python3 get_roc_curve.py  -o output/`





