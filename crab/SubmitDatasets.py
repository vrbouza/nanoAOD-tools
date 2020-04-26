import getpass
import os
import sys
from CreateCrabScript import CreateCrabScriptSh

# Default option for the verbose
verbose   = False

##################### Get time
import datetime
def GetMonthName(n):
  if   n == 1 : return 'Jan'
  elif n == 2 : return 'Feb'
  elif n == 3 : return 'Mar'
  elif n == 4 : return 'Apr'
  elif n == 5 : return 'May'
  elif n == 6 : return 'Jun'
  elif n == 7 : return 'Jul'
  elif n == 8 : return 'Ago'
  elif n == 9 : return 'Sep'
  elif n == 10: return 'Oct'
  elif n == 11: return 'Nov'
  elif n == 12: return 'Dec'

def GetToday():
  now = datetime.datetime.now()
  today = str(now.day) + GetMonthName(now.month) + str(now.year)[2:]
  return today

def GetTimeNow():
  now = datetime.datetime.now()
  time = str(now.hour) + 'h' + str(now.minute) + 'm' + str(now.second) + 's'
  return time

def GetEra(datasetName, year, isData = True):
  if not isData: return ''
  if isinstance(year, int): year = str(year)
  if len(year) == 2: year = "20%s"%year
  sy = 'Run%s'%(year)
  ls = len(sy)
  find = datasetName.find(sy)
  if find == -1: return ''
  era = datasetName[find+ls:find+ls+1]
  return era
  
#################################################

def GetName_cfg(datasetName, isData = False):
  ''' Returns the name of the cfg file for a given dataset '''
  if datasetName[0] != '/': datasetName = '/' + datasetName
  tag = datasetName[1 : datasetName[1:].find('/')+1]
  genTag = datasetName[ datasetName[1:].find('/')+1 :]
  genTag = genTag[:genTag[1:].find('/')+1]
  a = genTag.find('_ext')
  if a > 0: tag += genTag[a+1:a+5]
  if(isData): tag += genTag.replace('/','_')
  filename = 'crab_cfg_' + tag + '.py'
  return filename


def CheckPathDataset(path):
  ''' Check if the name exists in local folder or in dataset folder '''
  if(os.path.isfile(path)): return path
  if(os.path.isfile(path+'.txt')): return path+'.txt'
  path = 'datasets/' + path
  if(os.path.isfile(path)): return path
  if(os.path.isfile(path+'.txt')): return path+'.txt'
  return ''
 
def GuessIsData(path):
  ''' Returns False if the dataset file seems to correspond to mc, True otherwise '''
  name = path.replace('datasets', '')
  if name.find('mc') >= 0 or name.find('MC') >= 0: return False
  elif name.find('data') >= 0 or name.find('Data') >= 0 or name.find('DATA') >= 0: return True
  else: 
    if 'NANOAOD' in path:
      if 'NANOAODSIM' in path: return False
      else: return True

def GuessYear(path):
  if   '5TeV' in path or '5tev' in path or '5p02' in path:  return 5
  elif 'Run2018' in path: return 18
  elif 'Run2017' in path: return 17
  elif 'Run2016' in path: return 16
  elif '2018'    in path: return 18
  elif '2017'    in path: return 17
  elif '2016'    in path: return 16

