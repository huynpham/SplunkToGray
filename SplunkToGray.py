# Script to export log files from Splunk to Graylog using Splunk SDK  
# This script is written for linux systems, modify as necessary for your own OS.
 
# Imports
import os
import time
import splunklib.results as results
import splunklib.client as client
import requests as requests
import json

# Uncomment if you need to debug
"""
import logging
# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1
# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

# Base configuration
# Splunk search info
HOST = ""  # Splunk server
PORT = 8089  # Splunk REST API port
USERNAME = ''
PASSWORD = ''

#  Graylog server info
graylogPath = "http://graylog:12201/gelf"  # Address of a configured GELF HTTP Input on a Graylog server

# Splunk export search parameters
# For more details, go here: http://dev.splunk.com/view/python-sdk/SP-CAAAEE5

# latest_time_filename is the name of the file containing the latest time, which should be in Unix time
# If the file does not exist, the default will be the current time in Unix time
# The file is used to keep track of our current progress in case the script exits for any reason
latest_time_filename = "latest_time"

# earliest_time should be in unix time
earliest_time = ""

# Define search parameters
# "*" means to search everything
# "| eval timestamp=_time" returns the log timestamp,_time, as unix time so we can easily export to graylog
# _time is the timestamp in the log, while _indextime is the time that Splunk indexed the log. 
searchquery_export = "search * | eval timestamp=_time"

# open file to get the time where we left off
if os.path.exists(latest_time_filename):
    # if the file is empty, set the latest_time to the current time
    if os.stat(latest_time_filename).st_size == 0:
        with open(latest_time_filename, 'w') as f:
            latest_time = str(time.time())
            f.write(latest_time)
    # read the file and set the latest_time
    else:
        with open(latest_time_filename, 'r') as f:
            latest_time = f.readline()
            latest_time = latest_time.strip('\n')
else:
    # if file does not exist, create file and set the latest_time to the current time
    with open(latest_time_filename, 'w') as f:
        latest_time = str(time.time())
        f.write(latest_time)



print "Latest Time is: {}".format(latest_time)
print "Earliest Time is: {}".format(earliest_time)

service = client.connect(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)

# define the export parameters 
kwargs_export = {"earliest_time": earliest_time,
                 "latest_time": latest_time,
                 "search_mode": "normal"}


exportsearch_results = service.jobs.export(searchquery_export, **kwargs_export)

# Get the results and display them using the ResultsReader
reader = results.ResultsReader(exportsearch_results)
for result in reader:
    if isinstance(result, dict):
        # convert fields from Splunk into Graylog
        # If your _raw logs are very large, you can set "full_message": result["_raw"], as well, but keep in mind Graylog requires the short_message field so you would be doubling your storage size
        # http://docs.graylog.org/en/2.2/pages/gelf.html
        gelf = {"version": "1.1",
                "host": result["host"],
                "_source_file": result["source"],
                "short_message": result["_raw"],
                "splunk_indextime": result["_indextime"],
                "timestamp": result["timestamp"]}

        latest_time = str(result["timestamp"])
        with open(latest_time_filename, 'w') as f:
            f.write(latest_time)

        # Send to graylog
        requests.post(graylogPath, json=gelf)

    elif isinstance(result, results.Message):
        # Diagnostic messages may be returned in the results
        print "Message: %s" % result

