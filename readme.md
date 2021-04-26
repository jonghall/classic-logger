# **Classic Logger**

Periodically queries the IBM Classic event_log API for recent events.   Virtual Server, Bare Metal, and Server events trigger additional data to be accessed from provisioning data and is included in Log MetaData.

**Assumptions**
* Softlayer SDK (slcli setup) is configured with username and apikey with access to classic event log and billing data.
* logging.json configured with appropriate log handlers
* If using logdna set environment variable (logdna-ingest_key) is LogDna api key

**Usage**


````python eventLog.py

In main program call
        main = event_logs() to intialize

These modules will filter differently 
    recentLogs(lastdate) - all events since last date.
    bmLogs() - All BareMetal and Server Logs
    cciLogs() - All Cloud Compute Instance (Virtual Server) Logs)
    systemLogs() -  All System Logs
    loginLogs() - All Login Events
````


**Links**
Similiar Pyhon Event Log example
* https://sldn.softlayer.com/python/event_log/

IBM Classic API's used
* https://sldn.softlayer.com/reference/services/SoftLayer_Event_Log/
* https://sldn.softlayer.com/reference/services/SoftLayer_Account/getVirtualGuests/
* https://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/
