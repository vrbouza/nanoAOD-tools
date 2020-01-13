import os, sys
args = sys.argv

if len(args[1:]) == 0: 
  print 'Usage: \n>> python CheckDatasets.py datasets/mc2018.txt'
  exit()
fname = args[1]

command = 'dasgoclient --query="dataset dataset=%s"'

datasets = []
f = open(fname)
print 'Opening file: %s'%fname
for l in f.readlines():
  if l.startswith('#'): continue
  if '#' in l: l = l.split('#')[0]
  l = l.replace(' ', '').replace('\n', '')
  if l == '': continue
  datasets.append(l)

print 'Found %i datasets...'%len(datasets)
for d in datasets:
  #print 'Checking dataset %s...'%d
  match = os.popen(command%d).read()
  match = match.replace('\n', '')
  warn = '\033[0;32mOK       \033[0m' if match == d else '\033[0;31mNOT FOUND\033[0m'
  print '[%s] %s'%(warn, d)
