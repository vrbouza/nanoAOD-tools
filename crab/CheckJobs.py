import time, datetime, os, sys

def GetDirDate(path):
  t = datetime.datetime.fromtimestamp(os.path.getmtime(path))
  text = '%i/%i/%i'%(t.day,t.month,t.year)
  return text

def GetLine(fulltext, find):
  n = fulltext.find(find)
  if n == -1: return ''
  n = fulltext[n:]
  n = n.split('\n')[0]
  return n

def GC(n = -1):
  return '\033[0m' if n < 0 else '\033[1;3%im'%n

def CheckStatus(dirname, verbose = 1, autoResubmit = True, pretend = False, forceResubmit = False):
  if not os.path.isdir(dirname): return
  command = 'crab status -d ' + dirname
  if pretend: 
    print command
    return
  out = os.popen(command).read()

  fin = GetLine(out,'finished')
  tra = GetLine(out,'transferring')
  run = GetLine(out,'running')
  fai = GetLine(out,'failed'); 
  status = GetLine(out, 'Status on the scheduler')
  submitfailed = GetLine(out, 'SUBMITFAILED')
  if submitfailed != '': status = 'SUBMITFAILED'
  if status != '': status = status.split('\t')[-1]
  title = GC(4)+'['+GC(3)+dirname+GC(4)+']'+GC()
  if   status == 'SUBMITFAILED': title += '\t\tStatus: '+GC(1)+status+GC()
  elif status == 'FAILED'      : title += '\t\tStatus: '+GC(5)+status+GC()
  else                         : title += '\t\tStatus: '+GC(2)+status+GC()
  if fai != '' and status == 'FAILED':    title += '\t'+GC(1)+'Failed jobs: '+ fai.split('\t')[-1]+GC()
  if verbose >= 1 or not 'COMPLETE' in status: print title
  if verbose >= 2:
    if fin != '': print '  # ' + GC(2) + fin[:fin.find(' ')] + '\t' + GC(4) + fin[fin.find(' '):]+GC()
    if tra != '': print '  # ' + GC(2) + tra[:tra.find(' ')] + '\t' + GC(4) + tra[tra.find(' '):]+GC()
    if run != '': print '  # ' + GC(2) + run[:run.find(' ')] + '\t' + GC(4) + run[run.find(' '):]+GC()
    if fai != '': print '  # ' + GC(2) + fai[:fai.find(' ')] + '\t' + GC(4) + fai[fai.find(' '):]+GC()
  if   status == 'FAILED' and autoResubmit: Resubmit(dirname, verbose)
  elif status == 'SUBMITTED' and forceResubmit: Resubmit(dirname, verbose)
  elif status == 'SUBMITFAILED' and autoResubmit: CrabSubmit(dirname, verbose)
  #if status == 'SUBMITTED':

#crab_WZ_TuneCP5_13TeV-pythia8_mc2017_22jul2019/crab.log:INFO 2019-07-22 17:54:00,650: def Will use CRAB configuration file crab_cfg_WZ_TuneCP5_13TeV-pythia8.py
#dirname+'/crab.log'
#crab_TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_mc2017_22jul2019

def CrabSubmit(dirname, verbose = 1, pretend = False, force = True):
  f = open(dirname+'/crab.log').read()
  fname = GetLine(f, 'Will use CRAB configuration file').split(' ')[-1]
  #crab_cfg_TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8.py
  refname = "%s"%fname
  if os.path.isfile(refname):
    submitname = refname
  else:
    submitname = "%s"%dirname
    while submitname[0] == '.' or submitname[0] == '/': submitname = submitname[1:]
    if submitname.startswith('crab_'): submitname = submitname[5:]
    if refname.endswith('.py'): refname = refname[:-3]
    if refname.startswith('crab_cfg_'): refname = refname[9:]
    submitname = submitname[len(refname)+1:]
    while submitname[0] == '/': submitname = submitname[1:]
    submitname = submitname + '/' + fname
  command = "crab submit -c %s"%(submitname)
  if pretend:
    print command
    return
  if force: 
    newdir = refname+'old' if not '/' in refname else refname.split('/')[-1]+'old'
    print ' >> Moving dir %s to %s...'%(dirname, newdir)
    if os.path.isfile(newdir) or os.path.isdir(newdir): os.system('rm -r %s'%newdir)
    os.system('mv %s %s'%(dirname, newdir))
  os.system(command)


def Resubmit(dirname, verbose = 1, pretend = False):
  if verbose >= 1: print '  > ' + GC(1) + 'Resubmitting ' + GC(6) + dirname + GC() + '...'
  command = 'crab resubmit -d ' + dirname
  if pretend:
    print command
    return
  os.system(command)# + ' >> /dev/null')
  if verbose >= 2: print GC(3) + 'Done!' + GC()

def CheckJobs(path = './', dirstart = 'crab_', date = '', verbose = 1, autoResubmit = False, tag = '', forceResubmit = False):
  for d in os.listdir(path):
    if not os.path.isdir(path + '/' + d): continue
    if date != '' and date != GetDirDate(path + '/' + d): continue
    if not d.startswith(dirstart): continue
    if tag != '' and not tag in d: continue
    CheckStatus(path+'/'+d, verbose, autoResubmit, forceResubmit=forceResubmit)

##################################################################################################################
import argparse

date = ''; tag = ''
parser = argparse.ArgumentParser()
parser.add_argument('--date', type = str, help ='Introduce the date in the format D/M/YYYY (example: 9/1/2019)')
parser.add_argument('-p','--path', type = str, help ='Path to look for crab jobs')
parser.add_argument('--dir',  type = str, help ='Folder name must start with this string (by default: \'crab_\')')
parser.add_argument('--tag',  type = str, help ='String that must be contained in the folder name')
parser.add_argument("-v", "--verbose", type = int,help="Increase output verbosity (1 by default)")
parser.add_argument("-a", "--auto", action='store_true',help="Resubmit faling jobs automatically")
parser.add_argument("-f", "--force", action='store_true',help="Send resubmition also when SUBMITED status")
args = parser.parse_args()
date = args.date
path = args.path
dirn = args.dir
verb = args.verbose
auto = args.auto
force = args.force
tag  = args.tag
if date == None: date = ''
if path == None: path = './'
if dirn == None: dirn = 'crab_'
if verb == None: verb = 1
if auto == None: auto = 0
if tag  == None: tag  = ''
if force== None: force = False

CheckJobs(path, dirn, date, verb, auto, tag, force)

