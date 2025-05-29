# This script applies a VBF skim of the miniT samples
# This would only work at the moment with at most one level of directory in the input
from ROOT import TFile, TTree, TH1D, TLorentzVector
import os
import multiprocessing as mp
from array import array


def setup():
    # assuming the input has a directory name "miniT!"
    #inputDir = "/eos/user/d/dljmcwh/storage/01-03/"
    #inputDir = "/eos/user/d/dljmcwh/storage/01-04/user.csebasti.miniT_01-04-01_data15_A_XYZ/"
    inputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/unskimed/signal/"

    if not os.path.isdir(inputDir):
        print(inputDir + " does not exist, exitting")
        exit()
    # specifiy output
    outputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/before_postprocessing/signal/"
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("output directory set to be " + outputDir)
    tree = "miniT" 

    # access each root file in the inputDir
    # apply cuts on the tree and save the output in the outputDir
    files = []
    outputfiles = []
    for file in os.listdir(inputDir):
        # deal with subdirectorise in the inputDir 
        if  os.path.isdir(inputDir + file):
            for subfile in os.listdir(inputDir + file):
                if not os.path.isdir(outputDir + file):
                    os.makedirs(outputDir + file)
                if "2655862._000001.22658562._000001" in  subfile: 
                    files.append(inputDir + file + "/" + subfile )
                    outputfiles.append(outputDir + file + "/" + subfile)
        else:
            # deal with files within  the directory
            if "500760_r10201" in file:
                files.append(inputDir + file)
                outputfiles.append(outputDir + file)
    # use multiple thread with < 20 files            
    if len(files) < 20:
        pool = mp.Pool(len(files))
        results = [pool.apply_async(vbfskim, (files[i], outputfiles[i], tree, i)) for i in range(len(files))]
        pool.close()
        pool.join()
    # process files in parallel
    # this is not ideal..
    else:
        for i in range(len(files)):
            vbfskim(files[i], outputfiles[i], tree, i) 

def vbfskim(file, outputname, tree, index):
    print("Processing", file, tree, outputname)
    tfile = TFile(file)
    ttree = tfile.Get(tree)
    histos = [key.GetName() for key in tfile.GetListOfKeys() if key.GetClassName()[:2]=="TH"]

    tfile_out = TFile(outputname, "recreate")
    for x in histos:
        tfile_out.WriteTObject(tfile.Get(x))
    ttree_out = ttree.CloneTree(0)
    ttree_out.SetDirectory(tfile_out)

    for entry in range(ttree.GetEntries()): 
        #if entry > 100000: continue
        ttree.GetEntry(entry)
        ttree_out.GetEntry(entry)
        njets30 = 0
        jets30_loc = []
        # find the leading and subleading jet index and the number of jets above 30 GeV
        for idx_jet in range(ttree.jet_cal_pt.size()):
            isLJ = bool(ttree.jet_cal_isLJ.at(idx_jet))
            if isLJ == False and ttree.jet_cal_pt.at(idx_jet) > 30e3:
                jets30_loc.append(idx_jet)
        njets30 = len(jets30_loc)
        # skip this event if it does not have at least two good jets 
        if njets30 < 2: continue
        # if at least two non LJjets, find leading and subleading
        # find first the leading jet index
        idx_jet1 = jets30_loc[0] 
        for loc1 in jets30_loc:
            if ttree.jet_cal_pt.at(loc1) > ttree.jet_cal_pt.at(idx_jet1): idx_jet1 = loc1
        # find the initial index for the subleading jet, note that this can not be the same as the leading jet
        for loc2_start in jets30_loc:
            if loc2_start != idx_jet1: 
                idx_jet2 = loc2_start
                break
        for loc2 in jets30_loc:
            if loc2 != idx_jet1 and ttree.jet_cal_pt.at(loc2) > ttree.jet_cal_pt.at(idx_jet2):
                idx_jet2 = loc2 
        # apply further event selection
        #print(ttree.eventNumber, njets30, idx_jet1, idx_jet2)
        p4_j1 = TLorentzVector(0, 0, 0, 0)
        p4_j2 = TLorentzVector(0, 0, 0, 0)
        p4_j1.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet1), ttree.jet_cal_eta.at(idx_jet1), ttree.jet_cal_phi.at(idx_jet1), ttree.jet_cal_e.at(idx_jet1))
        p4_j2.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet2), ttree.jet_cal_eta.at(idx_jet2), ttree.jet_cal_phi.at(idx_jet2), ttree.jet_cal_e.at(idx_jet2))
        temp_mjj = (p4_j1+p4_j2).M()
        # skip this event if it does not satisfy the minimial VBF selection
        if temp_mjj < 900e3 or abs(p4_j1.Eta()-p4_j2.Eta()) < 3.0: continue
        ttree_out.Fill()

    tfile.Close()

    #ttree_out.Write()
    tfile_out.Write()
    tfile_out.Close()

if __name__=='__main__':
    setup()            
