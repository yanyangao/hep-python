from ROOT import TFile, TH1D
import os

def maketable():

    # Output file
    output = open('table.txt','w+')

    # Files
    files = []
    for file in os.listdir('.'):
        if '.root' in file:
            files.append(file)
    files=sorted(files)
    # Cuts        
    cuts = []
    file0 = TFile(files[0])
    hist0 = file0.Get('hist')
    for entry in range(1,hist0.GetNbinsX()+1):
        cuts.append(hist0.GetXaxis().GetBinLabel(entry))
    # Make table    
    output.write('\\begin{table}\n')
    output.write('\\centering\n')
    output.write('\\tiny\n')
    tabdimensions = '{c|'
    for file in files:
        tabdimensions += 'c'
    output.write('\\begin{{tabular}}{}}}\n'.format(tabdimensions))    
    output.write('\\hline\n')
    samplenames = 'Cuts '
    for file in files:
        samplenames += ' & {} '.format(file.split('output_')[1].split('.root')[0].replace('_', '\\_'))
    samplenames += '\\\\ \\hline \n'    
    output.write(samplenames)    
    for cut in range(1,len(cuts)):
        line = ''
        line += cuts[cut]
        for file in files:
            line += ' & '
            tempfile = TFile(file)
            temphist = tempfile.Get('hist')
            nevts = temphist.GetBinContent(cut)
            nerr = temphist.GetBinError(cut)
            str_yield = str(round(nevts,1))
            str_err = str(round(nerr,1))
            if nevts > 1e4 or nevts < 0.1:
                str_yield = "{:.1e}".format(nevts) 
                str_err = "{:.1e}".format(nerr) 
            line += str_yield 
            line += ' $\\pm$ '
            line += str_err 
        line += '\\\\ \n'    
        output.write(format(line))
    output.write('\\hline\n')  
    output.write('\\end{tabular}\n')
    output.write('\\end{table}\n')

def format(line):

    line = line.replace('_','\\_')
    line = line.replace('>=', ' $\\geq$ ')
    line = line.replace('<=', ' $\\leq$ ')
    line = line.replace('>', ' $>$ ')
    line = line.replace('<', ' $<$ ')
    line = line.replace('!=', ' $\\neq$ ')
    return line


if __name__=='__main__':
    maketable()    