def CrateCrab_cfg(datasetName, isData = False, isTest = False, productionTag = 'prodTest', year = 0, options = '', outTier = 'T2_ES_IFCA'):
  ''' Creates a cfg file to send crab jobs to analyze a given dataset '''
  # CONSTANTS
  tier = outTier
  unitsperjob = 1

  # Set according to datasetName
  filename = GetName_cfg(datasetName, isData)
  localdir = filename[9:-3]

  # Set according to username
  username = getpass.getuser()
  basedir = '/store/user/' + username + '/nanoAODcrab'

  # Detect if it's MC or DATA and set parameters
  strSplitting = "FileBased"; # MC
  lumiMask = ''
  crabScript = 'crab_script.py'
  crabname = 'crab_script_' + productionTag
  craboptions = '%s,%i'%(options,year) if not isData else 'data,%s,%i'%(options,year)
  era = GetEra(datasetName, year, isData)
  if era != '': craboptions += ',era%s'%era

  CreateCrabScriptSh(crabname, craboptions)
  
  crabScriptSH = crabname + '.sh'
  slimeFileName = 'SlimFile' if not 'TnP' in options else 'SlimFileTnP'
  lumijson = ''
  
  if(isData): 
    # Set as MC... the only way the Count histogram works!! --> So we can compare with the numbers in DAS
    # strSplitting = "LumiBased"#"Automatic" # "LumiBased";
    #crabScriptSH = 'crab_script_data.sh'
    if   year == 16:
      lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
      lumijson = 'Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
    if   year == 17: 
      lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'  # 41.29/fb
      lumijson = 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
    elif year == 18: 
      lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'
      #'/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-322057_13TeV_PromptReco_Collisions18_JSON.txt'
      lumijson = 'Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'
    #https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2018Analysis#DATA
    elif year == 5:
      print 'Runing on 5.02 TeV DATA!!'
      lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/5TeV/ReReco/Cert_306546-306826_5TeV_EOY2017ReReco_Collisions17_JSON.txt'
      lumijson = 'Cert_306546-306826_5TeV_EOY2017ReReco_Collisions17_JSON.txt'

  # Set according to input parameters
  totalUnits = 3000 # test

  # Set as MC... the only way the Count histogram works!! --> So we can compare with the numbers in DAS
  #if isData: 
  #  totalUnits = 500000
  #  unitsperjob = 500
  if isTest: totalUnits = 3
  prodTag = productionTag
  datatype = 'global' if year != 5 else 'phys03' #phys03, global
  #datatype = 'phys03'

  t_localdir     = "config.General.requestName = '"  + localdir[0:70] + "_" + prodTag + "'\n"
  t_allowCMSSW   = "config.JobType.allowUndistributedCMSSW = True\n"
  if isData:
    t_inputfiles   = "config.JobType.inputFiles = ['" + crabScript + "','../scripts/haddnano.py', '../python/postprocessing/%sIn.txt', '../python/postprocessing/%sOut.txt', '../python/postprocessing/json/%s']\n" %(slimeFileName, slimeFileName, lumijson)
  else:
    t_inputfiles   = "config.JobType.inputFiles = ['" + crabScript + "','../scripts/haddnano.py', '../python/postprocessing/%sIn.txt', '../python/postprocessing/%sOut.txt']\n" %(slimeFileName, slimeFileName)
  t_inputdataset = "config.Data.inputDataset = '" + datasetName + "'\n" 
  t_totalunits   = "config.Data.totalUnits = " + str(totalUnits) + "\n"
  t_unitsperjob  = "config.Data.unitsPerJob = " + str(unitsperjob) + "\n"
  t_splitting    = "config.Data.splitting = '" + strSplitting + "'\n"
  t_basedir      = "config.Data.outLFNDirBase = '" + basedir + "'\n"
  t_datasetTag = "config.Data.outputDatasetTag = '" + prodTag + "_" + localdir[0:70] + "'\n" 
  t_tier = "config.Site.storageSite = '" + tier + "'\n"
  t_lumiMask = "config.Data.lumiMask = '" + lumiMask + "'\n"
 
  text = "from WMCore.Configuration import Configuration\n"
  text += "config = Configuration()\nconfig.section_('General')\n"
  text += t_localdir
  text += "config.General.transferLogs=True\nconfig.section_('JobType')\nconfig.JobType.pluginName = 'Analysis'\n"
  text += "config.JobType.psetName = 'PSet.py'\nconfig.JobType.scriptExe = '" + crabScriptSH + "'\nconfig.JobType.sendPythonFolder = True\n"
  text += t_allowCMSSW
  text += t_inputfiles
  text += "config.section_('Data')\n"
  text += t_inputdataset
  text += "config.Data.inputDBS = '%s'\n"%datatype
  text += "config.Data.allowNonValidInputDataset = True\n"
  text += t_splitting
  if isData: text += t_lumiMask
  #else: 
  text += t_unitsperjob
  text += t_totalunits
  text += t_basedir
  text += "config.Data.publication = False\n"
  text += t_datasetTag
  text += "config.section_('Site')\n"
  text += t_tier

  f = open(filename, 'w')
  f.write(text)
  f.close()
  os.system('chmod a+x ' + filename)
  if verbose: print '   >> Created cfg file: ', filename

def ReadLines(path):
  lines = []
  f = open(path, 'r')
  for line in f:
    line = line.replace(' ', '')
    line = line.replace('\t', '')
    line = line.replace('\n', '')
    line = line.replace('\r', '')
    if line == '': continue
    if line[0] == '#': continue
    if line.find('#') > 0: line = line[:line.find('#')]
    if len(line) <= 1: continue
    lines.append(line)
  return lines


