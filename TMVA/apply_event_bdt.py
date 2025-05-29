'''
Description: Applies the weights of the trained event-level BDT classifier to unseeen data of unknown signal/background composition, and stores the output in a new branch in the input ROOT tree.
Example running script
python3 apply_event_bdt.py -t miniT -i /Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root -o output/ -w eventBDT_data/weights/TMVAClassification_BoostType=BDTG.weights.xml
'''
__author__ = "Jack Gargan and Yanyan Gao"
__doc__ = ""


# IMPORTS ===========================================================================================================
import numpy as np
from ROOT import TMVA as tmva
from ROOT import TFile, TTree
from array import array
import argparse, os


def main():

    parser = argparse.ArgumentParser(description='TMVA analysis script')
    parser.add_argument('-t', action="store", dest="tree_name", default="miniT")
    parser.add_argument('-i', action="store", dest="ip_file")
    parser.add_argument('-o', action="store", dest="op_dir")
    parser.add_argument('-w', action="store", dest="bdt_weights_file", default="")

    args = parser.parse_args()
    # get the filename from  the input file, last name element after "/"
    ip_file_array = args.ip_file.split("/")
    filename = ip_file_array[len(ip_file_array)-1]
    # Get input file and input tree 
    ip_tfile = TFile.Open(args.ip_file, "READ")
    # check if the input file is valid
    if not ip_tfile:
        print(args.ip_file + " does not exist, exitting")
        return
    ip_tree = ip_tfile.Get(args.tree_name)
    # check if the ip_tree is valid 
    if not ip_tree:
        print(args.treename + " does not exist, exitting") 
        return
    # create new file    
    os.system('mkdir -p ' + args.op_dir)
    op_tfile = TFile(args.op_dir +"/" + filename, "recreate")
    # copy all the histograms in the original file
    histos = [key.GetName() for key in ip_tfile.GetListOfKeys() if key.GetClassName()[:2]=="TH"]
    for x in histos:
        op_tfile.WriteTObject(ip_tfile.Get(x))
    # clone the ip_tree to op_tree and make sure this tree is assigned to the op_tfile 
    op_tree = ip_tree.CloneTree(0)
    op_tree.SetDirectory(op_tfile)

    # begin TMVA reader setup
    # These variables must match exactly what you used in the training
    reader = tmva.Reader()

    local_mjj     = array('f', [0]); reader.AddVariable("mjj", local_mjj)
    local_dphijj  = array('f', [0]); reader.AddVariable("dphijj", local_dphijj)
    local_detajj  = array('f', [0]); reader.AddVariable("detajj", local_detajj)
    local_jet1_pt = array('f', [0]); reader.AddVariable("jet1_pt", local_jet1_pt)
    local_jet1_eta = array('f', [0]); reader.AddVariable("jet1_eta", local_jet1_eta)
    local_jet2_pt = array('f', [0]); reader.AddVariable("jet2_pt", local_jet2_pt)
    local_jet2_eta = array('f', [0]); reader.AddVariable("jet2_eta", local_jet2_eta)
	
    reader.AddSpectator("scale1fb", array('f', [0]))	
    # make sure event_BDT matches the name in the weight
    reader.BookMVA("BDTG", args.bdt_weights_file)

    bdt_response = array('f', [0])
    # define the BDT output branch, this does not need to be same as the method name
    branch_name = 'VBF_BDT'
    bdt_branch = op_tree.Branch(branch_name,  bdt_response, branch_name+'/F')

    for entry in range(ip_tree.GetEntries()): 
        ip_tree.GetEntry(entry)
        op_tree.GetEntry(entry)
        #if entry > 5: continue
        local_mjj[0]     = ip_tree.mjj
        local_dphijj[0]  = ip_tree.dphijj
        local_detajj[0]  = ip_tree.detajj
        local_jet1_pt[0] = ip_tree.jet1_pt
        local_jet1_eta[0] = ip_tree.jet1_eta
        local_jet2_pt[0] = ip_tree.jet2_pt
        local_jet2_eta[0] = ip_tree.jet2_eta
        bdt_response[0] = reader.EvaluateMVA("BDTG")
        #print(ip_tree.eventNumber, local_mjj[0], local_dphijj[0], local_jet1_pt[0], local_jet2_pt[0], bdt_response[0])	
        op_tree.Fill()
    # make sure you close each file after it is open
    ip_tfile.Close()	
    # write the output file
    op_tfile.Write()
    op_tfile.Close()


if __name__ == '__main__':
    main()
