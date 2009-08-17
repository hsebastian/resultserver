# dependencies 
import os
import random
import simplejson as json
import datetime
import couchquery
# from couchquery import CouchDocument

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
    # "notes": [note1, note2, note3, ...]
# }

def main():
  
  document = 'TestingForDevelopment'
  products = ['Fennec', 'Firefox']
  platforms = ['Maemo', 'Win', 'Linux', 'Mac']
  testtypes = ['crashtests', 'mochitests', 'xpcshell', 'reftests']
  build = timestamp = ''
  
  db = couchquery.CouchDatabase("http://pythonesque.org:5984/fennec_test", cache=Cache())
  
  # create documents
  doccount = random.randint(500, 600)
  for i in range(0, doccount):
    
    # create metadata
    buildstructure = {}
    build = timestamp = str(datetime.datetime.now())
    buildstructure['build'] = build
    buildstructure['product'] = 'product' + str(random.randint(1, 2))
    buildstructure['os'] = 'platform' + str(random.randint(1, 2))
    buildstructure['testtype'] = 'testtype' + str(random.randint(1, 2))
    buildstructure['timestamp'] = build
    buildstructure['document'] = document
    
    # create tests
    tests = {}
    offset = random.randrange(1, 5)
    testcount = random.randint(100, 500)
    for x in range(0, testcount):
      failcount = random.randint(0, 10)
      todocount = random.randint(0, 3)
      notes = []
      for y in range(0, (failcount + todocount)):
        notes.append("This test should have returned TRUE but returned FALSE")
      tests['test' + str(offset + x) + '.js'] = {
        'pass': random.randint(0, 5),
        'fail': failcount,
        'todo': todocount,
        'note': notes
      }
    print json.dumps(buildstructure, indent=2)
    buildstructure['tests'] = tests
  
    # outputFile = "C:/_Code/python/outputdata" + str(i) + ".html"
    # outFile = open(outputFile, 'w')
    # outFile.write(json.dumps(buildstructure, indent=2))
    # outFile.close()  
    
    db.create(buildstructure)
  
  print "done uploading results"

class Cache(dict):
    def __init__(self, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        setattr(self, 'del', lambda *args, **kwargs: dict.__delitem__(*args, **kwargs) )
    get = lambda *args, **kwargs: dict.__getitem__(*args, **kwargs)
    set = lambda *args, **kwargs: dict.__setitem__(*args, **kwargs)
    
if __name__ == "__main__":
  result = main()