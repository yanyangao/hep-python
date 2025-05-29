from ROOT import TFile, TTree, TH1D, TLorentzVector
import os, math
import multiprocessing as mp
from array import array


def setup():
    # assuming the input has a directory name "miniT!"
    #inputDir = "/afs/cern.ch/work/e/epender/DarkPhotonAnalysis/hep-python/output/ntuplereader_out/p15/" 
    inputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/before_postprocessing/signal/"
    #inputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/before_postprocessing/multijet/"
    #inputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/before_postprocessing/data/"
    if not os.path.isdir(inputDir):
        print(inputDir + " does not exist, exitting")
        exit()
    # specifiy output
    outputDir = "/Users/yygao/atlas_data/DarkPhoton/data/miniT/vbfskim/unhadded/"
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    print("output directory set to be " + outputDir)
    tree = "miniT" 

    # access each root file in the inputDir
    # apply cuts on the tree and save the output in the outputDir
    files = []
    outputfiles = []
    for file in os.listdir(inputDir):
        if "500758" in file and "r9364" in file:
        #if "vbf" in file: 
        #if "jzsw" in file: 
        #if ".root" in file: 
            files.append(inputDir + file)
            outputfiles.append(outputDir + file)
    pool = mp.Pool(len(files))
    results = [pool.apply_async(skim, (files[i], outputfiles[i], tree, i)) for i in range(len(files))]
    pool.close()
    pool.join()

