import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class ElectronScaleSmear(Module):
    def __init__(self,fileName,doApplyCor=False,doSystVar=True,run=None):
        self.doApplyCor = doApplyCor
        self.doSysVar = doSysVar
        self.fileName = fileName
        self.run = run

        # Load the class EnergyScaleCorrection
        try:
          ROOT.gSystem.Load("libPhysicsToolsNanoAODTools")
          dummy = ROOT.EnergyScaleCorrection
        except Exception as e:
          print "Could not load module via python, trying via ROOT", e
           if "/EnergyScaleCorrection_cc.so" not in ROOT.gSystem.GetLibraries():
             print "Load C++ Worker"
             ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/src/EnergyScaleCorrection.cc++" % os.environ['CMSSW_BASE'])
          dummy = ROOT.EnergyScaleCorrection

    def loadHisto(self,filename,hname):
      pass

    def beginJob(self):
    	pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
		  if outputFile : outputFile.cd()
        self.eleCorr = ROOT.EnergyScaleCorrection(self.fname, ROOT.EnergyScaleCorrection.ECALELF); 
        self.out = wrappedOutputTree
        if self.doApplyCor:
          self.out.branch("Electron_pt_nom","F")
          self.out.branch("Electron_mass_nom","F")
        if self.doSysVar:
          self.out.branch("Electron_pt_up","F")
          self.out.branch("Electron_pt_down","F")
          self.out.branch("Electron_mass_up","F")
          self.out.branch("Electron_mass_down","F")
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
      """process event, return True (go to next module) or False (fail, go to next event)"""
      run = long(event.run) if self.run == None else self.run
      if self.doApplyCor:
        elecPtNom = []
        elecMassNom = []
      if self.doSysVar:
        elecPtUp = []
        elecPtDo = []
        elecMassUp = []
        elecMassDo = []
      elec = Collection(event, 'Electron')
      nrandom = ROOT.gRandom.Gaus(0,1)
      for el in elec:
        p = TLorentzVector()
        p.SetPtEtaPhi(elec.pt elec.eta, elec.phi, elec.mass))
        r9 = elec.r9
        seed = elec.seedGain
        ecor = elec.eCorr
        et = p.Et()
        abseta = abs(p.Eta())
        if self.isData:
          if not self.doApplyCor: return True
          # Apply scale to data
          praw = p*(1./ecor) # Correct back
          escale = self.scaleCorr(run, et, abseta, r9)
          vEle = praw*escale
          elecPtNom.append(vEle.Pt())
          elecMassNom.append(vEle.M())
        else: # MC
          if self.doApplyCor: # Apply smear to MC
            praw = p*(1./ecor) # Correct back
            eleSmear = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, 0, 0.)
            vEle = praw*(1+eleSmear*nrandom)
            elecPtNom.append(vEle.Pt())
            elecMassNom.append(vEle.M())
          if self.doSysVar:
            escaleErr  = self.scaleCorrUncert(run, et, abseta, r9)
            eleSmearUp = self.eleCorr.smearingSigma(run, et, abseta, r9, 12,  1, 0.)
            eleSmearDo = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, -1, 0.)
            vEleUp = p*(1+(eleSmearUp+escaleErr)*nrandom)
            vEleDo = p*(1+(eleSmearDo-escaleErr)*nrandom)
            elecPtUp.append(vEleUp.Pt())
            elecPtDo.append(vEleDo.Pt())
            elecMassUp.append(vEleUp.M())
            elecMassDo.append(vEleDo.M())
      if self.doApplyCor:
        self.out.fillBranch("Electron_pt_nom", elecPtNom)
        self.out.fillBranch("Electron_mass_nom", elecMassNom)
      if self.doSysVar:
        self.out.fillBranch("Electron_pt_up",     elecPtUp)
        self.out.fillBranch("Electron_pt_down",   elecPtDo)
        self.out.fillBranch("Electron_mass_up",   elecMassUp)
        self.out.fillBranch("Electron_mass_down", elecMassDo)
      return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

fname2016="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/elecES/Run2018_Step2Closure_CoarseEtaR9Gain_v2" % os.environ['CMSSW_BASE']
fname2017="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/elecES/Run2018_Step2Closure_CoarseEtaR9Gain_v2" % os.environ['CMSSW_BASE']
fname2018="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/elecES/Run2018_Step2Closure_CoarseEtaR9Gain_v2" % os.environ['CMSSW_BASE']
fname2017LowPU="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/elecES/Run2018_Step2Closure_CoarseEtaR9Gain_v2" % os.environ['CMSSW_BASE']

elecUnc2016    = lambda : ElectronScaleSmear(fname2016, doApplyCor=False, doSystVar=True)
elecUnc2017    = lambda : ElectronScaleSmear(fname2016, doApplyCor=False, doSystVar=True)
elecUnc2018    = lambda : ElectronScaleSmear(fname2016, doApplyCor=False, doSystVar=True)
elecScale2017LowPu = lambda : ElectronScaleSmear(fname2016, doApplyCor=True, doSystVar=True)
elecScale5TeV      = lambda : ElectronScaleSmear(fname2016, doApplyCor=True, doSystVar=True, run=306936)
