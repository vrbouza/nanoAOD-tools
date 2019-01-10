import os, sys
from utils import *

def haddForAllProd(dirname, prodname, pretend = False, outdir = './'):
  dirnames, samplenames = haddProduction(dirname, prodname)
  if not pretend:
    print pcol.red + ' STARTING...' + pcol.end
    for i in range(len(dirnames)): haddtrees(dirnames[i], samplenames[i], outdir = outdir)

arguments = sys.argv[1:]
narg = len(arguments)
if narg < 2:
  print ' >> Usage: python inputDir outputName'
  print '    Example:  python nanoAODcrab/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/jun10MC/ TTTo2L2Nu'
  print ' >> Usage: python inputDir --prod prodname '
  print '    Looks for all samples in the production and applies hadd to all'
  print '    Example:  python nanoAODcrab --prod jun10'
  print ''
  print ' ## Options:'
  print '    --pretend'
  print '    --outdir'
else:
  dirname = arguments[0]
  outname = arguments[1]
  prodname = ''
  outdir = './'
  pretend = False
  for i in range(narg):
    if arguments[i] == '--prod' or arguments[i] == '-p': prodname = arguments[i+1]
    if arguments[i] == '--outdir' or arguments[i] == '-o': outdir = arguments[i+1]
    if 'pretend' in arguments[i]: pretend = True
  if prodname == '': haddtrees(dirname, outname, outdir = outdir)
  else: haddForAllProd(dirname, prodname, pretend)

haddtrees('nanoAODcrab/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/jun12_ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/', 'tbarW')

#haddProduction('prueba', 'jun10')
