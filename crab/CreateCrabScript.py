def CreateCrabScriptSh(name, options = ''):
 t = ''
 t += 'echo Check if TTY\n'
 t += 'if [ "`tty`" != "not a tty" ]; then\n'
 t += '  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"\n'
 t += 'else\n'
 t += '\n'
 t += 'ls -lR .\n'
 t += 'echo "ENV..................................."\n'
 t += 'env\n'
 t += 'echo "VOMS"\n'
 t += 'voms-proxy-info -all\n'
 t += 'echo "CMSSW BASE, python path, pwd"\n'
 t += 'echo $CMSSW_BASE \n'
 t += 'echo $PYTHON_PATH\n'
 t += 'echo $PWD \n'
 t += 'rm -rf $CMSSW_BASE/lib/\n'
 t += 'rm -rf $CMSSW_BASE/src/\n'
 t += 'rm -rf $CMSSW_BASE/module/\n'
 t += 'rm -rf $CMSSW_BASE/python/\n'
 t += 'mv lib $CMSSW_BASE/lib\n'
 t += 'mv src $CMSSW_BASE/src\n'
 t += 'mv module $CMSSW_BASE/module\n'
 t += 'mv python $CMSSW_BASE/python\n'
 t += '\n'
 t += 'echo Found Proxy in: $X509_USER_PROXY\n'
 t += 'python crab_script.py \'%s\'\n'%(options)
 t += 'fi\n'
 
 f = open(name+'.sh', 'w')
 f.write(t)
 f.close()
