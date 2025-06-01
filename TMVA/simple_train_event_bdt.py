'''
     Author: Jack Gargan and Yanyan Gao
    Description: example script for BDT based training  between  signal and background
        Run: python3  simple_train_event_bdt.py 
'''

# IMPORTS ===========================================================================================================
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

    dataloader = tmva.DataLoader("eventBDT_data")
    dataloader.AddSignalTree(sigTree)
    dataloader.AddBackgroundTree(bgdTree)
    dataloader.AddVariable("mjj", 'F')
    dataloader.AddVariable("dphijj", 'F')
    dataloader.AddVariable("detajj", 'F')
    dataloader.AddVariable("jet1_pt", 'F')
    dataloader.AddVariable("jet1_eta", 'F')
    dataloader.AddVariable("jet2_pt", 'F')
    dataloader.AddVariable("jet2_eta", 'F')
    # add MC weight as spectator so that it does not inform training but can be used below
    #  dataloader.AddSpectator("weight")
    dataloader.AddSpectator("scale1fb")
    # account for intrinsic MC weights
    dataloader.SetBackgroundWeightExpression("scale1fb")

    # include pre-selection cuts here if desired. Left blank as default option
    #sigCut = TCut("MET>150e3")
    #bgdCut = TCut("MET>150e3")
    sigCut = TCut("min_dphi_jetmet>0.4")
    bgdCut = TCut("min_dphi_jetmet>0.4")
    #sigCut = TCut("1")
    #bgdCut = TCut("1")

    # setting both train signal and background samples to zero yields 50/50 data split. 
    # Number of events normalised TODO: this vs accounting for MC weights? ...
    #arglist = ":".join(["nTrain_Signal=0", "nTrain_Background=0", "SplitMode=Random", "NormMode=None", "!V"])
    # use 6000 signal events for training at least
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
    sigFilepath = "/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root"
    bgdFilepath = "/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/wjets_strong_sh227.root"

    sigTree, bgdTree, sigFile, bgdFile = get_trees(sigFilepath, bgdFilepath, "miniT")
	
    create_bdt(sigTree, bgdTree, "simple_event_bdt.root")

main()
