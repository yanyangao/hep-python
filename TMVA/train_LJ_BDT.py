'''
     Author: Jack Gargan
       Date: 25/06/2020
Description: Train event-level BDT on signal and background DP data with selected input features using TMVA.
'''

# IMPORTS ===========================================================================================================
import numpy as np
from ROOT import TMVA as tmva
from ROOT import TFile, TCut

# Define function to get and return data ROOT trees ----------------------------------------------------------------
def get_trees(sig_filepath, bgd_filepath, tree_name):
    # open ROOT files
    sigFile = TFile.Open(sig_filepath, "READ")
    bgdFile = TFile.Open(bgd_filepath, "READ")
	
    # get data trees from file
    sigTree = sigFile.Get(tree_name)
    bgdTree = bgdFile.Get(tree_name)

    # need to return files in addition to trees to prevent garb. collector closing them
    return sigTree, bgdTree, sigFile, bgdFile
	
# Define function to create and train 'Test BDT 1' -----------------------------------------------------------------
def create_bdt(sigTree, bgdTree, out_file):
    tmva.Tools.Instance()

    outfile = TFile(out_file, "RECREATE")
	
    arglist = ":".join(["!V", "!Silent", "Color", "DrawProgressBar", "AnalysisType=Classification"])
    factory = tmva.Factory("TMVAClassification", outfile, arglist)

    dataloader = tmva.DataLoader("LJ_BDT_data")
    dataloader.AddSignalTree(sigTree)
    dataloader.AddBackgroundTree(bgdTree)
    dataloader.AddVariable("LJjet1_jvt",      'F')
    dataloader.AddVariable("LJjet1_m",        'F')
    dataloader.AddVariable("LJjet1_EMfrac",   'F')
    dataloader.AddVariable("LJjet1_width",   'F')
    # add MC weight as spectator so that it does not inform training but can be used below
    dataloader.AddSpectator("scale1fb")
    # account for intrinsic MC weights
    dataloader.SetBackgroundWeightExpression("scale1fb")
    #dataloader.SetSignalWeightExpression("weight")
        
    sigCut = TCut("nLJjets>0  && LJjet1_pt>20e3 && LJjet1_gapRatio>0.9 && LJjet1_DPtruthMatched > 0")
    bgdCut = TCut("nLJjets>0  && LJjet1_pt>20e3 && LJjet1_gapRatio>0.9")

    # setting both train signal and background samples to zero yields 50/50 data split. 
    # Number of events normalised TODO: this vs accounting for MC weights? ...
    arglist = ":".join(["nTrain_Signal=0", "nTrain_Background=0", "SplitMode=Random", "NormMode=None", "!V"])
    dataloader.PrepareTrainingAndTestTree(sigCut, bgdCut, arglist)

    arglist = ":".join(["!H", "!V", "NTrees=1000:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2:PruneMethod=NoPruning"])
    method  = factory.BookMethod(dataloader, tmva.Types.kBDT, "BoostType=BDTG", arglist)

    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    outfile.Close() 
	
# MAIN METHOD =======================================================================================================
def main():

    #sigFilepath = "/afs/cern.ch/work/j/jagargan/public/vbf_bdt/out_signal.root"
    sigFilepath = "/Users/yygao/cernbox/ATLAS/Dark_photon/data/miniT/vbfskim/signal/reco/vbf_bdt/T500757_p15_TruthMatching.root"
    #bgdFilepath = "/afs/cern.ch/work/j/jagargan/public/vbf_bdt/out_background.root"
    #bgdFilepath = "/Users/yygao/cernbox/ATLAS/Dark_photon/data/miniT/vbfskim/multijet/vbf_bdt/qcd_main.root"
    bgdFilepath = "/Users/yygao/cernbox/ATLAS/Dark_photon/yanyan_hep_python/hep-python/scripts/qcd_main.root"
	
    sigTree, bgdTree, sigFile, bgdFile = get_trees(sigFilepath, bgdFilepath, "miniT")
    create_bdt(sigTree, bgdTree, "lj_bdt.root")

main()
