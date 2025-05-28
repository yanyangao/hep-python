# author yanyan.gao@cern.ch
# adapted from Matt Sullivan's code https://gitlab.cern.ch/msulliva/hep-python

import multiprocessing as mp 
from ROOT import TFile, TTree, TH1D
import os

######### Start of input block

# Define the files to process
# Hint: use ls command first to verify all the files do exist

files = [
    '/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500757.root',
    '/Users/ygao3/atlas_data/DarkPhoton/data/miniT/vbfskim/v02-00/frvz_vbf_500762.root',
] 

# Define the ntuple tree name in each file, the length should match the length of files
trees = ['miniT', 'miniT']

# Given each file a descriptive name, avoid spaces or other special characters 
names = ['signal_100MeV', 'signal_10gev']

# Specify the sequence of selections to be applied, one cut per '' for all samples 
cuts = ['1', '1', 'metTrig', 'MET>225e3', 'neleSignal==0', 'nmuSignal==0', 'hasBjet==0', 'abs(min_dphi_jetmet)>0.4', 'nLJjets20>=1', 'LJjet1_gapRatio>0.9', 'LJjet1_BIBtagger>0.2', 'LJjet1_DPJtagger>0.8', 'LJjet1_DPJtagger<0.9' ]
# Specify the weights to be applied 
weights = ['scale1fb', 'intLumi']

######### End of input block


def setup():

    pool = mp.Pool(len(files))
    results = [pool.apply_async(cutflow, (files[i], trees[i], i)) for i in range(len(files))]
    pool.close()
    pool.join()  

def cutflow(file, tree, index):

    tfile = TFile(file)
    ttree = tfile.Get(tree)

    output_name = 'output_{}.root'.format(names[index].replace(' ','_'))

    weightstring = ''
    for weight in range(len(weights)):
        weightstring += ' {} * '.format(weights[weight])    
    weightstring += ' 1'    

    tfile_out = TFile(output_name, 'recreate')
    histname = 'hist'
    hist = TH1D(histname, histname, len(cuts), 0, len(cuts))
    hist.Sumw2()

    for entry in range(len(cuts)):

        temphistname = "hist_%s" % str(entry)
        temphist = TH1D(temphistname, temphistname, 1,-1000,1000)
        temphist.Sumw2()

        cutstring = ''
        for cut in range(entry+1):
            cutstring += '(' + cuts[cut] + ')' + ' * '   
        cutstring += weightstring 

        ttree.Draw('1>>'+temphistname, cutstring)
        value = temphist.GetBinContent(1)
        error = temphist.GetBinError(1)
        bin = hist.GetBin(entry)
        hist.SetBinContent(bin, value)
        hist.SetBinError(bin, error)
        hist.GetXaxis().SetBinLabel(entry+1, cuts[entry])   
 
    hist.SetTitle(names[index])     
        
    tfile.Close()    
    hist.Write()
    tfile_out.Close()   

if __name__=='__main__':
    setup()            
