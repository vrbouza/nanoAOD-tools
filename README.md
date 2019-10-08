# nanoAOD-tools
Tools for working with NanoAOD (requiring only python + root, not CMSSW)
NanoAOD twiki: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD

## Checkout instructions

You need to install a recent version of CMSSW

    cmsrel CMSSW_9_4_6
    cd CMSSW_9_4_6/src
    cmsenv

Clone the code from the Oviedo-PAF group.

    git clone https://github.com/Oviedo-PAF/nanoAOD-tools.git PhysicsTools/NanoAODTools
    scram b

## How to run on CRAB

Set the enviroment.

    cmsenv
    source /cvmfs/cms.cern.ch/crab3/crab.sh
    voms-proxy-init -voms cms

Move to the directory:
 
    cd PhysicsTools/NanoAODTools/crab

To send jobs, run *SubmitDataset.py* as in the example:

    python SubmitDatasets.py datasets/data2017.txt --prodName myProd2017_DDMMYY

To check the status of the jobs:

    python CheckJobs.py --tag myProd2017_DDMMYY

## Some important info:

#### Important scripts

Check the default configuration (including JEC corrections) in *crab_script.py* and the options in *SubmitDataset.py*.

#### What is this doing? It reads a nanoAOD and:
- Applies a skim, using:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/modules/skimNRecoLeps.py

- Applies a slim using this file:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/SlimFile.txt

- Produces histogram with sum of weights here:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/framework/postprocessor.py

- Uses modules to produce PU weights, prefire weights, JEC uncertainties, Rochester corrections... the modules are in:
    https://github.com/Oviedo-PAF/nanoAOD-tools/tree/master/python/postprocessing/modules

- Chech what is being applied for each production in the script:
   https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/crab/crab_script.py 

