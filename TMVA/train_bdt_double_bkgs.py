'''
    Run: python3 train_bdt_double_bkgs.py >& output.log
'''

# IMPORTS ===========================================================================================================
import numpy as np
from ROOT import TMVA as tmva
from ROOT import TFile, TCut

# Define function to get and return data ROOT trees ----------------------------------------------------------------
def get_trees(sig_filepath, bgd_filepath1, bgd_filepath2, tree_name):
    # open ROOT files
    sigFile  = TFile.Open(sig_filepath, "READ")
    bgdFile1 = TFile.Open(bgd_filepath1, "READ")
    bgdFile2 = TFile.Open(bgd_filepath2, "READ")
	
    # get data trees from file
    sigTree  = sigFile.Get(tree_name)
    bgdTree1 = bgdFile1.Get(tree_name)
    bgdTree2 = bgdFile2.Get(tree_name)

    # need to return files in addition to trees to prevent garb. collector closing them
    return sigTree, bgdTree1, bgdTree2, sigFile, bgdFile1, bgdFile2
	
# Define function to create and train 'Test BDT 1' -----------------------------------------------------------------
def create_bdt(sigTree, bgdTree1, bgdTree2, out_file):
    tmva.Tools.Instance()

    outfile = TFile(out_file, "RECREATE")

    arglist = ":".join(["!V", "!Silent", "Color", "DrawProgressBar", "AnalysisType=Classification"])
    factory = tmva.Factory("TMVAClassification", outfile, arglist)

    dataloader = tmva.DataLoader("eventBDT_data")

    dataloader.AddSignalTree(sigTree)
    dataloader.AddBackgroundTree(bgdTree1)
    dataloader.AddBackgroundTree(bgdTree2)
    
    #dataloader.AddVariable("MET", 'F')
    #dataloader.AddVariable("MET_phi", 'F')
    #dataloader.AddVariable("mjj", 'F')
    dataloader.AddVariable("dphijj", 'F')
    dataloader.AddVariable("detajj", 'F')
    dataloader.AddVariable("jet1_pt", 'F')
    dataloader.AddVariable("jet1_eta", 'F')
    #dataloader.AddVariable("jet1_phi", 'F')
    dataloader.AddVariable("jet1_e", 'F')
    dataloader.AddVariable("jet2_pt", 'F')
    #dataloader.AddVariable("jet2_eta", 'F')
    #dataloader.AddVariable("jet2_phi", 'F')
    dataloader.AddVariable("jet2_e", 'F')
    dataloader.AddVariable("min_dphi_jetmet", 'F')
    #dataloader.AddVariable("METOSqrtHT", 'F')
    dataloader.AddVariable("METsig", 'F')
    #dataloader.AddVariable("dphi_j1met", 'F')
    #dataloader.AddVariable("HT_20", 'F')


    # add MC weight as spectator so that it does not inform training but can be used below
    # dataloader.AddSpectator("weight")
    dataloader.AddSpectator("scale1fb")
    # account for intrinsic MC weights
    dataloader.SetBackgroundWeightExpression("scale1fb")
    dataloader.SetSignalWeightExpression("scale1fb")

    # include pre-selection cuts

    sigCut = TCut("1 && 1 && njet30>=2 && mjj>1e6 && abs(detajj)>3.0 && metTrig==1 && MET>200e3 && hasBjet==0 && nLJ20==0 && min_dphi_jetmet>0.4 && nmuSignal==0 && neleSignal==0")
    bgdCut = TCut("1 && 1 && njet30>=2 && mjj>1e6 && abs(detajj)>3.0 && metTrig==1 && MET>200e3 && hasBjet==0 && nLJ20==0 && min_dphi_jetmet>0.4 && nmuSignal==0 && neleSignal==0")


    # setting both train signal and background samples to zero yields 50/50 data split. 
    # Number of events normalised TODO: this vs accounting for MC weights? ...
    #arglist = ":".join(["nTrain_Signal=0", "nTrain_Bkg1=0", "nTrain_Bkg2=0", "SplitMode=Random", "NormMode=None", "!V"])
    arglist = ":".join(["nTrain_Signal=0", "nTrain_Background=0", "SplitMode=Random", "NormMode=None", "!V"])
    dataloader.PrepareTrainingAndTestTree(sigCut, bgdCut, arglist)
    #set UseBaggedBoost= True - check 
    #try nCuts = -1 - goes through all possibilities 
    #arglist = ":".join(["!H", "!V", "NTrees=100:MinNodeSize=1.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost=True:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2:PruneMethod=NoPruning:NegWeightTreatment=Pray"])
    arglist = ":".join(["!H", "!V", "NTrees=200:MinNodeSize=1.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost=True:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=3:PruneMethod=NoPruning:NegWeightTreatment=Pray:VarTransform=G,D"])
    #arglist = ":".join(["!H", "!V", "NTrees=100:MinNodeSize=1.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=3:PruneMethod=NoPruning:NegWeightTreatment=Pray"])
    method  = factory.BookMethod(dataloader, tmva.Types.kBDT, "BoostType=BDTG", arglist)	
    
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    outfile.Close() 


# MAIN METHOD =======================================================================================================
def main():

    sigFilepath  = "~/Documents/Documents_New/rootfiles/signal_57_58_62.root"
    bgdFilepath1 = "~/Documents/Documents_New/rootfiles/wjets_strong_sh227.root"
    bgdFilepath2 = "~/Documents/Documents_New/rootfiles/wjj_ewk.root"

    sigTree, bgdTree1, bgdTree2, sigFile, bgdFile1, bgdFile2 = get_trees(sigFilepath, bgdFilepath1, bgdFilepath2, 'miniT')
    
    create_bdt(sigTree, bgdTree1, bgdTree2, "simple_event_bdt.root")

main()