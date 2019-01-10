import os, sys
from ROOT import TFile, TH1F, TTree

def CraftSampleName(name):
  # Deal with 'ext' in the end
  if   'ext' in name[-3:]: name = name[:-3] + '_' + name[-3:]
  elif 'ext' in name[-4:]: name = name[:-4] + '_' + name[-4:]
  # Rename bits...
  name.replace('madgraphMLM', 'MLM')
  # Delete bits...
  deleteWords = ['13TeV', 'TuneCUETP8M22T4', 'CUETP8M22T4', 'powheg', 'Powheg', 'amcatnloFXFX', 'amcatnlo', 'aMCatNLO', 'pythia8', 'TunCP5']
  s = name.replace('-', '_').split('_')
  a = ''
  for bit in s:
    if s in deleteWords: continue    
    else: a += '_' + bit
  if a.startswith('_'): a = a[1:]
  if a.endswith('_')  : a = a[:-1]
  while '__' in a: a = a.replace('__', '_')
  return a

def haddProduction(dirname, prodname):
  n = len(prodname)
  for path, subdirs, files in os.walk(dirname):
    for s in subdirs:
      if not s.startswith(prodname+'_'): continue
      else:
        treeName = s[n+1:]
        dirName  = path + '/' + s
        sampleName = CraftSampleName(treeName)
        #print 'Looking for ' + treeName + ' in ' + dirName + '...'
        print 'Adding output sample: ', sampleName


haddProduction('prueba', 'jun10')
