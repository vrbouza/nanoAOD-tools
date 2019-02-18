import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TLorentzVector

import os
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class addTnPvarMuon(Module):
    def __init__(self, year = 17):
      self.kProbePt = 12
      self.kTagPt   = 29
      self.kTagIso  = 0.20
      self.kMaxMass = 140
      self.kMinMass = 60
      self.year = year
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Tag_pt",   "F")
        self.out.branch("Tag_eta",  "F")
        self.out.branch("Tag_phi",  "F")
        self.out.branch("Tag_mass", "F")
        self.out.branch("Tag_iso",  "F")
        self.out.branch("Tag_dxy",  "F")
        self.out.branch("Tag_dz",  "F")
        self.out.branch("Tag_charge", "I")
        self.out.branch("Probe_pt",   "F")
        self.out.branch("Probe_eta",  "F")
        self.out.branch("Probe_phi",  "F")
        self.out.branch("Probe_mass", "F")
        self.out.branch("Probe_charge", "I")
        self.out.branch("Probe_dxy", "F")
        self.out.branch("Probe_dz", "F")
        self.out.branch("Probe_SIP3D", "F")
        self.out.branch("Probe_iso", "F")
        self.out.branch("Probe_passL",        "I")
        self.out.branch("Probe_passM",       "I")
        self.out.branch("Probe_passMP", "I")
        self.out.branch("Probe_passT",        "I")
        self.out.branch("Probe_passRelIsoVL",  "I")
        self.out.branch("Probe_passRelIsoL",  "I")
        self.out.branch("Probe_passRelIsoM",  "I")
        self.out.branch("Probe_passRelIsoT",  "I")
        self.out.branch("Probe_passMiniIsoL", "I")
        self.out.branch("Probe_passMiniIsoM", "I")
        self.out.branch("Probe_passMiniIsoT", "I")
        self.out.branch("Probe_passMiniIsoVT", "I")
        self.out.branch("Probe_passMultiIsoL", "I")
        self.out.branch("Probe_passMultiIsoM", "I")
        self.out.branch("Probe_passMultiIsoM2017", "I")
        self.out.branch("Probe_passMultiIsoM2017v2", "I")
        self.out.branch("Probe_ptRatio", "F")
        self.out.branch("Probe_ptRel", "F")
        self.out.branch("Probe_jetRelIso", "F")
        self.out.branch("Probe_passDptPt02",   "I")
        self.out.branch("Probe_passSIP4",         "I")
        self.out.branch("Probe_passSIP8",         "I")
        self.out.branch("Probe_passMVAL",         "I")
        self.out.branch("Probe_passMVAM",         "I")
        self.out.branch("Probe_passMVAT",         "I")
        self.out.branch("TnP_mass", "F")
        self.out.branch("TnP_ht", "F")
        self.out.branch("TnP_met", "F")
        self.out.branch("TnP_trigger", "I")
        self.out.branch("TnP_npairs", "I")
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def IsMatched(self, muonLorentzVector, trigObjCollection):
      dRmin = 0.1
      match = False
      for trigObj in trigObjCollection:
        dR = muonLorentzVector.DeltaR(trigObj)
        if dR < dRmin: match = True
      return match
    def analyze(self, event):
        # Get Jet and Muon collections
        jet  = Collection(event, 'Jet')
        muon = Collection(event, 'Muon')
        trigObj = Collection(event, 'TrigObj')

        #### Construct the trigger object collection containing muons triggering a single iso muon trigger
        selTrigObj = []
        for tr in trigObj:
          if not abs(tr.id) == 13: continue
          #print 'Trig muon found! with filterBits: ', tr.filterBits
          if not (bool(tr.filterBits & 2) or bool(tr.filterBits & 8)): continue
          t = TLorentzVector()
          t.SetPtEtaPhiM(tr.pt, tr.eta, tr.phi, 0.105)
          selTrigObj.append(t)
        #print 'len(selTrigObj) = ', len(selTrigObj)

        #### Selection of tag and probe muons
        # Tag: pT, eta, tightId, iso
        # Probe: pT, eta
        tags = []; probes = []; pair = []
        index = 0
        for mu in muon:
          if not abs(mu.eta) < 2.4 or not mu.pt > self.kProbePt: 
            index += 1
            continue
          if mu.pt > self.kTagPt and mu.tightId and mu.pfRelIso04_all < self.kTagIso:  
            tp = TLorentzVector()
            tp.SetPtEtaPhiM(mu.pt, mu.eta, mu.phi, mu.mass)
            if self.IsMatched(tp, selTrigObj): tags.append(index)
          else: probes.append(index)
          index+=1
        if len(tags) == 0:              return False
        if len(tags) + len(probes) < 2: return False

        ### Forming TnP pairs with leptons passing Tag selection
        ### If two tight muons, you have two TnP pairs!
        ### If one tag has more than one probe candidate, the pairs are not selected
        for t1 in tags:
          nProbesFound = 0
          tp1 = TLorentzVector()
          tp1.SetPtEtaPhiM(muon[t1].pt, muon[t1].eta, muon[t1].phi, muon[t1].mass)
          for t2 in tags:
            if t2 == t1: continue
            tp2 = TLorentzVector()
            tp2.SetPtEtaPhiM(muon[t2].pt, muon[t2].eta, muon[t2].phi, muon[t2].mass)
            mass = (tp1+tp2).M()
            if mass > self.kMaxMass or mass < self.kMinMass: continue
            ### The tag must match a trigger object:
            if nProbesFound == 0: 
              nProbesFound += 1
              pair.append([t1, t2])
            else: # This tag has 2 or more probes!!
              pair = pair[:-1]

        ### Forming TnP pairs with a Tag lepton and Probe leptons
        for t in tags:
          nProbesFound = 0
          tp = TLorentzVector()
          tp.SetPtEtaPhiM(muon[t].pt, muon[t].eta, muon[t].phi, muon[t].mass)
          for p in probes:
            pp = TLorentzVector()
            pp.SetPtEtaPhiM(muon[p].pt, muon[p].eta, muon[p].phi, muon[p].mass)
            mass = (tp+pp).M()
            if mass > self.kMaxMass or mass < self.kMinMass: continue
            ### The tag must match a trigger object:
            if nProbesFound == 0: 
              nProbesFound += 1
              pair.append([t, p])
            else: # This tag has 2 or more probes!!
              pair = pair[:-1]

        # Check that we have at least one pair... calculate the mass of the pair
        if len(pair) == 0: return False # events with 1 or 2 pairs!
        for thisPair in pair:
          ti, pi = thisPair
          ptag = TLorentzVector(); ppro = TLorentzVector()
          ptag.SetPtEtaPhiM(muon[ti].pt, muon[ti].eta, muon[ti].phi, muon[ti].mass)
          ppro.SetPtEtaPhiM(muon[pi].pt, muon[pi].eta, muon[pi].phi, muon[pi].mass)
          mass        = (ptag+ppro).M()

          # Trigger requirement... IsoMu27
          if   self.year == 17:
            passTrigger = event.HLT_IsoMu27
          elif self.year == 16:
            passTrigger = event.HLT_IsoMu24 or event.HLT_IsoTkMu24
          elif self.year == 18:
            passTrigger = event.HLT_IsoMu24
        
          # Compute HT and MET
          ht = 0; met = event.METFixEE2017_pt if self.year == 17 else event.MET_pt
          for j in jet: ht += j if j > 30 else 0

          # Tag kinematics
          self.out.fillBranch("Tag_pt",    muon[ti].pt)
          self.out.fillBranch("Tag_eta",   muon[ti].eta)
          self.out.fillBranch("Tag_phi",   muon[ti].phi)
          self.out.fillBranch("Tag_mass",  muon[ti].mass)
          self.out.fillBranch("Tag_charge",muon[ti].charge)
          self.out.fillBranch("Tag_iso",   muon[ti].pfRelIso04_all)
          self.out.fillBranch("Tag_dz",    muon[ti].dz)
          self.out.fillBranch("Tag_dxy",   muon[ti].dxy)

          # Probe kinematics
          self.out.fillBranch("Probe_pt",    muon[pi].pt)
          self.out.fillBranch("Probe_eta",   muon[pi].eta)
          self.out.fillBranch("Probe_phi",   muon[pi].phi)
          self.out.fillBranch("Probe_mass",  muon[pi].mass)
          self.out.fillBranch("Probe_charge",muon[pi].charge)
          self.out.fillBranch("Probe_dxy",   muon[pi].dxy)
          self.out.fillBranch("Probe_dz",    muon[pi].dz)
          self.out.fillBranch("Probe_SIP3D", muon[pi].sip3d)
          self.out.fillBranch("Probe_iso",   muon[pi].pfRelIso04_all)

          # Probe ID and ISO flags (from nanoAOD tag IDs)
          self.out.fillBranch("Probe_passL",         1)
          self.out.fillBranch("Probe_passM",         muon[pi].mediumId)
          self.out.fillBranch("Probe_passMP",        muon[pi].mediumPromptId)
          self.out.fillBranch("Probe_passT",         muon[pi].tightId)
          self.out.fillBranch("Probe_passRelIsoVL",  muon[pi].pfRelIso04_all <= 0.4)
          self.out.fillBranch("Probe_passRelIsoM",   muon[pi].pfRelIso04_all <= 0.25)
          self.out.fillBranch("Probe_passRelIsoL",   muon[pi].pfRelIso04_all <= 0.20)
          self.out.fillBranch("Probe_passRelIsoT",   muon[pi].pfRelIso04_all <= 0.15)
          self.out.fillBranch("Probe_passMiniIsoL",  muon[pi].miniIsoId >= 1)
          self.out.fillBranch("Probe_passMiniIsoM",  muon[pi].miniIsoId >= 2)
          self.out.fillBranch("Probe_passMiniIsoT",  muon[pi].miniIsoId >= 3)
          self.out.fillBranch("Probe_passMiniIsoVT", muon[pi].miniIsoId >= 4)

          # Other working points: SIP2D and dpt/pt
          self.out.fillBranch("Probe_passDptPt02",   muon[pi].ptErr/muon[pi].pt < 0.2)
          self.out.fillBranch("Probe_passSIP4",      muon[pi].sip3d < 4)
          self.out.fillBranch("Probe_passSIP8",      muon[pi].sip3d < 8)

          # Probe Lepton MVA (from nanoAOD, for the moment)
          self.out.fillBranch("Probe_passMVAL",      muon[pi].mvaId >= 1)
          self.out.fillBranch("Probe_passMVAM",      muon[pi].mvaId >= 2)
          self.out.fillBranch("Probe_passMVAT",      muon[pi].mvaId >= 3)

          # MultiIso... calculate jet-JecLepAware from Muon_jetRelIso in nanoAOD
          jetRelIso  = muon[pi].jetRelIso # jetRelIso = 1/ptRatio - 1
          ptRatio = 1/(jetRelIso + 1)
          jetJECLepAwarePt = muon[pi].pt*(jetRelIso + 1)
          jetId = muon[pi].jetIdx
          MiniRelIso = muon[pi].miniPFRelIso_all
          if jetId != -1:
            lp = TLorentzVector(); jt = TLorentzVector()
            lp.SetPtEtaPhiM(muon[pi].pt, muon[pi].eta, muon[pi].phi, muon[pi].mass)
            jt.SetPtEtaPhiM(jetJECLepAwarePt,  jet[jetId].eta,  jet[jetId].phi,  jet[jetId].mass)
            ptRel = lp.Perp((jt-lp).Vect())
          else:
            ptRel = 0

          # Definitions from https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF
          passMultiIsoL =       MiniRelIso < 0.20 and (ptRatio > 0.69 or ptRel > 6.0) 
          passMultiIsoM =       MiniRelIso < 0.16 and (ptRatio > 0.76 or ptRel > 7.2) 
          passMultiIsoM2017   = MiniRelIso < 0.12 and (ptRatio > 0.80 or ptRel > 7.5) 
          passMultiIsoM2017v2 = MiniRelIso < 0.11 and (ptRatio > 0.74 or ptRel > 6.8) 
          self.out.fillBranch("Probe_passMultiIsoL",       passMultiIsoL)
          self.out.fillBranch("Probe_passMultiIsoM",       passMultiIsoM)
          self.out.fillBranch("Probe_passMultiIsoM2017",   passMultiIsoM2017)
          self.out.fillBranch("Probe_passMultiIsoM2017v2", passMultiIsoM2017v2)
          self.out.fillBranch("Probe_ptRatio", ptRatio)
          self.out.fillBranch("Probe_ptRel",   ptRel)
          self.out.fillBranch("Probe_jetRelIso",   jetRelIso)

          # TnP variables
          self.out.fillBranch("TnP_mass",     mass);
          self.out.fillBranch("TnP_trigger",  passTrigger); 
          self.out.fillBranch("TnP_npairs",   len(pair)); 
          self.out.fillBranch("TnP_met",      met);
          self.out.fillBranch("TnP_ht",       ht);
          self.out.fill()
        return False

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
addTnPMuon16 = lambda : addTnPvarMuon(16)
addTnPMuon17 = lambda : addTnPvarMuon(17)
addTnPMuon18 = lambda : addTnPvarMuon(18)
addTnPMuon   = lambda : addTnPvarMuon()
