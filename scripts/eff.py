#
# This is an example script to analyse the hadronic lepton jet reconstruction efficiency
#

import ROOT, os
from ROOT import TFile, TLorentzVector, gStyle, TLegend

# Set global variables, input and output

# specifiy output plot directory
outputDir = "output/plots/"
if not os.path.isdir(outputDir):
    os.makedirs(outputDir)
print("output directory set to be " + outputDir)
 

path = '/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root'
myfile  = ROOT.TFile.Open(path, "READ")
tree = myfile.Get("miniT")

# define histograms
nbins = 50
xMin = 0
xMax = 10e3
h_lxy_den = ROOT.TH1D("den","den", nbins, xMin, xMax)
h_lxy_den.SetXTitle("Truth DP Lxy mm")
h_lxy_den.Sumw2()

h_lxy_num = ROOT.TH1D("h_lxy_num","h_lxy_num", nbins, xMin, xMax)
h_lxy_num.Sumw2()

h_lxy_eff = ROOT.TH1D("h_lxy_eff","h_lxy_eff", nbins, xMin, xMax)
h_lxy_eff.SetXTitle("Truth DP Lxy mm")
h_lxy_eff.Sumw2()

# define histograms or all dark photon and LJjets 
h_lxy_den_all = ROOT.TH1D("h_lxy_den_all","h_lxy_den_all", nbins, xMin, xMax)
h_lxy_den_all.SetXTitle("Truth DP Lxy mm")
h_lxy_den_all.Sumw2()

h_lxy_num_all = ROOT.TH1D("h_lxy_num_all","h_lxy_num_all", nbins, xMin, xMax)
h_lxy_num_all.SetXTitle("Truth DP Lxy mm")
h_lxy_num_all.Sumw2()

h_lxy_eff_all = ROOT.TH1D("h_lxy_eff_all","h_lxy_eff_all", nbins, xMin, xMax)
h_lxy_eff_all.SetXTitle("Truth DP Lxy mm")
h_lxy_eff_all.Sumw2()


for entry in range(tree.GetEntries()):

    tree.GetEntry(entry)
    #if entry > 100: continue
    #if tree.eventNumber!=  43795: continue

    nPart = tree.truthPdgId.size()
    dp_collection = []
    for index in range(nPart):
        if tree.truthPdgId[index] == 3000001:
            dp_collection.append(index)

    nDP = len(dp_collection)
    # skip this event if we do not have any dark photons
    if nDP < 1: continue
    idx_dp1 = dp_collection[0]
    pt_dp1 = tree.truthPt.at(idx_dp1)
    for idx in dp_collection:
        if tree.truthPt.at(idx) > pt_dp1:
            idx_dp1 = idx
            pt_dp1 = tree.truthPt.at(idx)
    #print(tree.eventNumber, dp_collection, idx_dp1)
    # Analyse the leading dark photon in the barrel region
    # to be matched with the leading lepton jets 
    if abs(tree.truthEta.at(idx_dp1))<1.1 :
        # Calculate lxy
        lx = tree.truthDecayVtx_x.at(idx_dp1)
        ly = tree.truthDecayVtx_y.at(idx_dp1)
        lxy = (lx * lx + ly * ly)**0.5
        h_lxy_den.Fill(lxy)
    
        # Calculate deltaR with the leading 
        dp1, LJ1 = TLorentzVector(), TLorentzVector()
        dp1.SetPtEtaPhiE(tree.truthPt.at(idx_dp1), tree.truthEta.at(idx_dp1), tree.truthPhi.at(idx_dp1), tree.truthE.at(idx_dp1))
        deltaR = 999
        if tree.nLJjets20 > 0:
            LJ1.SetPtEtaPhiM(tree.LJjet1_pt, tree.LJjet1_phi, tree.LJjet1_eta, tree.LJjet1_m)
            deltaR = dp1.DeltaR(LJ1)
            #print(dp1.Pt()*0.001, dp1.Eta(), LJ1.Pt()*0.001, LJ1.Eta(), deltaR)
            if deltaR<0.4:
                #print("Event ", tree.eventNumber, "Leading LJ is matched to leading DP")
                h_lxy_num.Fill(lxy)

    # Analyse all dark photons in the barrel region
    # to be matched with all the LJ objects
    for idx_dp in dp_collection:
        if abs(tree.truthEta.at(idx_dp)) < 1.1:
            lx = tree.truthDecayVtx_x.at(idx_dp)
            ly = tree.truthDecayVtx_y.at(idx_dp)
            lxy = (lx * lx + ly * ly)**0.5
            h_lxy_den_all.Fill(lxy)

            # loop over all reconstructed LJ to find a potential match within deltaR < 0.4
            dp, LJ = TLorentzVector(), TLorentzVector()
            dp.SetPtEtaPhiE(tree.truthPt.at(idx_dp), tree.truthEta.at(idx_dp), tree.truthPhi.at(idx_dp), tree.truthE.at(idx_dp))
            deltaR = 999
            nLJjets = tree.LJjet_pt.size()
            for idx_lj in range(tree.LJjet_pt.size()):
                LJ.SetPtEtaPhiM(tree.LJjet_pt.at(idx_lj), tree.LJjet_eta.at(idx_lj), tree.LJjet_phi.at(idx_lj), tree.LJjet_m.at(idx_lj))
                deltaR = dp.DeltaR(LJ)
                #print(dp.Pt()*0.001, dp.Eta(), LJ.Pt()*0.001, LJ.Eta(), deltaR)
                if deltaR < 0.4:
                    #print("Event ", tree.eventNumber, "Found a match")
                    h_lxy_num_all.Fill(lxy)
                    # when found a match exit search
                    break

