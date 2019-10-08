#########################################################################################
# Usage:
# Load enviroment: cmsenv
# Load crab      : source /cvmfs/cms.cern.ch/crab3/crab.sh
# Load voms      : voms-proxy-init -voms cms
# Load brilcalc  : export PATH=/afs/cern.ch/user/j/jrgonzal/.local/bin:/cvmfs/cms-bril.cern.ch/brilconda/bin:/afs/cern.ch/user/j/jrgonzal/.local/bin:/cvmfs/cms-bril.cern.ch/brilconda/bin:/afs/cern.ch/group/zh/bin:/afs/cern.ch/user/j/jrgonzal/scripts:/afs/cern.ch/cms/caf/scripts:/cvmfs/cms.cern.ch/common:/cvmfs/cms.cern.ch/bin:/usr/sue/bin:/usr/lib64/qt-3.3/bin:/usr/kerberos/sbin:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/puppetlabs/bin:/afs/cern.ch/user/j/jrgonzal/bin

# Example: 
# python GetLumi.py --datasets "MuonEG, DoubleMuon" --eras 'B, C' --year 2017 --date 11/Feb --json lumisToProcess --verbose 2

import os, time, sys, argparse

parser = argparse.ArgumentParser(description='GetLumi')
parser.add_argument('--path',      default = './',                                                        help = 'Set the path. By default: ./')
parser.add_argument('--verbose',   default = 1,                                                           help = 'Set the verbose level')
parser.add_argument('--json',      default = 'lumisToProcess',                                            help = 'Introduce the json file to read by brilcalc')
parser.add_argument('--datasets',  default = 'MuonEG, DoubleMuon, DoubleEG, SingleMuon, SingleElectron',  help = 'Choose the datasets')
parser.add_argument('--eras',      default = 'B,C,D,E,F,G',                                               help = 'Select the eras to check')
parser.add_argument('--year',      default = 2017,                                                        help = 'Select the year (2017 by default)')
parser.add_argument('--date',      default = '11/Feb',                                                    help = 'Check automatically folders created in date with format: "11/Feb"')
parser.add_argument('--tag',       default = '',                                                          help = 'Check that a given tag is in the folder name')
args = parser.parse_args()

# Constants
path     = args.path
verbose  = args.verbose
jsonName = args.json
tag      = args.tag
Year     = args.year
Datasets = args.datasets.replace(' ', '').split(',') # ['MuonEG', 'DoubleMuon', 'DoubleEG','SingleMuon','SingleElectron'] 
Eras     = args.eras.    replace(' ', '').split(',')     # ['B', 'C', 'D', 'E', 'F']
Day, Month = args.date.replace(' ', '').split('/')

doCheckTime = True # To check the day and month of the creation

def GetDatasetInfo(d):
  c = (d.split('-'))[0].split('_')
  dataset = c[1]
  year    = (c[2][3:-1])
  era     = c[2][-1]
  if year.isdigit(): year = int(year)
  return dataset, year, era

def GetDatasets():
  dirs = []
  for d in os.listdir(path):
    if os.path.isdir(d): 
      if not d.startswith('crab_'): continue
      if doCheckTime:
        t = (time.ctime(os.path.getmtime(d))).replace('  ', ' ').split(' ')
        day = t[2]; month = t[1]
        if not day == str(Day): continue
        if not month == Month: continue
        if tag != '' and not tag in d: continue
      dataset, year, era = GetDatasetInfo(d)
      if not dataset in Datasets: continue
      if not int(Year) == year: continue
      if verbose >= 2: print ' >> Found dir for dataset ' + dataset + ', [year, era] = [' + str(year) + ', ' + era + ']: ', d
      dirs.append(d)
  return dirs

def CreateReports():
  ''' Execute crab report for all selected datasets... skips when dir/results exists '''
  f = GetDatasets()
  print ' >> Creating lumi json reports for %i datasets...'%len(f)
  for d in f:
    if os.path.isfile(d + '/results/lumisToProcess.json'): continue
    os.system('crab report ' + d)

def GetLumiPath(pathToDataset, jsonName = 'lumisToProcess'):
  if pathToDataset[-1] != '/': pathToDataset += '/'
  if not jsonName[-5:] == '.json': jsonName += '.json'
  jsonfile = pathToDataset + 'results/' + jsonName
  if not os.path.isfile(jsonfile): CreateReports()
  command = 'brilcalc lumi -b "STABLE BEAMS" -u /fb -i '
  out = os.popen(command + jsonfile).read()
  outlines = out.split('\n'); i = -1; l = ''
  for line in outlines:
    i += 1
    if not 'totrecorded' in line: continue
    else: l = outlines[i+2]
  if l == '': 
    print 'ERROR: lumi not found...'
    return
  return float(l.split('|')[-2])

def GetLumi():
  paths = GetDatasets()
  for d in Datasets:
    totalLumi = 0
    for era in Eras:
      for p in paths:
       idataset, iyear, iera = GetDatasetInfo(p)
       if iera == era and idataset == d:
         lumi = GetLumiPath(p) 
         totalLumi += lumi
         print d + ' >> Run%i '%iyear + iera + ': ' + str(lumi)
    print d + ' >> Total lumi: ', totalLumi
    
GetLumi()
