import os,sys,ast
from SubmitDatasets import ReadLines, CheckPathDataset

def GetEntriesDAS(sample, verbose = False, pretend = False):
  if isinstance(sample, list):
    for s in sample: GetEntriesDAS(s, verbose, pretend)
    return
  dascommand = 'dasgoclient --query="summary dataset=%s"'%sample
  if verbose: print 'Looking for sample: ', sample
  if pretend:
    print 'Pretending: '
    print ' >> ', dascommand
    return
  out = os.popen(dascommand).read()
  d = ast.literal_eval(out)[0]
  nev = d['nevents']
  nfiles = d['nfiles']
  #print '%s: %i'%(FixStringLength(sample), nfiles)
  print '{%s} & %i & 1 \\\\'%(sample, nev)

def FixStringLength(s, n = 45):
  while len(s) < n: s += ' '
  while len(s) > n: s = s[:-1]
  return s

import argparse
parser = argparse.ArgumentParser(description='Get info from DAS')
parser.add_argument('--verbose','-v'    , action='store_true'  , help = 'Activate the verbosing')
parser.add_argument('--pretend','-p'    , action='store_true'  , help = 'Create the files but not send the jobs')
parser.add_argument('--test','-t'       , action='store_true'  , help = 'Sends only one or two jobs, as a test')
parser.add_argument('--options','-o'    , default=''           , help = 'Options to pass to your producer')
parser.add_argument('dataset'         , default=''           , nargs='?', help = 'txt file with datasets')

args = parser.parse_args()

verbose     = args.verbose
doPretend   = args.pretend
dotest      = args.test
options     = args.options
dataset     = args.dataset

path = CheckPathDataset(dataset)
if path != '': 
  print 'Reading file: ', path
  dataset = ReadLines(path)
GetEntriesDAS(dataset, verbose, doPretend)

