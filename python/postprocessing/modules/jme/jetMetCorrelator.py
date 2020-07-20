import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import os
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import math

class jetMetCorrelator(Module):
    def __init__(self, corrs, jetbranch, metbranch):
        self.corrs     = corrs    
        self.jetbranch = jetbranch
        self.metbranch = metbranch

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.wrappedOutputTree = wrappedOutputTree
        self.wrappedOutputTree.branch("%s_pt_jesTotalCorrUp"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_pt_jesTotalCorrDown"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_pt_jesTotalUnCorrUp"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_pt_jesTotalUnCorrDown"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_mass_jesTotalCorrUp"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_mass_jesTotalCorrDown"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_mass_jesTotalUnCorrUp"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_mass_jesTotalUnCorrDown"%self.jetbranch , "F", lenVar="n%s"%self.jetbranch)
        self.wrappedOutputTree.branch("%s_pt_jesTotalCorrUp"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_pt_jesTotalCorrDown"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_pt_jesTotalUnCorrUp"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_pt_jesTotalUnCorrDown"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_phi_jesTotalCorrUp"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_phi_jesTotalCorrDown"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_phi_jesTotalUnCorrUp"%self.metbranch , "F")
        self.wrappedOutputTree.branch("%s_phi_jesTotalUnCorrDown"%self.metbranch , "F")


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):

        """To correct the Jets"""
        jets = Collection(event, '%s'%self.jetbranch)
        jetCUp    = []
        jetCDown  = []
        jetUUp    = []
        jetUDown  = []
        jetCMUp    = []
        jetCMDown  = []
        jetUMUp    = []
        jetUMDown  = []

        """To correct the MET"""
        met = Object(event, self.metbranch)
        metPt  = getattr(met, "pt_nom", "pt")# if self.metbranch == "MET" else getattr(met, "pt", "pt")#pt_nom
        metPhi = getattr(met, "phi_nom", "phi")# if self.metbranch == "MET" else getattr(met, "phi", "phi") #phi_nom
        metPx  = metPt*math.cos(metPhi)
        metPy  = metPt*math.sin(metPhi)
        metPxCUp   = metPx
        metPyCUp   = metPy
        metPxCDown = metPx
        metPyCDown = metPy
        metPxUUp   = metPx
        metPyUUp   = metPy
        metPxUDown = metPx
        metPyUDown = metPy

        for j in jets:
            """If already recorrected, use the recorrected pT as nominal"""
            thePt  = getattr(j, "pt_nom", "pt") # pt_nom
            thePhi = getattr(j, "phi") 
            theMass= getattr(j, "mass_nom")
            jetCUp.append(0.)
            jetCDown.append(0.)
            jetUUp.append(0.)
            jetUDown.append(0.)
            jetCMUp.append(0.)
            jetCMDown.append(0.)
            jetUMUp.append(0.)
            jetUMDown.append(0.)
            for corr in self.corrs:
                jetCUp[-1]   = (jetCUp[-1]**2   + self.corrs[corr]    *((getattr(j,"pt_jes"+ corr + "Up")  -thePt))**2)**0.5 
                jetCDown[-1] = (jetCDown[-1]**2 + self.corrs[corr]    *((getattr(j,"pt_jes"+ corr + "Down")-thePt))**2)**0.5 
                jetUUp[-1]   = (jetUUp[-1]**2   + (1-self.corrs[corr])*((getattr(j,"pt_jes"+ corr + "Up")  -thePt))**2)**0.5 
                jetUDown[-1] = (jetUDown[-1]**2 + (1-self.corrs[corr])*((getattr(j,"pt_jes"+ corr + "Down")-thePt))**2)**0.5 
                jetCMUp[-1]   = (jetCUp[-1]**2   + self.corrs[corr]    *((getattr(j,"mass_jes"+ corr + "Up")  -theMass))**2)**0.5 
                jetCMDown[-1] = (jetCDown[-1]**2 + self.corrs[corr]    *((getattr(j,"mass_jes"+ corr + "Down")-theMass))**2)**0.5 
                jetUMUp[-1]   = (jetUUp[-1]**2   + (1-self.corrs[corr])*((getattr(j,"mass_jes"+ corr + "Up")  -theMass))**2)**0.5 
                jetUMDown[-1] = (jetUDown[-1]**2 + (1-self.corrs[corr])*((getattr(j,"mass_jes"+ corr + "Down")-theMass))**2)**0.5 
            """Use the corrected variation to recorrect MET"""
            metPxCUp   = metPxCUp   - jetCUp[-1]  *math.cos(thePhi)
            metPyCUp   = metPyCUp   - jetCUp[-1]  *math.sin(thePhi)
            metPxCDown = metPxCDown + jetCDown[-1]*math.cos(thePhi)
            metPyCDown = metPyCDown + jetCDown[-1]*math.sin(thePhi)
            metPxUUp   = metPxUUp   - jetUUp[-1]  *math.cos(thePhi)
            metPyUUp   = metPyUUp   - jetUUp[-1]  *math.sin(thePhi)
            metPxUDown = metPxUDown + jetUDown[-1]*math.cos(thePhi)
            metPyUDown = metPyUDown + jetUDown[-1]*math.sin(thePhi)
            """Save the values, not the variations"""
            jetCUp[-1]  += thePt
            jetUUp[-1]  += thePt
            jetCDown[-1] = thePt - jetCDown[-1]
            jetUDown[-1] = thePt - jetUDown[-1]
            jetCMUp[-1]   = theMass + jetCMUp[-1]
            jetUMUp[-1]   = theMass + jetUMUp[-1]
            jetCMDown[-1] = theMass - jetCMDown[-1]
            jetUMDown[-1] = theMass - jetUMDown[-1]

        """And then write everything"""
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalCorrUp"%self.jetbranch    ,  jetCUp       )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalCorrDown"%self.jetbranch  ,  jetCDown     )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalUnCorrUp"%self.jetbranch  ,  jetUUp       )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalUnCorrDown"%self.jetbranch,  jetUDown     )
        self.wrappedOutputTree.fillBranch("%s_mass_jesTotalCorrUp"%self.jetbranch    ,  jetCMUp       )
        self.wrappedOutputTree.fillBranch("%s_mass_jesTotalCorrDown"%self.jetbranch  ,  jetCMDown     )
        self.wrappedOutputTree.fillBranch("%s_mass_jesTotalUnCorrUp"%self.jetbranch  ,  jetUMUp       )
        self.wrappedOutputTree.fillBranch("%s_mass_jesTotalUnCorrDown"%self.jetbranch,  jetUMDown     )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalCorrUp"%self.metbranch    ,  (metPxCUp**2 + metPyCUp**2)**0.5    )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalCorrDown"%self.metbranch  ,  (metPxCDown**2 + metPyCDown**2)**0.5)
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalUnCorrUp"%self.metbranch  ,  (metPxUUp**2 + metPyUUp**2)**0.5    )
        self.wrappedOutputTree.fillBranch("%s_pt_jesTotalUnCorrDown"%self.metbranch,  (metPxUDown**2 + metPyUDown**2)**0.5)
        self.wrappedOutputTree.fillBranch("%s_phi_jesTotalCorrUp"%self.metbranch    , math.atan2(metPyCUp  ,    metPxCUp))
        self.wrappedOutputTree.fillBranch("%s_phi_jesTotalCorrDown"%self.metbranch  , math.atan2(metPyCDown,  metPxCDown))
        self.wrappedOutputTree.fillBranch("%s_phi_jesTotalUnCorrUp"%self.metbranch  , math.atan2(metPyUUp  ,    metPxUUp))
        self.wrappedOutputTree.fillBranch("%s_phi_jesTotalUnCorrDown"%self.metbranch, math.atan2(metPyUDown,  metPxUDown))

        return True

