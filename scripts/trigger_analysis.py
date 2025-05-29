#-----------------------
# This example code performs simple analysis based on existing flat ntuple
# This by default can do the analysis on all the files within a given directory
# Check the code to place restrictions
#-----------------------

from ROOT import TFile, TTree, TH1D, TLorentzVector
import os
import multiprocessing as mp
from array import array

def setup():
    #  specify input directory and make sure the inputs are there 
    inputDir = "/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/"
    if not os.path.isdir(inputDir):
        print(inputDir + " does not exist, exitting")
        exit()
    # specifiy output
    outputDir = "output/"
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("output directory set to be " + outputDir)
    tree = "miniT" 

    # access each root file in the inputDir
    # apply cuts on the tree and save the output in the outputDir
    files = []
    outputfiles = []
    for file in os.listdir(inputDir):
        # Use this to select the files to run over
        if "500757" in file and '.root' in file:
            files.append(inputDir + file)
            outputfiles.append(outputDir + "hist-" +  file)
    pool = mp.Pool(len(files))
    results = [pool.apply_async(analysis, (files[i], outputfiles[i], tree, i)) for i in range(len(files))]
    pool.close()
    pool.join()

def analysis(file, outputname, tree, index):
    print("Processing", file, tree, outputname) 
    tfile = TFile(file)
    ttree = tfile.Get(tree)
 
    tfile_out = TFile(outputname, "recreate")

    h1_MET = TH1D("h1_MET", "h1_MET", 50, 0, 500) 
    h1_MET.Sumw2()
    h1_MET_Trig = TH1D("h1_MET_Trig", "h1_MET_Trig", 50, 0, 500) 
    h1_MET_Trig.Sumw2()
 
    h1_MET_2017 = TH1D("h1_MET_2017", "h1_MET_2017", 50, 0, 500) 
    h1_MET_2017.Sumw2()
    h1_MET_2018 = TH1D("h1_MET_2018", "h1_MET_2018", 50, 0, 500) 
    h1_MET_2018.Sumw2()

    h1_MET_Trig_2017 = TH1D("h1_MET_Trig_2017", "h1_MET_Trig_2017", 50, 0, 500) 
    h1_MET_Trig_2017.Sumw2()

    h1_MET_Trig_2018 = TH1D("h1_MET_Trig_2018", "h1_MET_Trig_2018", 50, 0, 500) 
    h1_MET_Trig_2018.Sumw2()

    for entry in range(ttree.GetEntries()): 
        ttree.GetEntry(entry)
        # apply selections
        # select the 2018 data running to analyse the trigger
        is2017 = 0
        if ttree.RunNumber in range (324320, 341649): is2017 = 1 
        is2018 = 0
        if ttree.RunNumber in range (348197, 364485): is2018 = 1 
        #if ttree.eventNumber != 90912: continue
        # plot existing branches
        evt_weight = 1 # ttree.scale1fb 
        h1_MET.Fill(ttree.MET*0.001, evt_weight) 
        if is2017: h1_MET_2017.Fill(ttree.MET*0.001, evt_weight)
        if is2018: h1_MET_2018.Fill(ttree.MET*0.001, evt_weight)

        # check if a trigger is fired
        # MET trigger
        # 2017: HLT_xe110_pufit_L1XE55
        # 2018: HLT_xe110_pufit_xe70_L1XE50
        for t in range(ttree.trig_name.size()):
            if is2017 and ttree.trig_name.at(t) == "HLT_xe110_pufit_L1XE55" and ttree.trig.at(t) == 1:
                h1_MET_Trig_2017.Fill(ttree.MET*0.001, evt_weight) 
                h1_MET_Trig.Fill(ttree.MET*0.001, evt_weight) 
            if is2018 and ttree.trig_name.at(t) == "HLT_xe110_pufit_xe70_L1XE50" and ttree.trig.at(t) == 1:
                h1_MET_Trig_2018.Fill(ttree.MET*0.001, evt_weight) 
                h1_MET_Trig.Fill(ttree.MET*0.001, evt_weight) 

    tfile.Close()

    h1_MET_TrigEff_2017 =  h1_MET_Trig_2017.Clone("h1_MET_TrigEff_2017")  
    h1_MET_TrigEff_2017.Divide(h1_MET_TrigEff_2017, h1_MET_2017, 1, 1, "B")

    h1_MET_TrigEff_2018 =  h1_MET_Trig_2017.Clone("h1_MET_TrigEff_2017")  
    h1_MET_TrigEff_2018.Divide(h1_MET_TrigEff_2017, h1_MET_2017, 1, 1, "B")

    # write histograms into file
    h1_MET.Write() 
    h1_MET_Trig.Write() 
    h1_MET_2017.Write() 
    h1_MET_Trig_2017.Write() 
    h1_MET_2018.Write() 
    h1_MET_Trig_2018.Write() 
    h1_MET_TrigEff_2017.Write()
    h1_MET_TrigEff_2018.Write()

 
    tfile_out.Close()

if __name__=='__main__':
    setup()            
