# dependencies 
import os
import simplejson as json
import log_parser

this_directory = os.path.abspath(os.path.dirname(__file__))
testfixtures_dir = os.path.join(this_directory, 'testfixtures')

def main():
  print json.dumps(log_parser.parseLog("hello.js"), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "test_notestresults.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "test_onetestresult.htm")), indent=2)

if __name__ == "__main__":
  result = main()