import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TLorentzVector

import os
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class skipNRecoLeps(Module):
    def __init__(self, isdata = False, year = 17, recalibjets = '', era = ''):
        self.minelpt    =  8# 12 # 10 for 5 TeV, 18 for 13 # 7 for multilep
        self.minmupt    =  8#  0 for 5 TeV, 18 for 13 # 7 for multilep
        self.leadleppt  = 12# 12 for 5 TeV, 18 for 13
        self.maxeleta = 2.5
        self.maxmueta = 2.5
        self.isData = isdata
        self.year = year
        self.era = era
        self.filenameJECrecal = recalibjets
        self.filenameJEC = recalibjets
        if self.filenameJEC == '': self.filenameJEC = self.GetFileNameJEC(self.isData, self.filenameJEC, self.year, self.era)
        #self.jetReCalibrator = self.OpenJECcalibrator()
        
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def GetFileNameJEC(self, isdata, version = '', year = '', era = ''):
      f = version
      if f == '':
        if   year == 16: f = 'Summer16_23Sep2016V4'
        elif year == 17: f = 'Fall17_17Nov2017_V32'
        elif year == 18: f = 'Autumn18_V3'
      if isdata: f+= '_DATA'
      else:      f+= '_MC'
      return f

    #def OpenJECcalibrator(self, jetType = "AK4PF", doRes = True):
    #    # For jet re-calibrating
    #    fileNameJEC = self.filenameJEC
    #    jesInputFilePath = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/" # By default
    #    print 'Using the file: ', jesInputFilePath+fileNameJEC
    #    return JetReCalibrator(fileNameJEC, jetType , doRes, jesInputFilePath, upToLevel=1)

    def analyze(self, event):
        #jets = Collection(event, 'Jet')
        elec = Collection(event, 'Electron')
        muon = Collection(event, 'Muon')

        nlepgood = 0; minptLeading = False
        lepCharge = []
        for mu in muon:
          if mu.pt > self.minmupt and abs(mu.eta) < self.maxmueta:# and (mu.tightId or mu.mediumId): 
            nlepgood += 1
            lepCharge.append(mu.charge)
            if mu.pt >= self.leadleppt: minptLeading = True
        for el in elec:
          if el.pt > self.minelpt and abs(el.eta) < self.maxeleta: #and (el.cutBased >= 1): 
            nlepgood += 1
            lepCharge.append(el.charge)
            if el.pt >= self.leadleppt: minptLeading = True

        #if   nlepgood < 2:   return False
        #elif nlepgood == 2:  return ((lepCharge[0] * lepCharge[1] > 0) and minptLeading)
        #else              :  return minptLeading
        
        return nlepgood >= 2 and minptLeading

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

skimRecoLeps = lambda : skipNRecoLeps()
