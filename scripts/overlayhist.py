#-----------------------
# This example code performs simple analysis based on existing flat ntuple
#-----------------------

from ROOT import TFile, TH1D, TCanvas, gStyle, TLegend
import os
import multiprocessing as mp
from array import array

files = [
        'output/hist-user.csebasti.miniT_01-04_frvz_vbf.500757.root',
        'output/hist-user.csebasti.miniT_01-04_frvz_vbf.500758.root',
        'output/hist-user.csebasti.miniT_01-04_frvz_vbf.500762.root',
        ]
names = [
    'signal 0.1 GeV ee',
    'signal 0.4 GeV incl',
    'signal 15 GeV incl'
    ]

def plot(histname):
    histos = []
    for idx in range(len(files)):
        #print(idx, files[idx], names[idx])
        file = TFile(files[idx]) 
        tempHist = file.Get(histname)
        newHist = tempHist.Clone("histos_"+ str(idx))
        #print(newHist.GetName(), str(newHist.GetBinContent(10)))
        newHist.SetDirectory(0)
        histos.append(newHist)
        file.Close()
   
    canvas = TCanvas("canvas_"+ histname)
    gStyle.SetOptStat(0)
    # Move into the canvas (so anything drawn is part of this canvas)
    canvas.cd()
    # define the location of the legend
    x0, x1, y0, y1 = 0.50, 0.60, 0.50, 0.70
    legend = TLegend(x0,y0,x1,y1) 
    legend.SetBorderSize(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.032)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetLineColor(0)  

    for idx in range(len(files)):
        legend.AddEntry(histos[idx], names[idx], "lp")    
        histos[idx].SetMarkerColor(idx+1)
        histos[idx].SetLineColor(idx+1)
        if idx == 0:    histos[idx].Draw()
        else: histos[idx].Draw("samee")           
    legend.Draw("same")   
    canvas.Print(histname+'.pdf')
    

if __name__=='__main__':
    plot("h1_MET_TrigEff_2017")      
    plot("h1_MET_TrigEff_2018")      
