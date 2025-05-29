#
# Example script to read a tree and add 6 new branches
#
from ROOT import TFile, TTree, TH1D, TLorentzVector
import os
import multiprocessing as mp
from array import array


def setup():
    # assuming the input has a directory name "miniT!"
    inputDir = "/Users/yygao/cernbox/ATLAS/Dark_photon/data/reco/miniT/multijet/"
    if not os.path.isdir(inputDir):
        print(inputDir + " does not exist, exitting")
        exit()
    # specifiy output
    outputDir = inputDir + "/weighted/"
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("output directory set to be " + outputDir)
    tree = "miniT" 

    # access each root file in the inputDir
    # apply cuts on the tree and save the output in the outputDir
    files = []
    outputfiles = []
    for file in os.listdir(inputDir):
        if "miniT_364700.root" in file:
            files.append(inputDir + file)
            outputfiles.append(outputDir + file)
    pool = mp.Pool(len(files))
    results = [pool.apply_async(addweight, (files[i], outputfiles[i], tree, i)) for i in range(len(files))]
    pool.close()
    pool.join()

def addweight(file, outputname, tree, index):
   print("Processing", file, tree, outputname) 
   tfile = TFile(file)
   ttree = tfile.Get(tree)
   histos = [key.GetName() for key in tfile.GetListOfKeys() if key.GetClassName()[:2]=="TH"]
   
   tfile_out = TFile(outputname, "recreate")
   for x in histos:
        tfile_out.WriteTObject(tfile.Get(x))
   ttree_out = ttree.CloneTree(0)
   ttree_out.SetDirectory(tfile_out)

   m_scale1fb = array("f", [0])
   m_nJets30 = array("i",[0])
   m_mjj = array("f",[0])
   m_detajj = array("f",[0])
   m_jet1_pt = array("f",[0])
   m_jet2_pt = array("f",[0])


   scale1fb_branch = ttree_out.Branch( 'scale1fb', m_scale1fb, 'scale1fb/F' )
   nJets30_branch = ttree_out.Branch( 'nJets30', m_nJets30, 'nJets30/I' )
   mjj_branch = ttree_out.Branch( 'mjj', m_mjj, 'mjj/F' )
   detajj_branch = ttree_out.Branch( 'detajj', m_detajj, 'detajj/F' )
   jet1_pt_branch = ttree_out.Branch( 'jet1_pt', m_jet1_pt, 'jet1_pt/F' )
   jet2_pt_branch = ttree_out.Branch( 'jet2_pt', m_jet2_pt, 'jet2_pt/F' )

   sumOfWeights = tfile.numEvents.GetBinContent(2) 
   print(sumOfWeights)
   for entry in range(ttree.GetEntries()): 
        ttree.GetEntry(entry)
        ttree_out.GetEntry(entry)
        # make sure all branch values are reset at the beginning
        m_scale1fb[0] = ttree.weight*ttree.amiXsection*1000.*ttree.filterEff/sumOfWeights
        m_nJets30[0] = 0
        m_mjj[0] = 0
        m_detajj[0] = 0
        m_jet1_pt[0] = 0
        m_jet2_pt[0] = 0
 
        njets30 = 0
        idx_jet1 = 0
        idx_jet2 = 0

        # find the leading jet index and the number of jets above 30 GeV
        for idx_jet in range(ttree.jet_cal_pt.size()):
            if ttree.jet_cal_pt.at(idx_jet) > 30e3: njets30 = njets30 + 1
            if ttree.jet_cal_pt.at(idx_jet) > ttree.jet_cal_pt.at(idx_jet1): idx_jet1 = idx_jet
        # find the second jet index    
        if idx_jet1 == 0: idx_jet2 = 1
        for idx_jet in range(ttree.jet_cal_pt.size()):
            if idx_jet == idx_jet1: continue
            if ttree.jet_cal_pt.at(idx_jet) > ttree.jet_cal_pt.at(idx_jet2): idx_jet2 = idx_jet
        #print(ttree.eventNumber, idx_jet1, idx_jet2, ttree.jet_cal_p)

        if ttree.jet_cal_pt.size() > 1: 
            p4_j1 = TLorentzVector(0, 0, 0, 0)
            p4_j2 = TLorentzVector(0, 0, 0, 0)
            p4_j1.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet1), ttree.jet_cal_eta.at(idx_jet1), ttree.jet_cal_phi.at(idx_jet1), ttree.jet_cal_e.at(idx_jet1))
            p4_j2.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet2), ttree.jet_cal_eta.at(idx_jet2), ttree.jet_cal_phi.at(idx_jet2), ttree.jet_cal_e.at(idx_jet2))
 
            m_mjj[0] = (p4_j1+p4_j2).M()
            m_detajj[0] = abs(p4_j1.Eta() - p4_j2.Eta())
            m_jet1_pt[0] = p4_j1.Pt()
            m_jet2_pt[0] = p4_j2.Pt()
        ttree_out.Fill()
   tfile.Close()
   tfile_out.Write()
   tfile_out.Close()

if __name__=='__main__':
    setup()            
