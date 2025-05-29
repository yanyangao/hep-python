from ROOT import TFile, TTree, TH1D, gROOT

class sample:

    def __init__(self, name, metadata):

        self.name = name
        self.sampletype = metadata['sampletype']
        self.filepath = metadata['filepath']
        self.treename = metadata['treename']
        self.colour = int(metadata['colour'])
        self.blind = True if metadata['blind'] == 'True' else False
        self.scalefactor = metadata['scalefactor']
        self.includeweights = 1.0 if metadata['includeweights'] == '' else metadata['includeweights']
        self.excludeweights = 1.0 if metadata['excludeweights'] == '' else metadata['includeweights']
        self.unitynorm = True if metadata['unitynorm'] == 'True' else False

    def __gethist__(self, variable, cuts, nominalweights, nbins, xmin, xmax, forcebins):
        
        tempfile = TFile(self.filepath)
        temptree = tempfile.Get(self.treename)
        if self.sampletype != 'data':
            cutstring = '({}) * ({}) * ({}) * ({})'.format(cuts, nominalweights, self.includeweights, self.scalefactor)
        else:
            cutstring = '({}) * ({}) * ({}) * ({})'.format(cuts, 1.0, self.includeweights, self.scalefactor)
        temphistname = 'temphist_{}'.format(self.name)
        if len(forcebins) == 0:
            temphist = TH1D(temphistname,temphistname,nbins,xmin,xmax)
        else:
            numbins = len(forcebins) - 1
            temphist = TH1D(temphistname,temphistname,numbins,forcebins)
        temphist.Sumw2()
        temphist.SetTitle(self.name)
        temptree.Draw('{}>>{}'.format(variable, temphistname),cutstring,'HIST')
        gROOT.cd()
        newhist = temphist.Clone()
        if self.sampletype == 'data':
            newhist.SetMarkerSize(1.5)
        elif self.sampletype == 'background':
            newhist.SetFillColor(self.colour)
        elif self.sampletype == 'signal':
            newhist.SetFillColor(0)
            newhist.SetLineColor(self.colour)   
            newhist.SetLineWidth(2)    
            newhist.SetLineStyle(2)    
        self.hist = newhist   
