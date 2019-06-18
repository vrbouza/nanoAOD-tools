#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from framework.postprocessor import PostProcessor

isData = sys.argv[-1] == 'data'

### INPUT FILE
#filepath = ['/afs/cern.ch/work/j/jrgonzal/public/pruebaNanoAOD/8EAB6B64-9210-E811-B19D-FA163E759AE3.root']
filepath = ['root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root']
#filepath = ['root://cms-xrd-global.cern.ch//store/data/Run2017B/DoubleMuon/NANOAOD/Nano14Dec2018-v1/280000/FB901F01-98AA-214F-A2C2-D67630861952.root']
#filepath = ['/nfs/fanae/user/juanr/nanoAOD/CMSSW_9_4_6/src/PhysicsTools/NanoAODTools/python/postprocessing/skimtree.root']

### OUTPUT
outdir = '.'

### SKIM 
cut = '(nElectron + nMuon) >= 2 && Jet_pt > 200' # nGenDressedLepton >= 2

### SLIM FILE
slimfile = "SlimFile.txt"
jecfile  = "Autumn18_V8_MC"

### MODULES
### Include modules to compute derivate quantities or calculate uncertainties
from modules.jme.jetmetUncertainties import *
from modules.common.puWeightProducer import *
from modules.skimNRecoLeps import *
from modules.jme.jetRecalib import *
#from modules.addSUSYvar import *
#mod = [puAutoWeight(), skimRecoLeps(), addSUSYvarsMC()] # countHistogramsProducer(), jetmetUncertainties2017All()
mod = [puAutoWeight(), skimRecoLeps(), jetRecalib(jecfile)] # countHistogramsProducer(), jetmetUncertainties2017All()

p=PostProcessor(outdir,filepath,cut,slimfile,mod,provenance=True,outputbranchsel=slimfile)
p.run()