"""Following the recipes from https://docs.google.com/spreadsheets/d/1JZfk78_9SD225bcUuTWVo4i02vwI5FfeVKH-dwzUdhM/edit#gid=1345121349"""

jetMetCorrelations2016 = lambda : jetMetCorrelator({ "AbsoluteMPFBias": 1., "AbsoluteScale": 1., "AbsoluteStat":0., "FlavorQCD":1.,"Fragmentation":1.,"PileUpDataMC":0.5,"PileUpPtBB":0.5,"PileUpPtEC1":0.5,"PileUpPtEC2":0.5,"PileUpPtHF":0.5,"PileUpPtHF":0.5,"PileUpPtRef":0.5,"RelativeFSR":0.5,"RelativeJEREC1":0., "RelativeJEREC2":0., "RelativeJERHF":0.5,"RelativePtBB":0.5,"RelativePtEC1":0.,"RelativePtEC2":0.,"RelativePtHF":0.5, "RelativeBal":0.5, "RelativeSample":0., "RelativeStatEC":0., "RelativeStatFSR":0., "RelativeStatHF":0.,"SinglePionECAL":1., "SinglePionHCAL": 1., "TimePtEta":0.}, "Jet", "MET")

jetMetCorrelations2017 = lambda : jetMetCorrelator({ "AbsoluteMPFBias": 1., "AbsoluteScale": 1., "AbsoluteStat":0., "FlavorQCD":1.,"Fragmentation":1.,"PileUpDataMC":0.5,"PileUpPtBB":0.5,"PileUpPtEC1":0.5,"PileUpPtEC2":0.5,"PileUpPtHF":0.5,"PileUpPtHF":0.5,"PileUpPtRef":0.5,"RelativeFSR":0.5,"RelativeJEREC1":0., "RelativeJEREC2":0., "RelativeJERHF":0.5,"RelativePtBB":0.5,"RelativePtEC1":0.,"RelativePtEC2":0.,"RelativePtHF":0.5, "RelativeBal":0.5, "RelativeSample":0., "RelativeStatEC":0., "RelativeStatFSR":0., "RelativeStatHF":0.,"SinglePionECAL":1., "SinglePionHCAL": 1., "TimePtEta":0.}, "Jet", "METFixEE2017")

jetMetCorrelations2018 = lambda : jetMetCorrelator({ "AbsoluteMPFBias": 1., "AbsoluteScale": 1., "AbsoluteStat":0., "FlavorQCD":1.,"Fragmentation":1.,"PileUpDataMC":0.5,"PileUpPtBB":0.5,"PileUpPtEC1":0.5,"PileUpPtEC2":0.5,"PileUpPtHF":0.5,"PileUpPtHF":0.5,"PileUpPtRef":0.5,"RelativeFSR":0.5,"RelativeJEREC1":0., "RelativeJEREC2":0., "RelativeJERHF":0.5,"RelativePtBB":0.5,"RelativePtEC1":0.,"RelativePtEC2":0.,"RelativePtHF":0.5, "RelativeBal":0.5, "RelativeSample":0., "RelativeStatEC":0., "RelativeStatFSR":0., "RelativeStatHF":0.,"SinglePionECAL":1., "SinglePionHCAL": 1., "TimePtEta":0.}, "Jet", "MET")


