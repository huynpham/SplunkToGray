# SplunkToGray

This is a different implementation of ImRaptor's script.

It uses Splunk's Python SDK export function instead of oneshot.  Export has the benefit of avoiding pagination issues.
Recommend using nohup to run in background: nohup python SplukToGray.py > nohup_SplunkToGray.out 2>&1&



Purpose:
Export Splunk logs and send them to Graylog.

You will need a couple of python libraries to get started:

1) Splunk Python SDK (http://dev.splunk.com/python)

2) Python Requests



They can be installed with pip

* pip install splunk-sdk
* pip install requests