def SubmitDatasets(path, isTest = False, prodName = 'prodTest', doPretend = False, options = '', outTier='T2_ES_IFCA'):
  path = CheckPathDataset(path)
  if(path == ''):
    print 'ERROR: dataset not found'
    return
  isData = GuessIsData(path)
  year   = GuessYear(path)
  if verbose: 
    if isData: print 'Opening path: ', path, '(DATA)'
    else: print  'Opening path: ', path, '(MC)'
  for line in ReadLines(path):
    cfgName = GetName_cfg(line, isData)
    print 'line = ', line
    if verbose: print 'Creating cfg file for dataset: ', line
    if verbose: print '%s!! year = %s, options = %s'%('Data' if isData else 'MC', year, options) 
    CrateCrab_cfg(line, isData, isTest, prodName, year, options, outTier)
    if not doPretend:
      os.system('crab submit -c ' + cfgName)
      if not os.path.isdir(prodName): os.mkdir(prodName)
      os.rename(cfgName, prodName + '/' + cfgName)
      #os.remove(cfgName)

#SubmitDatasets('data2017')

arguments = sys.argv[1:]
narg = len(arguments)

# Variables to set
dotest    = False
doPretend = False
doDataset = False
prodName  = 'Prod_' + GetToday() + '_' + GetTimeNow()
datasetName = ''
options = ''

if narg == 0:
  print ' > Usage:'
  print ' >>> python SubmitDatasets.py NameOfDatasetFile --option1 arg1 --option2'
  print ' '
  print ' > Options:'
  print ' > --test'
  print ' >   Sends a job per sample'
  print ' > --prodName name'
  print ' >   Set a name for the production. Example: may23'
  print ' > --verbose (or -v)'
  print ' > --dataset /dataset/name/'
  print ' >   Runs on a given dataset'
  print ' > --pretend'
  print ' >   Only creates the cfg file; does not send jobs'
  print ' > --options'
  print ' >   Add different options... as --options "TnP" or --options "2018,data"'
  print ' > --nutTier'
  print ' >   Select your Tier... by default: T2_ES_IFCA'
  print ' '
  print ' > Examples:'
  print ' >   python SubmitDatasets.py datasets/data2018.txt -v --prodName may28'
  print ' >   python SubmitDatasets.py datasets/data2018_TnP.txt -v --prodName may28 --options "TnP,2018,data"'
  print ' >   python SubmitDatasets.py --dataset /TT_TuneCUETP8M2T4_mtop1665_13TeV-powheg-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM -v --test'
  print ' >   python SubmitDatasets.py --dataset /TT_TuneCUETP8M2T4_mtop1665_13TeV-powheg-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM -v --pretend'

def __main__():
  print 'Executing main'
  import argparse
  parser = argparse.ArgumentParser(description='Submit jobs to crab')
  parser.add_argument('--verbose','-v'    , action='store_true'  , help = 'Activate the verbosing')
  parser.add_argument('--pretend','-p'    , action='store_true'  , help = 'Create the files but not send the jobs')
  parser.add_argument('--test','-t'       , action='store_true'  , help = 'Sends only one or two jobs, as a test')
  parser.add_argument('--dataset','-d'    , default=''           , help = 'Submit jobs to run on a given dataset')
  parser.add_argument('--year','-y'       , default=0            , help = 'Year')
  parser.add_argument('--prodName','-n'   , default=''           , help = 'Give a name to your production')
  parser.add_argument('--options','-o'    , default=''           , help = 'Options to pass to your producer')
  parser.add_argument('--outTier'    , default='T2_ES_IFCA' , help = 'Your output tier')
  parser.add_argument('file'         , default=''           , nargs='?', help = 'txt file with datasets')
  
  args = parser.parse_args()
  
  verbose     = args.verbose
  doPretend   = args.pretend
  dotest      = args.test
  datasetName = args.dataset
  prodName    = args.prodName
  options     = args.options
  outTier     = args.outTier
  fname       = args.file
  doDataset   = False if datasetName == '' else True
  year        = int(args.year)
  
  
  if doDataset:
    if verbose: print 'Creating cfg file for dataset: ', datasetName
    doData = GuessIsData(datasetName)
    if year == 0: year = GuessYear(datasetName)
    print ' >> Is data?: ', doData
    print ' >> Year    : ', year
    cfgName = GetName_cfg(datasetName, doData)
    CrateCrab_cfg(datasetName, doData, dotest, prodName, year, options,outTier)
    if not doPretend:
      os.system('crab submit -c ' + cfgName)
      if not os.path.isdir(prodName): os.mkdir(prodName)
      os.rename(cfgName, prodName + '/' + cfgName)
      #os.remove(cfgName)
  else:
    SubmitDatasets(fname, dotest, prodName, doPretend, options, outTier)
  
if __name__ == '__main__':
  __main__()
