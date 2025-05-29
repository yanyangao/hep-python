#
# This example script analyse the hadronic lepton jet reconstruction fake rate
#
import ROOT, os
from ROOT import TFile, TLorentzVector, gStyle, TLegend

# Open the file
path = '/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root'
myfile  = ROOT.TFile.Open(path, "READ")
tree = myfile.Get("miniT")

# Give a descriptive name of output plots directory
# it would create a new directory if this does not exist 
outputDir = "output/plots/"
if not os.path.isdir(outputDir):
    os.makedirs(outputDir)
print("output directory set to be " + outputDir)
 
# define histograms
nbins = 50

h_eta_den = ROOT.TH1D("eta_den","eta_den", nbins, -3, 3)
h_eta_den.SetXTitle("LJjet1_eta")
h_eta_den.Sumw2()

h_eta_num = ROOT.TH1D("FakeRate vs eta","FakeRate vs eta", nbins, -3, 3)
h_eta_den.SetXTitle("LJjet1_eta")
h_eta_num.Sumw2()

h_eta_fake = ROOT.TH1D("h_eta_fake","h_eta_fake", nbins, -3, 3)
h_eta_fake.SetXTitle("LJjet1_eta")
h_eta_fake.Sumw2()

h_phi_den = ROOT.TH1D("phi_den","phi_den", nbins, -4, 4)
h_phi_den.SetXTitle("LJjet1_phi")
h_phi_den.Sumw2()

h_phi_num = ROOT.TH1D("FakeRate vs phi","FakeRate vs phi", nbins, -4, 4)
h_eta_den.SetXTitle("LJjet1_phi")
h_phi_num.Sumw2()

h_phi_fake = ROOT.TH1D("h_phi_fake","h_phi_fake", nbins, -4, 4)
h_phi_fake.SetXTitle("LJjet1_phi")
h_phi_fake.Sumw2()


for entry in range(tree.GetEntries()):

    tree.GetEntry(entry)
    #if entry > 10: continue
    #if tree.eventNumber!=  90487: continue

    # Preselection
    if tree.nLJjets20<1: continue
    if tree.LJjet1_gapRatio < 0.9: continue

    eta = tree.LJjet1_eta
    phi = tree.LJjet1_phi

    h_eta_den.Fill(eta)
    h_phi_den.Fill(phi)

    nPart = tree.truthPdgId.size()
    dp_collection = []
    for index in range(nPart):
        if tree.truthPdgId[index] == 3000001:
            dp_collection.append(index)

    nDP = len(dp_collection)
    #print(dp_collection)
    # skip this event if we do not have any dark photons
    if nDP < 1: continue

    LJ1 = TLorentzVector()
    LJ1.SetPtEtaPhiM(tree.LJjet1_pt, tree.LJjet1_eta, tree.LJjet1_phi, tree.LJjet1_m)
    deltaR = 999
    deltaR_list = []

    for idx in dp_collection:
        dp1 = TLorentzVector()
        dp1.SetPtEtaPhiE(tree.truthPt.at(idx), tree.truthEta.at(idx), tree.truthPhi.at(idx), tree.truthE.at(idx))
        deltaR = dp1.DeltaR(LJ1)
        deltaR_list.append(deltaR)
    deltaR_min = min(deltaR_list)
    #print(tree.eventNumber, deltaR_list, deltaR_min)

    if deltaR_min<0.4:
        h_eta_num.Fill(eta)
        h_phi_num.Fill(phi)
    else:
        print(tree.eventNumber, deltaR_list)



# Fill the fake rate for the dp->LJ match
# set the overflow bin to the last bin of the histogram
lastbin = h_eta_den.GetNbinsX()
overflow = h_eta_den.GetBinContent(lastbin+1)
content_lastbin = h_eta_den.GetBinContent(lastbin)
h_eta_den.SetBinContent(lastbin, content_lastbin + overflow )
h_eta_fake = h_eta_num.Clone()
h_eta_fake.Divide(h_eta_fake, h_eta_den, 1,  1, "B")

lastbin_phi = h_phi_den.GetNbinsX()
overflow_phi = h_phi_den.GetBinContent(lastbin_phi+1)
content_lastbin_phi = h_phi_den.GetBinContent(lastbin_phi)
h_phi_den.SetBinContent(lastbin_phi, content_lastbin_phi + overflow_phi )
h_phi_fake = h_phi_num.Clone()
h_phi_fake.Divide(h_phi_fake, h_phi_den, 1,  1, "B")


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
h_eta_fake.Draw()

# Write the plot to the output plot file
canvas.Print(outputDir + '/FakeRate_eta.pdf')

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
legend.AddEntry(h_eta_den, "Truth DP", 'l')
legend.AddEntry(h_eta_num, "Matched hadronic LJ", 'l')

h_eta_den.SetMinimum(0.1)
h_eta_den.Draw()
h_eta_num.SetLineColor(2)
h_eta_num.Draw("samehist")
legend.Draw("same")

canvas.Print(outputDir + '/eta.pdf')


# phi
canvas.Clear()
gStyle.SetOptStat(0)
h_phi_fake.Draw()

# Write the plot to the output plot file
canvas.Print('FakeRate_phi.pdf')

# save the phi distribution
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
legend.AddEntry(h_phi_den, "Truth DP", 'l')
legend.AddEntry(h_phi_num, "Matched hadronic LJ", 'l')

h_phi_den.SetMinimum(0.1)
h_phi_den.Draw()
h_phi_num.SetLineColor(2)
h_phi_num.Draw("samehist")
legend.Draw("same")

canvas.Print('phi.pdf')


myfile.Close()
