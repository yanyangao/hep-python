#  Pre-requisite: Setting up the scripts 

```
setupATLAS
lsetup "views LCG_107_swan x86_64-el9-gcc13-opt"
```
Then copy both signal and background file in this area
/home/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/vbfljetskim/
 

# Running the scripts

If everything is defined and checked, you can run by:

```
python3 train_LJjet1_AD_v1.py 
```

You need to close the x11 window for the plots to proceed to the next step. Two plots would pop up, one for the loss the other for the score.

# Hints for technical problems:

