#
# This is an example script to analyse the hadronic lepton jet reconstruction efficiency
#

import ROOT, os
from ROOT import TFile, TLorentzVector, gStyle, TLegend

# Set global variables, input and output

# specifiy output plot directory
outputDir = "output/plots_truth/"
if not os.path.isdir(outputDir):
    os.makedirs(outputDir)
print("output directory set to be " + outputDir)
 

path = '/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root'
myfile  = ROOT.TFile.Open(path, "READ")
tree = myfile.Get("miniT")

# define histograms

h_dp_pt = ROOT.TH1D("h_dp_pt","h_dp_pt", 50, 0, 200)
h_dp_pt.SetXTitle("Leading Truth DP pT GeV")
h_dp_pt.Sumw2()

h_dp_lxy = ROOT.TH1D("h_dp_lxy","h_dp_lxy", 50, 0, 10e3)
h_dp_lxy.SetXTitle("Leading Truth DP Lxy mm")
h_dp_lxy.Sumw2()

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
    for idx in dp_collection:
        lx = tree.truthDecayVtx_x.at(idx)
        ly = tree.truthDecayVtx_y.at(idx)
        lxy = (lx * lx + ly * ly)**0.5
        h_dp_lxy.Fill(lxy)
        h_dp_pt.Fill(tree.truthPt.at(idx)*0.001)
    #print(tree.truthPt.at(idx_dp))

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

canvas.Clear()
canvas.SetLogy(0)
h_dp_lxy.Draw()

# Write the plot to the output plot file
canvas.Print(outputDir + '/dp_lxy.png')

# save the lxy distribution
canvas.Clear()
gStyle.SetOptStat(0)
h_dp_pt.Draw()
canvas.Print(outputDir + '/dp_pt.png')



myfile.Close()
