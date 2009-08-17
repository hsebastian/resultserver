# dependencies 
import os
import re
import fnmatch
import simplejson as json
import datetime
#import couchdb
from couchdb import Server

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
logFiles = []
tests = dict()

def findFiles(dir, pattern):
  for file in os.listdir(dir):
    if os.path.isdir(dir + file):
      findFiles(dir + file + "/", pattern)
    else:
      if fnmatch.fnmatch(file, pattern):
        logFiles.append(dir + file)

# def getBuildDate(text):
  # label = r'tinderbox: builddate: '
  # regex = re.compile(label + r'.*')
  # result = regex.search(text).group(0)
  # result = result[len(label):len(result)]
  # return result

def getBuild(text):
  label = r'tinderbox: build: '
  regex = re.compile(label + r'.*')
  result = regex.search(text)
  if result != None:
    return (result.group(0))[len(label):len(result.group(0))]
  else:
    return 'no-info'

# note: BUILDID appears twice with different values in the log
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
  return (re.split(' +', getBuild(text)))[0]

def getTestType(text):
  splitted = re.split(' +', getBuild(text))
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

def dbSend(data):

  import httplib2
  h = httplib2.Http(".cache")
  h.add_credentials('happyhans', 'happyhanshappyhans')
  h.request("http://happyhans.couch.io/tests1",
    "POST", body=json.dumps(data),
    headers={'content-type':'application/json'} )

# note: xpcshell tests run twice or appears twice in the log making the counts double
def main():
  
  # i = 0 # for outFile
  findFiles("C:/Documents and Settings/Hans Sebastian/Desktop/samples/", "*_xpc.htm")
  
  for fileName in logFiles:
    
    contentAll = ''
    try:       
      inFile = open(fileName, 'r')
    except IOError:
      print "Can't open " + fileName
    else:
      contentAll = inFile.read()
      inFile.close()
    
    if reStatus.search(contentAll) != None:
      tests.clear()
      # i += 1 # for outFile
      print inFile
      
      doc = dict({ 
        "build": getBuildId(contentAll), 
        "product": getProduct(contentAll), 
        "os": getOs(contentAll), 
        "testtype": getTestType(contentAll)})
      
      contentByLine = []
      try:       
        inFile = open(fileName, 'r')
      except IOError:
        print "Can't open " + fileName
      else:
        contentByLine = inFile.readlines()
        inFile.close()
        
        for line in contentByLine:
          if reStatus.search(line) != None:
            getTestDetail(line)      
        doc['tests'] = tests
        doc['timestamp'] = str(datetime.datetime.now())
        
        # outputFile = "C:/_Code/python/output" + str(i) + ".html"
        # outFile = open(outputFile, 'w')
        # outFile.write(json.dumps(doc, indent=2, sort_keys=True))
        # outFile.close()
        
        dbSend(doc)

  print "done uploading results"

if __name__ == "__main__":
  result = main()