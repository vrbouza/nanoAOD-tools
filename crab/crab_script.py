#!/usr/bin/env python
import os, sys, json
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

### SKIM 
#cut = 'Jet_pt > 200 && (nElectron + nMuon) >= 2 && nGenDressedLepton >= 2'
cut = '(nElectron + nMuon) >= 2'

### SLIM FILE
slimfilein  = "SlimFileIn.txt"
slimfileout = "SlimFileOut.txt"

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetMetCorrelator import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.skimNRecoLeps import *
from PhysicsTools.NanoAODTools.postprocessing.modules.addTnPvarMuon import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
isData    = 'data' in sys.argv[-1] or 'Data' in sys.argv[-1]
doNotSkim = 'noskim' in sys.argv[-1] or 'noSkim' in sys.argv[-1]
doTnP     = 'TnP'  in sys.argv[-1]
doJECunc  = 'JEC'  in sys.argv[-1]
doMuonScale = 'muScale' in sys.argv[-1]
doJECunc = True
doMuonScale = True
if         '18' in sys.argv[-1] : year = 18
elif       '16' in sys.argv[-1] : year = 16
elif        '5' in sys.argv[-1] : year =  5
else                            : year = 17
era = '' if not 'era' in sys.argv[-1] else sys.argv[-1][sys.argv[-1].find('era')+3:sys.argv[-1].find('era')+4]
if era !='': print '>Found era: ', era

### Json file
jsonfile = runsAndLumis()
#if isData:
#  if     year == 18: jsonfile = 'Cert_314472-322057_13TeV_PromptReco_Collisions18_JSON.txt'
#  elif   year == 17: jsonfile = 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt' 
#  elif   year == 16: jsonfile = 'Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
  
mod = []
jecfile  = ''
if not isData: 
  if   year == 16:  
    mod.append(puWeight_2016())
    mod.append(PrefCorr2016())
  elif year == 17:  
    mod.append(puWeight_2017()) # puAutoWeight_2017 
    mod.append(PrefCorr2017())
  elif year == 18:  
    #jecfile  = "Autumn18_V19_MC"
    #jecarc   = "Autumn18_V19_MC"
    mod.append(puWeight_2018())
  elif year == 5:
    mod.append(puWeight_5TeV())
    mod.append(PrefCorr5TeV())
    jecfile  = "Spring18_ppRef5TeV_V4_MC"
    jecarc   = "Spring18_ppRef5TeV_V4_MC"
    #mod.append()
  else           :  mod.append(puWeight_2017())
#elif year == 18 and era != '': 
#  jecfile = 'Autumn18_Run%s_V8_DATA'%era
#  jecarc  = 'Autumn18_V8_DATA'
elif year == 5:
  jecfile = 'Spring18_ppRef5TeV_V4_DATA'
  jecarc  = 'Spring18_ppRef5TeV_V4_DATA'
  #jecfile = 'Spring18_ppRef5TeV_V2_DATA'
  #jecarc  = 'Spring18_ppRef5TeV_V2_DATA'

if jecfile != '': 
  print 'JEC file: ', jecfile
  mod.append(jetRecalib(jecfile, jecarc, redoJEC = True, year=year))

if doTnP:
  if isData:
    if   year == 17: mod.append(addTnPMuon17data())
    elif year == 16: mod.append(addTnPMuon16data())
    elif year == 18: mod.append(addTnPMuonForMoriond18data())
  else:
    if   year == 17: mod.append(addTnPMuon17())
    elif year == 16: mod.append(addTnPMuon16())
    elif year == 18: mod.append(addTnPMuonForMoriond18())
  slimfilein = "SlimFileTnP.txt"
  slimfileout = "SlimFileTnP.txt"
  cut = 'nMuon >= 2 && Muon_pt[0] > 25 && Muon_pt[1] >= 12'
else:
  if not doNotSkim: mod.append(skimRecoLeps())
  else: cut = ''
  if doJECunc and not isData: 
    if   year == 16: 
      mod.append(jetmetUncertainties2016All())
      mod.append(jetMetCorrelations2016())
    elif year == 17: 
      mod.append(jetmetUncertainties2017All())
      mod.append(jetMetCorrelations2017())
    elif year == 18: 
      mod.append(jetmetUncertainties2018All())
      mod.append(jetMetCorrelations2018())
    elif year == 5:  mod.append(jetmetUncertainties5TeV())
  if doMuonScale:
    if   year == 16: mod.append(muonScaleRes2016())
    elif year == 17: mod.append(muonScaleRes2017())
    elif year == 18: mod.append(muonScaleRes2018())
    elif year ==  5: mod.append(muonScaleRes2017())

print '>> Slim file in : ', slimfilein
print '>> Slim file out: ', slimfileout
print '>> cut: ', cut
print '>> ' + ('Is data!' if isData else 'Is MC!')
print '>> ' + ('Creating a TnP Tree' if doTnP else 'Creating a skimmed nanoAOD file')
if doJECunc: print '>> Adding JEC uncertainties'

#mod = [puAutoWeight(),jetmetUncertainties2017All(), skimRecoLeps()]
p=PostProcessor(".",inputFiles(),cut,slimfilein,mod,provenance=True,fwkJobReport=True,jsonInput=jsonfile,outputbranchsel=slimfileout) #jsonInput
p.run()

print "DONE"
os.system("ls -lR")
