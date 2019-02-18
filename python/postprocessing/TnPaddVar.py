#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from framework.postprocessor import PostProcessor
import json

isData = sys.argv[-1] == 'data'
dataverbose = 'Is data!!' if isData else 'is MC!!'
print dataverbose

jsonInput = ''
year = 17

### INPUT FILE
#filepath = ['/afs/cern.ch/work/j/jrgonzal/public/pruebaNanoAOD/8EAB6B64-9210-E811-B19D-FA163E759AE3.root']
#filepath = ['root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root']
#filepath = ['/nfs/fanae/user/juanr/nanoAOD/CMSSW_9_4_6/src/PhysicsTools/NanoAODTools/python/postprocessing/skimtree.root']
if isData:
  #filepath = ['root://cms-xrd-global.cern.ch//store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/0726FD7F-D51D-4348-8B48-FA2B7D2B403D.root']
  filepath = ['root://cms-xrd-global.cern.ch//store/data/Run2017D/SingleMuon/NANOAOD/Nano14Dec2018-v1/80000/3E9394FA-EC63-114B-8AB1-18BD46BC5D43.root']
  if     year == 18: jsonfile = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-322057_13TeV_PromptReco_Collisions18_JSON.txt'
  elif   year == 17: jsonfile = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
  elif   year == 16: jsonfile = ''
  jsn = open(jsonfile, 'r')
  jsonInput = json.loads(jsn.read())
  jsn.close()
  jsn = open(jsonfile, 'r')
  jsonInput = json.loads(jsn.read())
  jsn.close()
  print 'Using json: ', jsonfile

else: 
  filepath = ['root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/20000/CCF670CF-51AD-FA46-8EEF-A10CE19C3474.root']

### OUTPUT
outdir = '.'

### SKIM 
cut = 'nMuon >= 2 && Muon_pt[0] > 25 && Muon_pt[1] >= 12 && Jet_pt > 200'#(nElectron + nMuon) >= 2 && Jet_pt > 200' # nGenDressedLepton >= 2

### SLIM FILE
slimfile = "SlimFileTnP.txt"

### MODULES
### Include modules to compute derivate quantities or calculate uncertainties
from modules.jme.jetmetUncertainties import *
from modules.common.puWeightProducer import *
from modules.skimNRecoLeps import *
from modules.addTnPvarMuon import *
#from modules.addSUSYvar import *
#mod = [puAutoWeight(), skimRecoLeps(), addSUSYvarsMC()] # countHistogramsProducer(), jetmetUncertainties2017All()
mod = [puAutoWeight(), addTnPMuon()] if not isData else [addTnPMuon()]# countHistogramsProducer(), jetmetUncertainties2017All()

p=PostProcessor(outdir,filepath,cut,slimfile,mod,provenance=True,outputbranchsel=slimfile,jsonInput = jsonInput)
p.run()
