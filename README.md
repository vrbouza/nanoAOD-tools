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

Change to this branch:

    git checkout -b nanoAODv6_13jan2020

Compile:

    scram b

## How to run on CRAB

Set the enviroment.

    cmsenv
    source /cvmfs/cms.cern.ch/crab3/crab.sh
    voms-proxy-init -voms cms

Move to the directory:
 
    cd PhysicsTools/NanoAODTools/crab

To send jobs, run *SubmitDataset.py*. Try to execute it with no options to obtain info and examples. You can process all files from a text file using a txt file as output as in the example below. You can first check if all the datasets are found in crab using the *CheckDatasets.py* script and passing the txt file as an argument.

    python SubmitDatasets.py datasets/data2017.txt --prodName nanoAODv6_13jan2020

To process a single dataset:

    python SubmitDatasets.py --datasets [DATASET] --outTier [T2_ES_IFCA] --prodName nanoAODv6_13jan2020 --year 17

Use the option *--test* to send a few short jobs or the option *--pretend* to create the files and not run on them.

To check the status of the jobs:

    python CheckJobs.py --tag nanoAODv6_13jan2020
    
Add the option *-a* to auto-resubmit all failed jobs.

## Some important info:

#### Important scripts

Check the default configuration (including JEC corrections) in *crab_script.py* and the options in *SubmitDataset.py*.

#### What is this doing? It reads a nanoAOD and:
- Applies a skim, using:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/modules/skimNRecoLeps.py

- Applies a slim using this file:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/SlimFileOut.txt

- Produces histogram with sum of weights here:
    https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/python/postprocessing/framework/postprocessor.py

- Uses modules to produce PU weights, prefire weights, JEC uncertainties, Rochester corrections... the modules are in:
    https://github.com/Oviedo-PAF/nanoAOD-tools/tree/master/python/postprocessing/modules

- Chech what is being applied for each production in the script:
   https://github.com/Oviedo-PAF/nanoAOD-tools/blob/master/crab/crab_script.py 

## Merge the output trees
Use the instructions in this repository:
    https://github.com/GonzalezFJR/xtools
