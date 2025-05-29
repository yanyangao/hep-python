'''
    This script saves and compares ROC curves 
    Run by
        python3 roc_comparison.py  -o roc_output/
Not fully working
'''
__author__ = "Yanyan Gao"
__doc__ = ""

# IMPORTS ===========================================================================================================
import numpy as np
from ROOT import TMVA as tmva
from ROOT import TFile, TTree, TH1F, TGraph, TCanvas, TLegend, kBlue, kRed, kBlack, kGreen
from array import array
import argparse

sig_filename = "output/frvz_vbf_500757.root"
bkg_filename = "output/qcd.root"

def get_roc(x, y, sig_filename, bkg_filename, treename, cut_string, weight_string, variable_name, nBins, xMin, xMax, left_cut=False):

    full_cut_string = '(' + weight_string + ')*(' + cut_string + ')' 
    # Process signal
    sig_tfile = TFile.Open(sig_filename, "READ")
    sig_ttree = sig_tfile.Get(treename)
    print('Signal has ' + str(sig_ttree.GetEntries()) + ' entries')

    h_sig_name = 'h_sig_' + variable_name
    if '(' in variable_name:
        h_sig_name = h_sig_name.replace('(', '_')
    if ')' in variable_name:
        h_sig_name = h_sig_name.replace(')', '')
    h_sig = TH1F(h_sig_name, h_sig_name, nBins, xMin, xMax)
    h_sig.Sumw2()
    h_sig.SetXTitle(variable_name)
 
    draw_string = variable_name + '>>' + h_sig_name
    print(draw_string, full_cut_string)
    sig_ttree.Draw(draw_string, full_cut_string)
    #print(h_sig.Integral())

    for bin in range(nBins):
        eff = h_sig.Integral(bin, nBins+1) / h_sig.Integral(0, nBins+1)
        if left_cut:
            eff = h_sig.Integral(0, bin) / h_sig.Integral(0, nBins+1)
        #print(bin, h_sig.GetBinContent(bin), eff)
        x.append(eff)
    sig_tfile.Close()

    # Process background 
    bkg_tfile = TFile.Open(bkg_filename, "READ")
    bkg_ttree = bkg_tfile.Get(treename)
    print('Background has ' + str(bkg_ttree.GetEntries()) + ' entries')

    h_bkg_name = 'h_bkg_' + variable_name
    if '(' in variable_name:
        h_bkg_name = h_bkg_name.replace('(', '_')
    if ')' in variable_name:
        h_bkg_name = h_bkg_name.replace(')', '')
 
    h_bkg = TH1F(h_bkg_name, h_bkg_name, nBins, xMin, xMax)
    h_bkg.Sumw2()
    h_bkg.SetXTitle(variable_name)
 
    draw_string = variable_name + '>>' + h_bkg_name
    #print(draw_string, full_cut_string)
    bkg_ttree.Draw(draw_string, full_cut_string)
    #print(h_bkg.Integral())

    for bin in range(nBins):
        eff = h_bkg.Integral(bin, nBins+1) / h_bkg.Integral(0, nBins+1)
        if left_cut:
            eff = h_bkg.Integral(0, bin) / h_bkg.Integral(0, nBins+1)
        #print(bin, h_bkg.GetBinContent(bin), eff)
        y.append(1-eff)
    bkg_tfile.Close()

def setstyle(gr, name, color):
    gr.SetTitle('ROC curve')
    graph_name = name
    if '(' in graph_name:
        graph_name = graph_name.replace('(', '_')
    if ')' in graph_name:
        graph_name = graph_name.replace(')', '')
    gr.SetName(graph_name)
    gr.GetXaxis().SetRangeUser(0,1)
    gr.GetXaxis().SetTitle("Signal Efficiency")
    gr.GetYaxis().SetRangeUser(0,1)
    gr.GetYaxis().SetTitle("Background Rejection")
    gr.SetLineWidth(2)
    gr.SetLineColor(color)
    gr.SetMarkerColor(color)

def main():

    parser = argparse.ArgumentParser(description='ROC curve analysis script')
    parser.add_argument('-o', action="store", dest="op_dir", default="output")

    args = parser.parse_args()

    treename = "miniT"
    weight_string = 'scale1fb'
    cut_string = 'nLJjets>0&&LJjet1_pt>20e3&&LJjet1_gapRatio>0.9'

    # roc curve for two variables
    nbins = 200
    var1 = 'VBF_BDT';  x1_min = -1;     x1_max = 1
    x_var1, y_var1 = array( 'd' ), array( 'd' )
    get_roc(x_var1, y_var1, sig_filename, bkg_filename, treename, cut_string, weight_string, var1, nbins, x1_min, x1_max) 
    var2 = 'dphijj';  x2_min = -3.2;     x2_max = 3.2
    x_var2, y_var2 = array( 'd' ), array( 'd' )
    get_roc(x_var2, y_var2, sig_filename, bkg_filename, treename, cut_string, weight_string, var2, nbins, x2_min, x2_max)


    # create new file to store the ROC curves 
    os.system('mkdir -p ' + args.op_dir)
    op_tfile = TFile(args.op_dir +"/roc_curve.root", "recreate")

    # create graph for LJjet1 BDT
    gr_var1 = TGraph( len(x_var1), x_var1, y_var1 )
    setstyle(gr_var1, 'var1',  kBlack)
    gr_var1.Write()

    # create graph for LJjet1 CNN
    gr_var2 = TGraph( len(x_var2), x_var2, y_var2 )
    setstyle(gr_var2, 'var2',  kRed)
    gr_var2.Write()

    # make overlay plots 
    canvas = TCanvas( 'canvas', 'ROC curve')
    gr_var2.Draw()
    gr_var1.Draw("same")

    # define the location of the legend
    x0, x1, y0, y1 = 0.20, 0.60, 0.30, 0.60
    legend = TLegend(x0,y0,x1,y1) 
    legend.SetBorderSize(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.04)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetLineColor(0)  
    legend.AddEntry(gr_var2, var2,  'l')
    legend.AddEntry(gr_var1, var1, 'l')
    legend.Draw()

    canvas.SaveAs(args.op_dir + '/roc_curve.png')

    op_tfile.Close()


if __name__ == '__main__':
    main()