def skim(file, outputname, tree, index):
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
    m_intLumi = array("f", [0])
    m_nJets30 = array("i",[0])
    m_jet1_pt = array("f",[0])
    m_jet1_eta = array("f",[0])
    m_jet1_phi = array("f",[0])
    m_jet1_e = array("f",[0])
    m_jet2_pt = array("f",[0])
    m_jet2_eta = array("f",[0])
    m_jet2_phi = array("f",[0])
    m_jet2_e = array("f",[0])

    m_mjj = array("f",[0])
    m_detajj = array("f",[0])
    m_signetajj = array("f",[0])
    m_dphijj = array("f",[0])

    # MET related veraiables
    m_dphi_j1met = array("f", [0])
    m_min_dphi_jetmet = array("f", [0])

    # overall LJ
    m_nLJ20 =  array("i",[0])

    # hadronic dark photon jets
    m_nLJjets =  array("i",[0])
    m_nLJjets20 =  array("i",[0])
    m_LJjet1_pt = array("f",[0])
    m_LJjet1_eta = array("f",[0])
    m_LJjet1_phi = array("f",[0])
    m_LJjet1_m = array("f",[0])
    m_LJjet1_width = array("f",[0])
    m_LJjet1_EMfrac = array("f",[0])
    m_LJjet1_timing = array("f",[0])
    m_LJjet1_jvt = array("f",[0])
    m_LJjet1_gapRatio = array("f",[0])
    m_LJjet1_IsBIB = array("f",[0])
    m_LJjet1_DPJtagger = array("f",[0])
    m_LJjet1_truthDPidx = array("i", [0])

    # muonic DPJ
    m_nLJmus20 =  array("i",[0])
    m_LJmu1_pt = array("f",[0])
    m_LJmu1_eta = array("f",[0])
    m_LJmu1_phi = array("f",[0])

    # Declare the branches of these new variables
    scale1fb_branch = ttree_out.Branch( 'scale1fb', m_scale1fb, 'scale1fb/F' )
    intLumi_branch = ttree_out.Branch( 'intLumi', m_intLumi, 'intLumi/F' )

    nJets30_branch = ttree_out.Branch( 'nJets30', m_nJets30, 'nJets30/I' )
    jet1_pt_branch = ttree_out.Branch( 'jet1_pt', m_jet1_pt, 'jet1_pt/F' )
    jet1_eta_branch = ttree_out.Branch( 'jet1_eta', m_jet1_eta, 'jet1_eta/F' )
    jet1_phi_branch = ttree_out.Branch( 'jet1_phi', m_jet1_phi, 'jet1_phi/F' )
    jet1_e_branch = ttree_out.Branch( 'jet1_e', m_jet1_e, 'jet1_e/F' )

    jet2_pt_branch = ttree_out.Branch( 'jet2_pt', m_jet2_pt, 'jet2_pt/F' )
    jet2_eta_branch = ttree_out.Branch( 'jet2_eta', m_jet2_eta, 'jet2_eta/F' )
    jet2_phi_branch = ttree_out.Branch( 'jet2_phi', m_jet2_phi, 'jet2_phi/F' )
    jet2_e_branch = ttree_out.Branch( 'jet2_e', m_jet2_e, 'jet2_e/F' )

    # di-jet kinematics
    mjj_branch = ttree_out.Branch( 'mjj', m_mjj, 'mjj/F' )
    detajj_branch = ttree_out.Branch( 'detajj', m_detajj, 'detajj/F' )
    signetajj_branch = ttree_out.Branch( 'signetajj', m_signetajj, 'signetajj/F' )
    dphijj_branch = ttree_out.Branch( 'dphijj', m_dphijj, 'dphijj/F' )

    # MET
    dphi_j1met_branch = ttree_out.Branch( 'dphi_j1met', m_dphi_j1met, 'dphi_j1met/F')
    min_dphi_jetmet_branch = ttree_out.Branch( 'min_dphi_jetmet', m_min_dphi_jetmet, 'min_dphi_jetmet/F')

    # LJ
    nLJ20_branch = ttree_out.Branch( 'nLJ20', m_nLJ20, 'nLJ20/I' )

    # hadronic DPJ
    nLJjets_branch = ttree_out.Branch( 'nLJjets', m_nLJjets, 'nLJjets/I' )
    nLJjets20_branch = ttree_out.Branch( 'nLJjets20', m_nLJjets20, 'nLJjets20/I' )
    LJjet1_pt_branch = ttree_out.Branch( 'LJjet1_pt', m_LJjet1_pt, 'LJjet1_pt/F' )
    LJjet1_eta_branch = ttree_out.Branch( 'LJjet1_eta', m_LJjet1_eta, 'LJjet1_eta/F' )
    LJjet1_phi_branch = ttree_out.Branch( 'LJjet1_phi', m_LJjet1_phi, 'LJjet1_phi/F' )
    LJjet1_m_branch = ttree_out.Branch( 'LJjet1_m', m_LJjet1_m, 'LJjet1_m/F' )
    LJjet1_width_branch = ttree_out.Branch( 'LJjet1_width', m_LJjet1_width, 'LJjet1_width/F' )
    LJjet1_EMfrac_branch = ttree_out.Branch( 'LJjet1_EMfrac', m_LJjet1_EMfrac, 'LJjet1_EMfrac/F' )
    LJjet1_timing_branch = ttree_out.Branch( 'LJjet1_timing', m_LJjet1_timing, 'LJjet1_timing/F' )
    LJjet1_jvt_branch = ttree_out.Branch( 'LJjet1_jvt', m_LJjet1_jvt, 'LJjet1_jvt/F' )
    LJjet1_gapRatio_branch = ttree_out.Branch( 'LJjet1_gapRatio', m_LJjet1_gapRatio, 'LJjet1_gapRatio/F' )
    LJjet1_IsBIB_branch = ttree_out.Branch( 'LJjet1_IsBIB', m_LJjet1_IsBIB, 'LJjet1_IsBIB/F')
    LJjet1_DPJtagger_branch = ttree_out.Branch( 'LJjet1_DPJtagger', m_LJjet1_DPJtagger, 'LJjet1_DPJtagger/F')
    LJjet1_truthDPidx_branch = ttree_out.Branch( 'LJjet1_truthDPidx', m_LJjet1_truthDPidx, 'LJjet1_truthDPidx/I')

    # muon DPJ
    nLJmus20_branch = ttree_out.Branch( 'nLJmus20', m_nLJmus20, 'nLJmus20/I' )
    LJmu1_pt_branch = ttree_out.Branch( 'LJmu1_pt', m_LJmu1_pt, 'LJmu1_pt/F' )
    LJmu1_eta_branch = ttree_out.Branch( 'LJmu1_eta', m_LJmu1_eta, 'LJmu1_eta/F' )
    LJmu1_phi_branch = ttree_out.Branch( 'LJmu1_phi', m_LJmu1_phi, 'LJmu1_phi/F' )

    # special for the dijet samples
    # https://twiki.cern.ch/twiki/bin/view/AtlasProtected/JetEtMissMCSamples
    # BinContent(1): nubmer of total events, use this for the JZW slicing, DSID  361020 (JZ0W) - 361032 (JZ12W)
    # BinContent(2): sum of weights, use this for JZWithSW slicing 
    sumOfWeights_nEvents = tfile.numEvents.GetBinContent(1)
    # this is the default sum of weight 
    sumOfWeights = tfile.numEvents.GetBinContent(2)
    # keep track of events passing each cut
    nEvents_total = 0
    nEvents_2jets30 = 0
    nEvents_vbffilter=0
    # jet counters
    truth_count=0
    for entry in range(ttree.GetEntries()):
        ttree.GetEntry(entry)
        ttree_out.GetEntry(entry)
        #print("Processing event " + str(ttree.eventNumber))
        # make sure all branch values are reset at the beginning
        xs = ttree.amiXsection
        weight = ttree.weight
        nEvents_total = nEvents_total + 1
        if ttree.dsid in range(500757, 500764):       xs = 3.78*0.1 
        m_scale1fb[0] = xs*1000.*weight*ttree.filterEff/sumOfWeights
        #print("m_scale1fb[0] = " + str(m_scale1fb[0]))
        
        # assign integrated luminosity according to luminosity for MC
        # this variable will be used to scale the MC predictions together with scale1fb
        intLumi = 1
        if ttree.isMC:
            # mc16a: 2015+2016
            if ttree.RunNumber in range (266904, 311481): intLumi = 36.1 
            # mc16d: 2017
            if ttree.RunNumber in range (324320, 341649): intLumi = 44.3 
            # mc16e: 2018
            if ttree.RunNumber in range (348197, 364485): intLumi = 58.45
            # special setting for the 364704 sample, where mc16a is missing
            # scale the mc16d to the sum of mc16a/d lumi
            if ttree.dsid == 364704 and ttree.RunNumber in range (266904, 341649): intLumi = 36.1 + 44.3 
        m_intLumi[0] = intLumi    

        # Set initial values of the output branches
        m_nJets30[0] = -999
        m_jet1_pt[0] = -999
        m_jet1_eta[0] = -999
        m_jet1_phi[0] = -999
        m_jet1_e[0] = -999
        m_jet2_pt[0] = -999
        m_jet2_eta[0] = -999
        m_jet2_phi[0] = -999
        m_jet2_e[0] = -999
        m_mjj[0] = -999
        m_detajj[0] = -999
        m_signetajj[0] = -999  
        m_dphijj[0] = -999
        m_dphi_j1met[0] = -999
        m_min_dphi_jetmet[0] = -999

        m_nLJ20[0] = -999
        # hadronic DPJ
        m_nLJjets[0] = -999
        m_nLJjets20[0] = -999
        m_LJjet1_pt[0] = -999
        m_LJjet1_eta[0] = -999
        m_LJjet1_phi[0] = -999
        m_LJjet1_m[0] = -999
        m_LJjet1_width[0] = -999
        m_LJjet1_EMfrac[0] = -999
        m_LJjet1_timing[0] = -999
        m_LJjet1_jvt[0] = -999
        m_LJjet1_gapRatio[0] = -999
        m_LJjet1_DPJtagger[0] = -999
        m_LJjet1_IsBIB[0] = -999
        m_LJjet1_truthDPidx[0] = -999

        # muon DPJ
        m_nLJmus20[0] = -999
        m_LJmu1_pt[0] = -999
        m_LJmu1_eta[0] = -999
        m_LJmu1_phi[0] = -999

        # Fill the normal hadronic jets information
        # find the indices of all jets with pT>30 GeV and not been used in the LJ 
        jets30_loc = []
        for idx_jet in range(ttree.jet_cal_pt.size()):
            isLJ = bool(ttree.jet_cal_isLJ.at(idx_jet))
            if isLJ == False and ttree.jet_cal_pt.at(idx_jet) > 30e3: jets30_loc.append(idx_jet)
        njets30 = len(jets30_loc)
        # skip this event if it does not have at least two good jets 
        if njets30 < 2: continue
        nEvents_2jets30+=1

        # find first the leading jet index
        idx_jet1 = jets30_loc[0] 
        for loc1 in jets30_loc:
            if ttree.jet_cal_pt.at(loc1) > ttree.jet_cal_pt.at(idx_jet1): idx_jet1 = loc1
        # find the first jet index that is different from the leading jet 
        for loc2_start in jets30_loc:
            if loc2_start != idx_jet1: 
                idx_jet2 = loc2_start
                break
        for loc2 in jets30_loc:
            if loc2 != idx_jet1 and ttree.jet_cal_pt.at(loc2) > ttree.jet_cal_pt.at(idx_jet2):
                idx_jet2 = loc2 

        # apply further event selection
        p4_j1 = TLorentzVector(0, 0, 0, 0)
        p4_j2 = TLorentzVector(0, 0, 0, 0)
        p4_j1.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet1), ttree.jet_cal_eta.at(idx_jet1), ttree.jet_cal_phi.at(idx_jet1), ttree.jet_cal_e.at(idx_jet1))
        p4_j2.SetPtEtaPhiE(ttree.jet_cal_pt.at(idx_jet2), ttree.jet_cal_eta.at(idx_jet2), ttree.jet_cal_phi.at(idx_jet2), ttree.jet_cal_e.at(idx_jet2))
        temp_mjj = (p4_j1+p4_j2).M()
        # skip this event if it does not satisfy the minimial VBF selection
        if temp_mjj < 900e3 or abs(p4_j1.Eta()-p4_j2.Eta()) < 3.0: continue
        nEvents_vbffilter+=1
        # skip problematic large weight events at the tail for low pT QCD slices
        if ttree.isMC and ttree.dsid == 364702 and p4_j1.Pt() > 500e3: continue
        if ttree.isMC and ttree.dsid == 364703 and p4_j1.Pt() > 1000e3: continue

        # fill VBF jets related branches
        m_nJets30[0] = njets30
        m_jet1_pt[0] = p4_j1.Pt()
        m_jet1_eta[0] = p4_j1.Eta()
        m_jet1_phi[0] = p4_j1.Phi()
        m_jet1_e[0] = p4_j1.E()
        m_jet2_pt[0] = p4_j2.Pt()
        m_jet2_eta[0] = p4_j2.Eta()
        m_jet2_phi[0] = p4_j2.Phi()
        m_jet2_e[0] = p4_j2.E()
        m_mjj[0] = (p4_j1+p4_j2).M()
        m_detajj[0] = abs(p4_j1.Eta() - p4_j2.Eta())
        m_dphijj[0] = p4_j1.DeltaPhi(p4_j2) 
        m_signetajj[0] = 1 
        if p4_j1.Eta()*p4_j2.Eta() < 0: m_signetajj[0] = -1 

        # calculate the angular separation between MET aand leading jet
        dphi_j1_met = p4_j1.Phi() - ttree.MET_phi
        if dphi_j1_met > math.pi:
            dphi_j1_met = dphi_j1_met - 2*math.pi
        if dphi_j1_met < -math.pi:
            dphi_j1_met = dphi_j1_met + 2*math.pi
        m_dphi_j1met[0] = abs(dphi_j1_met) 
        #print("m_dphi_j1met[0] = " + str( m_dphi_j1met[0])) 

        # calculate the min-angular dphi between jets and MET
        # consider only up to 4 jets with pt > 30 GeV 
        min_dphi_jetmet = 999
        counter_jet = 0
        for idx in jets30_loc:
            counter_jet += 1 
            if counter_jet > 4: break
            dphi_jet_met = ttree.jet_cal_phi.at(idx) - ttree.MET_phi
            if dphi_jet_met  > math.pi:
                dphi_jet_met = dphi_jet_met - 2*math.pi
            if dphi_jet_met  < -math.pi: 
                dphi_jet_met = dphi_jet_met + 2*math.pi
            if abs(dphi_jet_met) < min_dphi_jetmet:
                min_dphi_jetmet = abs(dphi_jet_met)
        m_min_dphi_jetmet[0] = min_dphi_jetmet        
        #print("m_min_dphi_jetmet[0] = " + str( m_min_dphi_jetmet[0])) 

        # DPJ
        LJ20 = []
        for idx_LJ in range(ttree.ptLJ.size()): 
            if ttree.ptLJ.at(idx_LJ) >  20e3: 
                LJ20.append(idx_LJ)
        m_nLJ20[0] = len(LJ20)

        # hadronic DPJ 
        m_nLJjets[0] = ttree.LJjet_pt.size() 
        LJjets20 = []
        for idx_LJjet in range(ttree.LJjet_pt.size()): 
            if ttree.LJjet_pt.at(idx_LJjet) >  20e3: 
                LJjets20.append(idx_LJjet)
        m_nLJjets20[0] = len(LJjets20)

        # find the leading LJjet
        if len(LJjets20) > 0:
            idx_LJjet1 = LJjets20[0]
            # find leading LJjet index
            for idx_LJjet in LJjets20: 
                if ttree.LJjet_pt.at(idx_LJjet) > ttree.LJjet_pt.at(idx_LJjet1): 
                    idx_LJjet1 = idx_LJjet
            # Check truth matching for leading LJJet
            p4_LJjet1 = TLorentzVector(0, 0, 0, 0)
            p4_LJjet1.SetPtEtaPhiM(ttree.LJjet_pt.at(idx_LJjet1), ttree.LJjet_eta.at(idx_LJjet1), ttree.LJjet_phi.at(idx_LJjet1), ttree.LJjet_m.at(idx_LJjet1)) 
            # get truth particle ID for dark photons 
            truthDP_idxs= []
            for part in range(ttree.truthPt.size()):
                if ttree.truthPdgId.at(part) == 3000001: truthDP_idxs.append(part)
            min_dR_LJ_DP = 999
            LJjet1_MatchedTruthDPindex = -999
            # loop over all truth dark photons and find out the one closest to the leading LJjet using deltaR
            for idx_dp in truthDP_idxs:
                p4_truthDP = TLorentzVector(0, 0, 0, 0)
                p4_truthDP.SetPtEtaPhiE(ttree.truthPt.at(idx_dp), ttree.truthEta.at(idx_dp), ttree.truthPhi.at(idx_dp), ttree.truthE.at(idx_dp)) 
                dR_LJ_DP = p4_truthDP.DeltaR(p4_LJjet1)	
                if dR_LJ_DP < min_dR_LJ_DP: 
                    min_dR_LJ_DP = dR_LJ_DP
                    LJjet1_MatchedTruthDPindex = idx_dp
            if min_dR_LJ_DP < 0.4:
                m_LJjet1_truthDPidx[0] = LJjet1_MatchedTruthDPindex

            # fill other leading LJjet branches
            m_LJjet1_pt[0] = ttree.LJjet_pt.at(idx_LJjet1)
            m_LJjet1_eta[0] = ttree.LJjet_eta.at(idx_LJjet1)       
            m_LJjet1_phi[0] = ttree.LJjet_phi.at(idx_LJjet1)       
            m_LJjet1_m[0] = ttree.LJjet_m.at(idx_LJjet1)
            m_LJjet1_width[0] = ttree.LJjet_width.at(idx_LJjet1)
            m_LJjet1_EMfrac[0] = ttree.LJjet_EMfrac.at(idx_LJjet1)
            m_LJjet1_timing[0] = ttree.LJjet_timing.at(idx_LJjet1)
            m_LJjet1_jvt[0] = ttree.LJjet_jvt.at(idx_LJjet1)
            m_LJjet1_gapRatio[0] = ttree.LJjet_gapRatio.at(idx_LJjet1)
            m_LJjet1_IsBIB[0] = ttree.LJjet_IsBIB.at(idx_LJjet1)
            m_LJjet1_DPJtagger[0] = ttree.LJjet_DPJtagger.at(idx_LJjet1)
            m_LJjet1_IsBIB[0] = ttree.LJjet_IsBIB.at(idx_LJjet1)

        # find all indices for muon DPJ
        LJmus20 = []
        for idx_LJ in range(ttree.ptLJ.size()): 
            if ttree.ptLJ.at(idx_LJ) >  20e3 and ttree.types.at(idx_LJ) == 0: 
                LJmus20.append(idx_LJ)
        m_nLJmus20[0] = len(LJmus20)
 
        #print(ttree.eventNumber, m_nLJmus20[0])

        # find the leading mu DPJ 
        if len(LJmus20) > 0:
            idx_LJmu1 = LJmus20[0]
            # find leading LJmu index
            for idx_LJ in LJmus20: 
                if ttree.ptLJ.at(idx_LJ) > ttree.ptLJ.at(idx_LJmu1):
                    idx_LJmu1 = idx_LJ
            m_LJmu1_pt[0] = ttree.ptLJ.at(idx_LJmu1)
            m_LJmu1_eta[0] = ttree.etaLJ.at(idx_LJmu1)       
            m_LJmu1_phi[0] = ttree.phiLJ.at(idx_LJmu1)       

        ttree_out.Fill()
    
    tfile.Close()

    print ("")
    print ("SAMPLE " + file.rsplit("/", 1)[1])
    print ("SumOfWeights: " + str(sumOfWeights))
    print ("nEvents_total: "+str(nEvents_total))
    print ("nEvents_2jets30: "+str(nEvents_2jets30))
    print ("nEvents_vbffilter: "+str(nEvents_vbffilter))
    tfile_out.Write()
    tfile_out.Close()

if __name__=='__main__':
    setup()            
