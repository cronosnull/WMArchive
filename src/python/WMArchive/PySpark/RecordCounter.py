"""
This is example how to write mapper and reducer methods of MapReduce class for
WMArchive/Tools/myspark.py tool. User should perform all necessary actions with
given set of records and return back desired results. Here our mapper process
records from avro files and collect results into a single dictionary. The
reducer will collect results from all mappers and return back aggregated
information.
"""

import re

def parse_spec(spec):
    "Simple spec parser, it converts strings to patterns so far"
    ospec = {}
    for key, val in spec.items():
        if  isinstance(val, basestring):
            ospec[key] = re.compile(val)
        else:
            ospec[key] = val
    return ospec

def match_value(keyval, value):
    "helper function to match value from spec with keyval"
    if hasattr(value, 'pattern'): # it is re.compile pattern
        if value.match(keyval):
            return True
    else:
        if keyval == value:
            return True
    return False

def match(rec, spec):
    "Find if record match given spec"
    for key, val in spec.items():
        if key == 'lfn':
            for lfn in rec['LFNArray']:
                if match_value(lfn, val):
                    return True
        elif key in rec:
            return match_value(rec[key], val)
    return False

class MapReduce(object):
    def __init__(self, ispec=None):
        self.fields = []
        if  ispec:
            if  'spec' in ispec:
                spec = ispec['spec']
            if  'fields' in ispec:
                self.fields = ispec['fields']
            if  'timerange' in ispec:
                del ispec['timerange'] # this is not used for record search
            self.spec = parse_spec(ispec)
        else:
            self.spec = {}

    def mapper(self, records):
        """
        Function to find a record for a given spec during spark
        collect process. It will be called by RDD.map() object within spark.
        The spec of the class is a JSON query which we'll apply to records.
        """
        matches = []
        for rec in records:
            if  not rec:
                continue
            if  not self.spec:
                matches.append(1)
                continue
            elif match(rec, self.spec):
                matches.append(1)
        return matches

    def reducer(self, records, init=0):
        "Simpler reducer which collects all results from RDD.collect() records"
        nrec = 0
        for items in records:
            for rec in items:
                if  not rec:
                    continue
                nrec += 1
        return {"nrecords":nrec}
