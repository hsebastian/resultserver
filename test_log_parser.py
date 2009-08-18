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
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "test_nobuildid.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "test_twobuildids.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "testbuild1.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "testbuild2.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "testbuild3.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "testbuild4.htm")), indent=2)
  print json.dumps(log_parser.parseLog(os.path.join(testfixtures_dir, "testbuild5.htm")), indent=2)
if __name__ == "__main__":
  result = main()