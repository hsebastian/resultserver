# dependencies 
import os
import re
import fnmatch
import datetime
from optparse import OptionParser

import simplejson as json
import couchquery
from couchquery import CouchDBException

# data format
# dataStructure = {
  # "buildid": build, 
  # "product": product,
  # "os": opsys,
  # "testtype": testtype,
  # "timestamp": str(date),
  # "tests": [test1, test2, test3, ...]
# }

# testStructure = {
  # testname: {
    # "pass": passcount,
    # "fail": failcount,
    # "todo": todocount,
    # "note": [note1, note2, note3, ...]
# }

# pattern for matching either ...
reStatus = re.compile(r'TEST-((FAIL)|(PASS)|(UNEXPECTED-FAIL)|(TIMEOUT)|(KNOWN-FAIL))')

# global variables
tests = dict()

def _getBuild(text):
  label = r'tinderbox: build: '
  regex = re.compile(label + r'.*')
  result = regex.search(text)
  if result != None:
    return (result.group(0))[len(label):len(result.group(0))]
  else:
    return 'no-info'

# bug: BUILDID appears twice with different values in the log
def getBuildId(text):
  label = r'BuildID='
  regex = re.compile(label + r'.*')
  result = regex.search(text)
  if result != None:
    return (result.group(0))[len(label):len(result.group(0))]
  else:
    return 'no-info'

def getProduct(text):
  label = r'Name='
  regex = re.compile(label + r'.*')
  result = regex.search(text)
  if result != None:
    return (result.group(0))[len(label):len(result.group(0))]
  else:
    return 'no-info'

def getOs(text):
  return (re.split(' +', _getBuild(text)))[0]

def getTestType(text):
  splitted = re.split(' +', _getBuild(text))
  return splitted[len(splitted)-1]

# cannot handle blank test file when exception occurred
# some notes appear on the line below:
# TEST-PASS | /media/mmc1/release/xpcshell/tests/test_uriloader_exthandler/unit/test_handlerService.js | [run_test : 147] true == true
# NEXT ERROR TEST-UNEXPECTED-FAIL | /media/mmc1/release/xpcshell/tests/test_uriloader_exthandler/unit/test_handlerService.js | 0 == 3 - See following stack:
# JS frame :: /media/mmc1/release/xpcshell/head.js :: do_throw :: line 181
# JS frame :: /media/mmc1/release/xpcshell/head.js :: do_check_eq :: line 211
# JS frame :: /media/mmc1/release/xpcshell/tests/test_uriloader_exthandler/unit/test_handlerService.js :: run_test :: line 154
# JS frame :: /media/mmc1/release/xpcshell/head.js :: _execute_test :: line 125
# JS frame :: -e :: <TOP_LEVEL> :: line 1
# TEST-INFO | (xpcshell/head.js) | exiting test
  # <<<<<<<
# TEST-PASS | /media/mmc1/release/xpcshell/tests/test_uriloader_exthandler/unit/test_punycodeURIs.js | test passed
def getTestDetail(text):
  line = text.split('|')
  outcome = (reStatus.search(line[0])).group(0)
  pathname = line[1].strip()
  pieces = pathname.split('/')
  if 'reftest' in pieces:
    index = pieces.index('reftest') + 1
    name = "/".join(pieces[index:])
  elif 'xpcshell' in pieces:
    index = pieces.index('xpcshell') + 1
    name = "/".join(pieces[index:])
  else:
    name = pathname  
  note = ''
  p = f = t = 0
  
  if outcome == 'TEST-PASS':
    p = 1
    if name not in tests:
      tests[name] = dict({'pass': p, 'fail': f, 'todo': t, 'note': []})
    else:
      tests[name]['pass'] = tests[name]['pass'] + p
  elif outcome == 'TEST-KNOWN-FAIL':
    t = 1
    note = line[2]
    if name not in tests:
      tests[name] = dict({'pass': p, 'fail': f, 'todo': t, 'note': [note.strip()]})
    else:
      tests[name]['todo'] = tests[name]['todo'] + t
      tests[name]['note'].append(note.strip())
  else:
    f = 1
    note = line[2]
    if name not in tests:
      tests[name] = dict({'pass': p, 'fail': f, 'todo': t, 'note': [note.strip()]})
    else:
      tests[name]['fail'] = tests[name]['fail'] + f
      tests[name]['note'].append(note.strip())

def parseLog(filename):
  
  doc = {}
  contentAll = ''
  try:       
    inFile = open(filename, 'r')
  except IOError:
    print "Can't open " + filename
  else:
    contentAll = inFile.read()
    inFile.close()
  
  if reStatus.search(contentAll) != None:
    tests.clear()
    print inFile
    
    doc = { 
      "build": getBuildId(contentAll), 
      "product": getProduct(contentAll), 
      "os": getOs(contentAll), 
      "testtype": getTestType(contentAll)}
    
    contentByLine = []
    try:       
      inFile = open(filename, 'r')
    except IOError:
      print "Can't open " + filename
    else:
      contentByLine = inFile.readlines()
      inFile.close()
      
      for line in contentByLine:
        if reStatus.search(line) != None:
          getTestDetail(line)      
      doc['tests'] = tests
      doc['timestamp'] = str(datetime.datetime.now())
      print "Done parsing " + filename
  return doc  

def save(data):
  
  db = couchquery.CouchDatabase("http://pythonesque.org:5984/fennec_test1", cache=Cache())
  saved = False
  try:
    starttime = datetime.datetime.now()
    db.create(data)
    finishtime = datetime.datetime.now()
    print finishtime - starttime
    saved = True
  except CouchDBException, e:
    print "Error occurred while sending data :" + str(e)
  finally:
    return saved

def main():
  
  usage = "usage: %prog [options] arg"
  parser = OptionParser(usage)
  parser.add_option("-f", "--file", action="store", type="string", dest="filename", help="read data from FILENAME")
  
  (options, args) = parser.parse_args()
  
  if options.filename == None:
    print "Please supply a filename (--help)"
  else:
    result = parseLog(options.filename)
    if result == None:
      print "Failed uploading results"
    else:
      if save(result) is False:
        print "Failed uploading results"
      else:
        print "Done uploading results"

class Cache(dict):
    def __init__(self, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        setattr(self, 'del', lambda *args, **kwargs: dict.__delitem__(*args, **kwargs) )
    get = lambda *args, **kwargs: dict.__getitem__(*args, **kwargs)
    set = lambda *args, **kwargs: dict.__setitem__(*args, **kwargs)
    
if __name__ == "__main__":
  result = main()