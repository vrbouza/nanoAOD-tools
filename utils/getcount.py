from utils import *

arguments = sys.argv[1:]
narg = len(arguments)
files = []
if narg < 1:
  print 'Usage: ' 
  print ' >> python samplename'
  print ' >> python path samplename'
  print '   Example:  python dir TTbar_Powheg'
else:
  if narg == 1:
    outname = arguments[0]
    PrintCount(outname, '')
  else:
    dirname = arguments[0]
    outname = arguments[1]
    PrintCount(dirname, outname)
