#
# This script runs after the VBF tagger dresser
# Adds VBF analysis variables 
# run for single file
# 

from ROOT import TFile, TTree, TH1D, TLorentzVector
import sys, os, math
import numpy as np
import multiprocessing as mp
from array import array

def setup():
    # assuming the input has a directory name "miniT!"
    inputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/v01-06/"
    if not os.path.isdir(inputDir):
        print(inputDir + " does not exist, exitting")
        exit()
    # specifiy output
    outputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/v01-06/vbfmetskim/"
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("output directory set to be " + outputDir)
    tree = "miniT" 

    # access each root file in the inputDir
    # apply cuts on the tree and save the output in the outputDir
    files = []
    outputfiles = []
    for file in os.listdir(inputDir):
        #if "frvz" in file and ".root" in file: 
        #if "qcd_main" in file and ".root" in file: 
        #if "strong" in file and ".root" in file: 
        #if "data1" in file and ".root" in file: 
        #if "top" in file and ".root" in file: 
        if "ewk" in file and ".root" in file: 
            files.append(inputDir + file)
            outputfiles.append(outputDir + file)
    pool = mp.Pool(len(files))
    results = [pool.apply_async(vbfmetskim, (files[i], outputfiles[i], tree, i)) for i in range(len(files))]
    pool.close()
    pool.join()


def vbfmetskim(file, outputname, tree, index):
    print("Processing", file, tree, outputname)
    tfile = TFile(file)
    ttree = tfile.Get(tree)
    if not ttree:
        print("no valid input tree, exitting")
        return 
    histos = [key.GetName() for key in tfile.GetListOfKeys() if key.GetClassName()[:2]=="TH"]
    tfile_out = TFile(outputname, "recreate")
    for x in histos:
        tfile_out.WriteTObject(tfile.Get(x))
    ttree_out = ttree.CloneTree(0)
    ttree_out.SetDirectory(tfile_out)
    for entry in range(ttree.GetEntries()):
        ttree.GetEntry(entry)
        #if entry > 10 :  continue
        if entry > 0 and entry%10000==0:
            print("Processed {} of {} entries".format(entry,ttree.GetEntries()))
        ttree_out.GetEntry(entry)
        if ttree.mjj < 1000e3: continue
        if ttree.detajj < 3.0: continue
        if ttree.njet30 < 2: continue
        if ttree.MET < 200e3: continue
        if ttree.metTrig == 0: continue
        if ttree.hasBjet == 1 : continue
        if ttree.neleSignal > 0 : continue
        if ttree.nmuSignal > 0 : continue
        ttree_out.Fill()

    tfile.Close()

    tfile_out.Write()
    tfile_out.Close()

if __name__=='__main__':
    setup()            
