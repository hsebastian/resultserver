#dependencies
import simplejson as json
from couchdb import Server, Database

def main():
  views = dict()
  
  # specify the views: name, map, and reduce if it's present
  
  views['getProducts'] = {
  'map': 
"""
function(doc){
  emit(doc.product, 1);
}
""",
  'reduce': 
"""
function(keys, values, rereduce){
  return sum(values);
}
"""
  }

  views['getTesttypes'] = {
  'map': 
"""
function(doc){
  emit(doc.testtype, 1);
}
""",
  'reduce': 
"""
function(keys, values, rereduce){
  return sum(values);
}
"""
  }
  
  views['getOs'] = {
  'map': 
"""
function(doc){
  emit(doc.os, 1);
}
""",
  'reduce': 
"""
function(keys, values, rereduce){
  return sum(values);
}
"""
  }
  
  views['getNumTests'] = {
  'map': 
"""
function(doc) {
  var i = 0;
  for(test in doc.tests) 
    i++; 
  emit([doc.build, doc.os, doc.testtype], {tests: i});
}
"""
  }
  
  views['getMetadata'] = {
  'map': 
"""
function(doc) {
  emit(doc.build, 
    { metadata: doc.product + ',' + 
                doc.os + ',' + 
                doc.testtype + ',' + 
                doc.timestamp
    }
  );
}
"""
  }
  
  views['getResults'] = {
  'map': 
"""
function (doc) { emit([doc.testtype, doc.build], doc.tests);}
""",
  'reduce':
"""
function (key, value) {

  //for some reason key is [key, doc._id]
  //so emit([doc.testtype, doc.build], doc.tests)
  //doc.build = key[0][0][1]
  if (parseInt(key[0][0][1]) > 0) {
    retval = {};
    retval["pass"] = 0;
    retval["fail"] = 0;
    retval["todo"] = 0;
    for (v in value[0]) {
      test = value[0][v];
      retval.pass = retval.pass + test.pass;
      retval.fail = retval.fail + test.fail;
      retval.todo = retval.todo + test.todo;    
    }
    return retval;
  }
  return {};
}
"""
  }
  

  # specify the language
  
  language = 'javascript'
  
  # specify design document name
  
  designdocname = '_design/results'

  db = Database('http://happyhans.couch.io/tests')
  db.resource.http.add_credentials('happyhans', 'happyhanshappyhans')
  
  if (db[designdocname] != None):
    del db[designdocname]  
  db[designdocname] = dict({'language': language, 'views': views})
  
  views.clear()
  
  print "done uploading views"

if __name__ == "__main__":
  result = main()
