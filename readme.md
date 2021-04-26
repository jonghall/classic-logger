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
Text based Log output
````
2021-04-26 07:53:05,096 - root - INFO - Login Successful IBM579583
2021-04-26 07:53:05,097 - root - INFO - Login Successful IBM579583
2021-04-26 08:05:21,317 - root - INFO - Login Successful IBM579583
2021-04-26 08:15:39,345 - root - INFO - Power On virtualserver01.Jonathan-Hall-s-Account.cloud
2021-04-26 08:16:40,637 - root - INFO - Login Successful IBM579583
2021-04-26 08:18:43,037 - root - INFO - Network Component(s) Updated With Security Group allow_all_from_home
2021-04-26 08:18:43,037 - root - INFO - Security Group Added virtualserver01.Jonathan-Hall-s-Account.cloud
2021-04-26 08:21:16,413 - root - INFO - Cancel Service virtualserver01.Jonathan-Hall-s-Account.cloud
2021-04-26 08:21:47,002 - root - INFO - Disable Port virtualserver01.Jonathan-Hall-s-Account.cloud- Public Interfaces
2021-04-26 08:21:47,002 - root - INFO - Disable Port virtualserver01.Jonathan-Hall-s-Account.cloud- Private Interfaces
2021-04-26 08:21:47,002 - root - INFO - Power Off virtualserver01.Jonathan-Hall-s-Account.cloud
2021-04-26 08:21:47,003 - root - INFO - Disable Port virtualserver01.Jonathan-Hall-s-Account.cloud- Public Interfaces
2021-04-26 08:21:47,003 - root - INFO - Disable Port virtualserver01.Jonathan-Hall-s-Account.cloud- Private Interfaces
````
Meta Data Logged with output.  (Power On virtualServer01.Jonathan-Hall-s-Account.cloud)
````
{
  "accountId": 579583,
  "createDate": "2021-04-26T08:14:38-05:00",
  "dedicatedAccountHostOnlyFlag": false,
  "domain": "Jonathan-Hall-s-Account.cloud",
  "fullyQualifiedDomainName": "virtualserver01.Jonathan-Hall-s-Account.cloud",
  "hostname": "virtualserver01",
  "id": 119528632,
  "lastPowerStateId": "",
  "lastVerifiedDate": "",
  "maxCpu": 1,
  "maxCpuUnits": "CORE",
  "maxMemory": 1024,
  "metricPollDate": "",
  "modifyDate": "2021-04-26T08:15:35-05:00",
  "placementGroupId": "",
  "provisionDate": "",
  "startCpus": 1,
  "statusId": 1001,
  "typeId": 6,
  "uuid": "88978a9e-72be-2d90-c69f-4cb6624f46a5",
  "status": {
    "keyName": "ACTIVE",
    "name": "Active"
  },
  "hostName": "virtualserver01",
  "image": "Stock Image",
  "privateVlan": "",
  "publicVlan": 1523,
  "primaryBackendIpAddress": "10.187.101.97",
  "primaryIpAddress": "",
  "frontendRouter": "fcr01a.dal13",
  "backendRouter": "bcr01a.dal13",
  "datacenter": "dal13"
}
````

**Links**
Similiar Pyhon Event Log example
* https://sldn.softlayer.com/python/event_log/

IBM Classic API's used
* https://sldn.softlayer.com/reference/services/SoftLayer_Event_Log/
* https://sldn.softlayer.com/reference/services/SoftLayer_Account/getVirtualGuests/
* https://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/
