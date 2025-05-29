import ROOT, json, sys
from ROOT import TLegend, gROOT, TFile, TH1D, THStack, TPad, TArrow, TLine
import numpy as np
import io

import sample

class plotutils:

    def setuplegend(self, x0 = 0.65, y0 = 0.7, x1 = 0.88, y1 = 0.88):

        legend = TLegend(x0,y0,x1,y1) 
        legend.SetBorderSize(0)
        legend.SetTextFont(42)
        legend.SetTextSize(0.032)
        legend.SetFillColor(0)
        legend.SetFillStyle(0)
        legend.SetLineColor(0)  
        self.legend = legend
        return   

    def drawATLASlabel(self, level = 'Internal', region = '', levelposition = 0.29):

        if self.doratio == True:
            levelposition = 0.25

        latexObject = ROOT.TLatex()
        latexObject.SetTextSize(0.05)
        latexObject.SetTextFont(72)
        latexObject.DrawLatexNDC(0.16, 0.83, 'ATLAS')
        latexObject.SetTextSize(0.045)
        latexObject.SetTextFont(42)  
        latexObject.DrawLatexNDC(levelposition, 0.83, level)  
        latexObject.SetTextSize(0.04) 
        latexObject.SetTextFont(42)  
        latexObject.DrawLatexNDC(0.16, 0.78, region) 
        return

    def backgrounds(self, tempbackgrounds):

        # Order backgrounds in terms of contribution to region
        tempbackgrounds = self.sortsamples(tempbackgrounds)

        # Setup stack
        thstack = THStack('thstack','')
        if self.ymax != 0:
            thstack.SetMaximum(self.ymax)
        if self.ymin != 0:    
            thstack.SetMinimum(self.ymin)

        # Setup total SM
        if self.forcebins == []:
            totalSM = TH1D('totalSM','totalSM',self.nbins,self.xmin,self.xmax)
        else:
            numbins = len(self.forcebins) - 1
            totalSM = TH1D('totalSM','totalSM',numbins,self.forcebins)

        totalSM.Sumw2()

        totalSM.SetMarkerSize(0.00001)
        totalSM.SetFillStyle(3004)
        totalSM.SetFillColor(1) 
        
        # Construct stack of backgrounds and total background sample
        temperror = 0.0
        for background in tempbackgrounds:
            self.samples[background.name] = background.hist
            if background.blind == False:
                if background.unitynorm == True:
                    background.hist.Scale(1/background.hist.Integral())
                thstack.Add(background.hist)
                if len(self.bkgerrors) == 0:
                    totalSM.Add(background.hist)
                else:
                    for bin in range(background.hist.GetNbinsX()):
                        totalSM.AddBinContent(bin+1, background.hist.GetBinContent(bin+1))
                legendentry = background.name
                if background.scalefactor != 1.0:
                    legendentry = '({}x) {}'.format(background.scalefactor, background.name)
                self.legend.AddEntry(background.hist, legendentry, 'f')   

        if len(self.bkgerrors) != 0:
            for bin in range(totalSM.GetNbinsX()):
                totalSM.SetBinError(bin+1, self.bkgerrors[bin])
                print('Bin {} error = {}'.format(bin+1, self.bkgerrors[bin]))                 

        self.samples['totalSM'] = totalSM
        #self.samples['totalSMerror'] = totalSMerror

        self.backgroundstack = thstack
        self.totalSM = totalSM   
        #self.totalSMerror = totalSMerror
        #print('Background yield: {}'.format(totalSM.Integral()))
        gROOT.cd()
        return   

    def signals(self, tempsignals):

        # Plot individual signal samples
        for signal in tempsignals:
            self.samples[signal.name] = signal.hist
            if signal.unitynorm == True:
                signal.hist.Scale(1/signal.hist.Integral())
            if self.plotsignals == True:
                legendentry = signal.name
                if signal.scalefactor != 1.0:
                    legendentry = '({}x) {}'.format(signal.scalefactor, signal.name)
                self.legend.AddEntry(signal.hist, legendentry, 'l')
                
        self.signals = tempsignals  
        #self.signalratio = tempsignals[0]      

    def data(self, tempdata):

        for data in tempdata:
            if data.blind == False and self.forceblind == False:
                if data.unitynorm == True:
                    data.hist.Scale(1/data.hist.Integral())
                self.legend.AddEntry(data.hist, data.name, 'PE') 
                self.samples[data.name] = data.hist
                print('Data yield: {}'.format(data.hist.Integral())) 

        self.data = tempdata    
        return    

    def setup(self, canvas, files, regions_file, variable, variablename, units, region, weights, nbins, xmin, xmax, ymin, ymax, plotlog, plotsignals, plotarrows, forceblind, useregionbins):

        self.xmax = xmax
        self.xmin = xmin
        self.ymax = ymax
        self.ymin = ymin
        self.nbins = nbins
        self.variable = variable
        self.variablename = variablename
        self.units = units
        self.plotsignals = False if plotsignals == 0 else True
        self.plotarrows = plotarrows
        self.useregionbins = False if useregionbins == 0 else True
        self.samples = {}
        self.lines = {}
        self.lineerrors = {}
        self.ratio = {}
        self.ratioerror = {}
        cuts, self.forceblind, forcebins, bkgerrors = self.loadregions(regions_file, region)
        print('Region blinded: {}'.format(self.forceblind))   
        if len(forcebins) != 0 and useregionbins:
            from array import array
            forcebins = map(float, forcebins.replace(' ', '').split(','))
            self.forcebins = array('f',forcebins)
            if len(bkgerrors) != 0:
                print('Using following per-bin errors: {}'.format(bkgerrors))
                bkgerrors = map(float, bkgerrors.replace(' ', '').split(','))
                self.bkgerrors = array('f',bkgerrors)
            else:
                self.bkgerrors = []
        else:
            self.forcebins = [] 
            self.bkgerrors = [] 
        tempbackgrounds, tempsignals, tempdata = self.loadsamples(files)
        self.applyselections(tempbackgrounds, tempsignals, tempdata, variable, cuts, weights, nbins, xmin, xmax, self.forcebins)
        self.backgrounds(tempbackgrounds)
        self.signals(tempsignals)
        self.data(tempdata)    
        
    def drawhists(self):
        
        self.backgroundstack.Draw('HIST')
        self.totalSM.Draw('E2 SAME') 
        for data in self.data:
            if (data.blind == False and self.forceblind == False):
                data.hist.Draw('HIST SAME EP X0') 
            else:
                print ('Data blinded')   
        for signal in self.signals:
            if self.plotsignals == True: 
                signal.hist.Draw('HIST SAME')
            else:
                print('Signals not plotted')         
                
    def fit(self, sample):
        from ROOT import TF1
        gaus = TF1('fit','gaus')
        self.data[0].hist.Fit(gaus)
            #gaus.SetLineColor(2)
            #gaus.SetLineStyle(1)
        self.gausfit = gaus
        self.gausfit.Draw('LSAME')

    def decorate(self, ATLASlabel, regionlabel):

        #variablename = self.variable.split('*')[0]
        variablename = self.variablename
        if self.units == '':
            xlabel = '{}'.format(self.variable)
            ylabel = 'Events'.format(variablename, self.units)
        else:
            binspacing = round((self.xmax - self.xmin)/self.nbins)
            xlabel = '{} [{}]'.format(variablename, self.units)
            ylabel = 'Events / {} {}'.format(binspacing, self.units)
            #ylabel = 'Events'
        self.backgroundstack.GetXaxis().SetTitle(xlabel)
        self.backgroundstack.GetYaxis().SetTitle(ylabel)
        self.backgroundstack.GetYaxis().SetTitleOffset(1)
        if self.doratio == True:
            self.ratioplot.GetXaxis().SetTitle(xlabel)
            self.pad1.cd()
        self.drawATLASlabel(level = ATLASlabel, region = regionlabel)           

    def plotdatamcratio(self, ratiomin, ratiomax, numerator, denominator):

        self.pad2.cd()

        #if self.forceblind == False:
        #    ratioplot = self.samples[numerator].Clone()
        #else:
        #    print('Region is blinded, numerator = denominator!')
        #    ratioplot = self.samples[denominator].Clone()    
        #denominator_hist = self.samples[denominator].Clone()
        #ratioplot.Divide(denominator_hist)

        histname = 'datamc'
        errorname = 'datamcerror'
        if self.forcebins == []:
            ratioplot = TH1D(histname,histname,self.nbins,self.xmin,self.xmax)
            errorhist = TH1D(errorname,errorname,self.nbins,self.xmin,self.xmax)
        else:
            numbins = len(self.forcebins) - 1
            ratioplot = TH1D(histname,histname,numbins,self.forcebins)
            errorhist = TH1D(errorname,errorname,numbins,self.forcebins)
        ratioplot.Sumw2() 
        for bin in range(1,ratioplot.GetNbinsX()+1):
            binnum = self.samples[numerator].Clone().GetBinContent(bin)
            binden = self.samples[denominator].Clone().GetBinContent(bin)
            numerror = self.samples[numerator].Clone().GetBinError(bin)
            denerror = self.samples[denominator].Clone().GetBinError(bin)
            if binnum != 0 and binden != 0:
                ratio = binnum/binden
                #ratioerror = np.sqrt((numerror/binnum)**2 + (denerror/binden))
                ratioerror = denerror/binden
            else:
                ratio = 0    
                ratioerror = 0
            ratioplot.SetBinContent(bin, ratio)
            ratioplot.SetBinError(bin, ratioerror)
            errorhist.SetBinContent(bin, 1.0)
            errorhist.SetBinError(bin, ratioerror)
            ratioplot.SetMarkerColorAlpha(1,1)
            ratioplot.SetFillColor(0)
            ratioplot.SetLineColor(0)
            ratioplot.SetLineWidth(2)
            errorhist.SetFillColor(1)
            errorhist.SetFillStyle(3013)
            errorhist.SetMarkerColorAlpha(0,0)
            self.ratio['ratio'] = ratioplot
            self.ratioerror['ratioerror'] = errorhist
            self.ratioplot = ratioplot
        
        #ratioplot.SetFillColor(2)
        #ratioplot.SetFillStyle(3004)

        self.ratio['ratio'].Draw('HIST P')
        self.ratioerror['ratioerror'].Draw('E2 SAME')
        self.ratio['ratio'].GetYaxis().SetNdivisions(3,6,0)
        self.ratio['ratio'].SetMaximum(ratiomax)
        self.ratio['ratio'].SetMinimum(ratiomin)
        self.ratio['ratio'].GetYaxis().SetTitle('{} / {}'.format(numerator, denominator))
        self.ratio['ratio'].SetTitleOffset(1.2,'X')
        self.ratio['ratio'].SetTitleOffset(0.4,'Y')
        self.ratio['ratio'].SetTitleSize(0.12,'X')
        self.ratio['ratio'].SetTitleSize(0.10,'Y')
        self.ratio['ratio'].SetLabelSize(0.12,'X')
        self.ratio['ratio'].SetLabelSize(0.12,'Y')
        self.ratio['ratio'].SetMarkerColor(1)

        for bin in range(self.ratio['ratio'].GetNbinsX()):
            print('Bin {}, {}, {}'.format(bin, self.ratio['ratio'].GetBinCenter(bin), self.ratio['ratio'].GetBinError(bin)))

        centreline = TLine(self.xmin,1,self.xmax,1)
        centreline.SetLineWidth(1)
        centreline.SetLineStyle(2)
        centreline.DrawLine(self.xmin,1,self.xmax,1)

        if self.plotarrows == True:

            for bin in range(1,ratioplot.GetNbinsX()+1):
                if self.ratio['ratio'].GetBinContent(bin) > ratiomax:
                    binx = self.ratio['ratio'].GetBinCenter(bin)
                    arrow = TArrow(binx, ratiomax-(ratiomax-ratiomin)*0.25, binx, ratiomax, 0.02, "|>")
                    arrow.DrawArrow(binx, ratiomax-(ratiomax-ratiomin)*0.25, binx, ratiomax, 0.02)
                if self.ratio['ratio'].GetBinContent(bin) < ratiomin:
                    binx = self.ratio['ratio'].GetBinCenter(bin)
                    arrow = TArrow(binx, ratiomin, binx, ratiomin+((ratiomax-ratiomin)*0.25), 0.02, "<|")
                    arrow.DrawArrow(binx, ratiomin, binx, ratiomin+((ratiomax-ratiomin)*0.25), 0.02)                  

    def plotratioline(self, ratiomin, ratiomax, numerator, denominator, colour):

        self.pad2.cd()

        nlines = len(numerator)
        if len(denominator) != len(numerator):
            print('Plotting ratio lines requires equal numbers of numerators and denominators!')   

        index = 0
        for num, den in zip(numerator,denominator):

            histname = 'temphist{}'.format(index)
            errorname = 'errorhist{}'.format(index)

            if self.forcebins == []:
                temphist = TH1D(histname,histname,self.nbins,self.xmin,self.xmax)
                errorhist = TH1D(errorname,errorname,self.nbins,self.xmin,self.xmax)
            else:
                numbins = len(self.forcebins) - 1
                temphist = TH1D(histname,histname,numbins,self.forcebins)
                errorhist = TH1D(errorname,errorname,numbins,self.forcebins)
            temphist.Sumw2()    
            for bin in range(temphist.GetNbinsX()):
                binnum = self.samples[num].Clone().GetBinContent(bin)
                binden = self.samples[den].Clone().GetBinContent(bin)
                numerror = self.samples[num].Clone().GetBinError(bin)
                denerror = self.samples[den].Clone().GetBinError(bin)
                if binnum != 0 and binden != 0:
                    ratio = binnum/binden
                    ratioerror = np.sqrt((numerror/binnum)**2 + (denerror/binden))
                else:
                    ratio = 0    
                    ratioerror = 0
                temphist.SetBinContent(bin, ratio)
                temphist.SetBinError(bin, ratioerror)
                errorhist.SetBinContent(bin, 1.0)
                errorhist.SetBinError(bin, ratioerror)
                temphist.SetMarkerColorAlpha(0,0)
                temphist.SetFillColor(0)
                temphist.SetLineColor(colour[index])
                temphist.SetLineWidth(2)
                errorhist.SetFillColor(colour[index])
                errorhist.SetFillStyle(3013)
                errorhist.SetMarkerColorAlpha(0,0)

            self.lines['line{}'.format(index)] = temphist
            self.lineerrors['line{}'.format(index)] = errorhist
            index += 1 

        for index,line in enumerate(self.lines):
            if index == 0:
                self.ratioplot = self.lines[line]
                self.lines[line].Draw('HIST')
                self.lineerrors[line].Draw('E2 SAME')
            else:
                self.lines[line].Draw('HIST SAME') 
                #self.lines[line].Draw('E2 SAME')   


        self.ratioplot.GetYaxis().SetNdivisions(3,6,0)
        self.ratioplot.SetMaximum(ratiomax)
        self.ratioplot.SetMinimum(ratiomin)
        self.ratioplot.GetYaxis().SetTitle('Ratio')
        self.ratioplot.SetTitleOffset(1.2,'X')
        self.ratioplot.SetTitleOffset(0.4,'Y')
        self.ratioplot.SetTitleSize(0.12,'X')
        self.ratioplot.SetTitleSize(0.10,'Y')
        self.ratioplot.SetLabelSize(0.12,'X')
        self.ratioplot.SetLabelSize(0.12,'Y')

        centreline = TLine(self.xmin,1,self.xmax,1)
        centreline.SetLineWidth(1)
        centreline.SetLineStyle(2)
        centreline.DrawLine(self.xmin,1,self.xmax,1)                                

        #ploterrors = True
        #if ploterrors == True:
        #    errorband = ratioplot.Clone()
        #    for bin in range(errorband.GetNbinsX()):
        #        errorband.SetBinContent(bin,1.0)####

        #    errorband.SetMarkerColorAlpha(0,0.0)
        #    errorband.SetFillColor(1)
        #    errorband.SetFillStyle(3004)
        #    print(errorband.Integral())
        #    self.errorband = errorband
        #    errorband.Draw('E2 SAME')        

    def setuppad(self, plotlog, ratio = ''):

        if ratio == '':

            pad1 = TPad('pad1','pad1',0,0,1,1)
            pad1.Draw()
            pad1.SetBottomMargin(0.15)
            pad1.SetLeftMargin(0.12)
            pad1.SetRightMargin(0.1)
            pad1.cd() 
            if plotlog == True:
                pad1.SetLogy()
            self.doratio = False
            self.pad1 = pad1
            self.pad2 = pad1
            
        elif ratio != '':
            
            pad1 = TPad('pad1','pad1',0,0.3,1,1)
            pad2 = TPad('pad2','pad2',0,0.02,1,0.3)
            pad1.Draw()
            pad2.Draw()
            pad1.SetBottomMargin(0.0)
            pad2.SetBottomMargin(0.4)
            pad1.SetLeftMargin(0.12)
            pad2.SetLeftMargin(0.12)
            pad1.SetRightMargin(0.1)
            pad2.SetRightMargin(0.1)
            pad2.SetTopMargin(0.04)
            pad1.cd()   
            if plotlog == True:
                pad1.SetLogy()
            self.doratio = True
            self.pad1 = pad1
            self.pad2 = pad2
            
    def loadsamples(self, files):
        
        rawjsonfile = io.open(files, encoding='utf-8')
        jsondict = json.load(rawjsonfile)
        files = jsondict.get('files')

        tempbackgrounds = []
        tempsignals = []
        tempdata = []

        for file, metadata in files.items():
            tempsample = sample.sample(file, metadata)
            if metadata["sampletype"] == 'data':
                tempdata.append(tempsample)
            elif metadata["sampletype"] == 'background':
                tempbackgrounds.append(tempsample)
            elif metadata["sampletype"] == 'signal':     
                tempsignals.append(tempsample) 
                
        return tempbackgrounds, tempsignals, tempdata

    def loadregions(self, cuts_file, region):

        rawjsonfile = io.open(cuts_file, encoding='utf-8')
        jsondict = json.load(rawjsonfile)
        regions = jsondict.get('regions')
        tempcuts = ''
        if region not in regions:
            sys.exit('Region not found, please check and try again.')
        else:    
            tempcuts = regions[region]['cuts']
            if regions[region]['blinding_cuts'] != '' and regions[region]['blind'] == 'False':
                tempcuts += ' * {}'.format(regions[region]['blinding_cuts'])
            blind = True if regions[region]['blind'] == 'True' else False
            forcebins = regions[region]['forcebins']
            bkgerrors = regions[region]['bkgerrors']
            return tempcuts, blind, forcebins, bkgerrors                  

    def applyselections(self, tempbackgrounds, tempsignals, tempdata, variable, cuts, weights, nbins, xmin, xmax, forcebins):

        for background in tempbackgrounds:
            background.__gethist__(variable, cuts, weights, nbins, xmin, xmax, forcebins)
            
        for signal in tempsignals:
            signal.__gethist__(variable, cuts, weights, nbins, xmin, xmax, forcebins)
            
        for data in tempdata:
            data.__gethist__(variable, cuts, weights, nbins, xmin, xmax, forcebins)         

    def sortsamples(self, samples):
        
        temphists = []
        tempyields = []

        for sample in samples:

            temphist = sample.hist
            tempyields.append(temphist.Integral())

        tempyields.sort()
        
        for tempyield in tempyields:

            for sample in samples:

                temphist = sample.hist
                if temphist.Integral() == tempyield:

                    temphists.append(sample)

        return temphists    
        
        
