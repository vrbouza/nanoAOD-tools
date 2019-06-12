# nanoAOD-tools
Tools for working with NanoAOD (requiring only python + root, not CMSSW)

## Checkout instructions

You need to install a recent version of CMSSW

    cmsrel CMSSW_9_4_6
    cd CMSSW_9_4_6/src
    cmsenv

Clone the code from the Oviedo-PAF group.

    git clone https://github.com/Oviedo-PAF/nanoAOD-tools.git PhysicsTools/NanoAODTools
    scram b


## Local example for producing TnP trees

You can run a example to run on a single file and obtain a TnP n-tuple with the TnP produced module.

    cmsenv
    voms-proxy-init -voms cms
    cd PhysicsTools/NanoAODTools/python/postprocessing/
    python TnPaddVar.py

## How to run on CRAB

Set the enviroment.

    cmsenv
    source /cvmfs/cms.cern.ch/crab3/crab.sh

Move to the directory:
 
    cd PhysicsTools/NanoAODTools/crab

To send jobs, run this script and follow the instructions:

    python SubmitDatasets.py

To run on several datasets, edit the txt files in the /datasets folder. Follow the instruction in:
   
    https://github.com/Oviedo-PAF/nanoAOD-tools/tree/master/crab

## Run in local:

The code is prepared to run an example. After setting the enviroment:

    cd PhysicsTools/NanoAODTools/python/postprocessing/
    python NanoPAFprepare.py

This shoud run on a nanoAOD file and produce an output.

## Some important info:

#### What is this doing? It reads a nanoAOD and:
- Applies a string-like skim
- Use the module skimNRecoLeps to select events with 2 leptons with pT > 18, eta < 2.5 (by default)
- Removes plenty of branches
- Produces PU weights
- Produces Count / SumWeights histograms
- Changes the name of the main tree 'Events' to 'tree'
- Changes the output name and copies the output to a T2
- Additionally, the TnP module can be used to create an output TnP tree to produce muon efficiencies.
