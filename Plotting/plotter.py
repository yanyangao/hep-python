import ROOT, argparse
from ROOT import TFile, TTree, TH1D, TCanvas, THStack, gROOT, TLegend, TPad, TLine, TArrow

import os
import sample
import plotutils as plotutils

class plotter:

    def __init__(self):

        self.REGIONS_FILE = 'regions.json'

        # NORMALISATIONS
        #self.MCWEIGHTSTRING = 'xsec * lumi * WeightEvents * WeightSF_e * WeightSF_mu * WeightEventsSherpa * WeightPileUp * jvfSF * PassTruthMetFilter * WeightTrigger_DiLep * (1./SumOfWeights)'
        self.MCWEIGHTSTRING = '1'
        self.DATAWEIGHTSTRING = '1'   

        # SETTINGS

        self.ATLASLABEL = 'Internal'
        self.PLOTLOG = True
        self.PLOTSIGNALS = True
        self.PLOTARROWS = True
        self.blind = False 
        self.RATIOMIN = 0.0
        self.RATIOMAX = 10.0

    def run(self):

        # Set ATLAS style
        gROOT.LoadMacro("ATLAS_Style/atlasstyle-00-03-05/AtlasStyle.C")
        gROOT.LoadMacro("ATLAS_Style/atlasstyle-00-03-05/AtlasUtils.C")
        ROOT.SetAtlasStyle() 
        gROOT.SetBatch()

        # Run plotting
        #def newplot(self, files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 0, PLOTSIGNALS = False, ratioplot = '',forcebins=False, plotLOG=True):
        inputfile = 'files_local_yanyan.json' 
        plotSignal = True 
        ratio_string  = ''

        self.newplot(inputfile, 'mjj*0.001', 'm_{jj}', 'GeV','vbffilter',25,0,5000,1E-4,10, True,'', False, True)
        self.newplot(inputfile,'jet1_pt*0.001','Leading jet pT','GeV','vbffilter',25,0,500,1E-4,10,True,'',False, True)
        self.newplot(inputfile,'jet2_pt*0.001','Subleading jet pT', 'GeV','vbffilter',25,0,500,1E-4,10,True,'', False, True)
        self.newplot(inputfile,'jet1_eta','Leading jet #eta','','vbffilter',25,-5.,5,0,0.2,True,'', False, False)
        self.newplot(inputfile,'jet2_eta','Subleading jet #eta', '','vbffilter',25,-5.,5,0,0.2,True,'', False, False)
        self.newplot(inputfile,'detajj','|#Delta#eta_{jj}|','','vbffilter',25,3,8,0,0.2,True,'', False, False)
        self.newplot(inputfile,'dphijj','|#Delta#phi_{jj}|','','vbffilter',20,0,3.2,0,0.4,True,'', False, False)
        self.newplot(inputfile,'MET*0.001','MET','GeV','vbffilter',25,0,500,1e-4,10,True,'', False, True)
        self.newplot(inputfile,'dphi_j1met','|#Delta#phi_{j_1, MET}|','','vbffilter',25,0,3.2,0,0.3,True,'', False, False)
        self.newplot(inputfile,'min_dphi_jetmet','min #DeltaPhi_{j<=4}','','vbffilter',25,0,3.2,1E-4,10,True,'', False, True)
        self.newplot(inputfile,'nLJ20','Number of DPJ','','vbffilter',5,-0.5,4.5,0,1.2,True,'', False, False)
        self.newplot(inputfile,'nLJjets20','Number of had-DPJ','','vbffilter',5,-0.5,4.5,0,1.2,True,'', False, False)
        self.newplot(inputfile,'nLJmus20','Number of #mu-DPJ','','vbffilter',5,-0.5,4.5,0,1.2,True,'', False, False)

    def newplot(self, files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 0, PLOTSIGNALS = False, ratioplot = '',forcebins=False, plotLOG=True):
      
        # Create directory for plots
        if region not in os.listdir('./'):
            os.system('mkdir ./{}'.format(region))

        # Create instance of plot utils
        pu = plotutils.plotutils()

        # Setup canvas
        c = TCanvas('c','c',800,600)
        # Setup TLegend
        pu.setuplegend(y0 = 0.6)

        # Setup TPad
        pu.setuppad(plotLOG, ratioplot)

        # Setup plotutils
        if ('SR' in region or 'sr' in region or 'Sr' in region):
            forceblind = True
        else:
            forceblind = False

        pu.setup(c, files, self.REGIONS_FILE, variable, variablename, units, region, self.MCWEIGHTSTRING, nbins, xmin, xmax, ymin, ymax, self.PLOTLOG, PLOTSIGNALS, self.PLOTARROWS, forceblind, forcebins)
        # Draw histograms
        pu.drawhists()
        #pu.fit('Data')

        # Draw legend
        pu.legend.Draw()

        # Do ratio plot
        if ratioplot != '':
            pu.plotdatamcratio(self.RATIOMIN, self.RATIOMAX, ratioplot.split(':')[0], ratioplot.split(':')[1])
            #pu.plotratioline(self.RATIOMIN, self.RATIOMAX, ['Data'], ['totalSM'], [1])
            #pu.plotratioline(self.RATIOMIN, self.RATIOMAX, ['single top'], ['Z+jets'],3,False)

        # Draw axis labels and ATLAS label    
        pu.decorate(self.ATLASLABEL, region)

        # Name output file
        suffix = ''
        if ratioplot != '':
            suffix = '_{}'.format(ratioplot)  
        filename_pdf = '{}_{}{}.pdf'.format(variable.split('*')[0], region, suffix)
        filename_png = '{}_{}{}.png'.format(variable.split('*')[0], region, suffix)
        c.SaveAs(filename_pdf)
        c.SaveAs(filename_png)

        # Move output file to region folder
        os.system('mv {} {}'.format(filename_pdf, region))
        os.system('mv {} {}'.format(filename_png, region))

if __name__=='__main__':
    plotter().run()    