# Fill the efficiency for the dp1->LJ1 match
# set the overflow bin to the last bin of the histogram
lastbin = h_lxy_den.GetNbinsX()
overflow = h_lxy_den.GetBinContent(lastbin+1)
content_lastbin = h_lxy_den.GetBinContent(lastbin)
h_lxy_den.SetBinContent(lastbin, content_lastbin + overflow )
h_lxy_eff = h_lxy_num.Clone()
h_lxy_eff.Divide(h_lxy_eff, h_lxy_den, 1,  1, "B")

# Fill the efficiency for all dp -> all LJ match 
# set the overflow bin to the last bin of the histogram
lastbin = h_lxy_den_all.GetNbinsX()
overflow = h_lxy_den_all.GetBinContent(lastbin+1)
content_lastbin = h_lxy_den_all.GetBinContent(lastbin)
h_lxy_den_all.SetBinContent(lastbin, content_lastbin + overflow )
h_lxy_eff_all = h_lxy_num_all.Clone()
h_lxy_eff_all.Divide(h_lxy_eff_all, h_lxy_den_all, 1,  1, "B")


# Prepare the canvas for plotting
# Make a canvas
canvas = ROOT.TCanvas("canvas")
gStyle.SetOptStat(0)
# Move into the canvas (so anything drawn is part of this canvas)
canvas.cd()

# Open the canvas for continuous printing
# This works for a few file types, most notably pdf files
# This allows you to put several plots in the same pdf file
# The key is the opening square-bracket after the desired file name
h_lxy_eff.Draw()

# Add a line for HCAL
yMax = h_lxy_eff.GetMaximum()
line_HC = ROOT.TLine(2000,0.,2000, yMax)
line_HC.SetLineColor(ROOT.kRed)
line_HC.SetLineWidth(2)
line_HC.Draw()
# Add a line for HCAL
line_HC_2 = ROOT.TLine(4000,0.,4000,yMax)
line_HC_2.SetLineColor(ROOT.kRed)
line_HC_2.SetLineWidth(2)
line_HC_2.Draw()

# Write the plot to the output plot file
canvas.Print(outputDir + '/Effiiciency_dp1.pdf')

# save the lxy distribution
canvas.Clear()
canvas.SetLogy()
# define the location of the legend
x0, x1, y0, y1 = 0.50, 0.60, 0.70, 0.80
legend = TLegend(x0,y0,x1,y1) 
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.SetTextSize(0.032)
legend.SetFillColor(0)
legend.SetFillStyle(0)
legend.SetLineColor(0)  
legend.AddEntry(h_lxy_den, "Truth DP", 'l')
legend.AddEntry(h_lxy_num, "Matched hadronic LJ", 'l')

h_lxy_den.SetMinimum(0.1)
h_lxy_den.Draw()
h_lxy_num.SetLineColor(2)
h_lxy_num.Draw("samehist")
legend.Draw("same")

canvas.Print('lxy_dp1.pdf')

# Redo everything for the all dp ones
canvas.Clear()
canvas.SetLogy(0)
h_lxy_eff_all.Draw()

# Add a line for HCAL
yMax = h_lxy_eff_all.GetMaximum()
line_HC = ROOT.TLine(2000,0.,2000, yMax)
line_HC.SetLineColor(ROOT.kRed)
line_HC.SetLineWidth(2)
line_HC.Draw()
# Add a line for HCAL
line_HC_2 = ROOT.TLine(4000,0.,4000,yMax)
line_HC_2.SetLineColor(ROOT.kRed)
line_HC_2.SetLineWidth(2)
line_HC_2.Draw()

# Write the plot to the output plot file
canvas.Print(outputDir + '/Effiiciency_dp_all.pdf')

# save the lxy distribution
canvas.Clear()
gStyle.SetOptStat(0)
canvas.SetLogy()
h_lxy_den_all.SetMinimum(0.5)
h_lxy_den_all.Draw()
h_lxy_num_all.SetLineColor(2)
h_lxy_num_all.Draw("samehist")
legend.Draw("same")
canvas.Print('lxy_dp_all.pdf')



myfile.Close()
