#!/usr/bin/env python3
# eventLogs.py - A script to export IBM Cloud Classic Infrastructure events to external log source
# Author: Jon Hall
# Copyright (c) 2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Script reads logging.json for log handler configuration
# to use with LogDNA set environment variable logdna_ingest_key = apikey.
#
#Log Items forwarded to log handlers by default
#
# recentLogs(lastdate) - all events since last date.
# bmLogs() - All BareMetal and Server Logs
# cciLogs() - All Cloud Compute Instance (Virtual Server) Logs)
# systemLogs() -  All System Logs
# loginLogs() - All Login Events
#:......................:
#:        types         :
#:......................:
#:       Account        :
#:         CDN          :
#:         User         :
#: Bare Metal Instance  :
#:  API Authentication  :
#:        Server        :
#:         CCI          :
#:        Image         :
#:      Bluemix LB      :
#:       Facility       :
#: Cloud Object Storage :
#:    Security Group    :
#:.....................

import SoftLayer, json, os, time
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import logging, logging.config
from logdna import LogDNAHandler

class event_logs():
    def __init__(self):
        self.client = SoftLayer.Client()
        #debugger = SoftLayer.DebugTransport(self.client.transport)
        #self.client.transport = debugger

    def recentLogs(self, lastdate):
        filterdate = datetime.fromisoformat(lastdate)+timedelta(seconds=1)
        _filter = {
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [
                    {'name': 'date', 'value': [filterdate.strftime("%Y-%m-%dT%H:%M:%S")]}
                ]
            }
        }
        for event in self.getAllObjects(_filter):
            printLogs(event)

    def systemLogs(self):

        _filter = {'userType': {'operation': 'SYSTEM'}}
        for event in self.getAllObjects(_filter):
            printLogs(event)

    def loginLogs(self):
        _filter = {
            'eventName': {
                'operation': '^= Login'
            }
        }
        for event in self.getAllObjects(_filter):
            printLogs(event)

    def cciLogs(self):
        _filter = {
            'objectName': {
                'operation': '^= CCI'
            }
        }
        for event in self.getAllObjects(_filter):
            printLogs(event)

    def bmLogs(self):
        _filter = {
            'objectName': {
                'operation': '^= Server'
            }
        }
        for event in self.getAllObjects(_filter):
            printLogs(event)

    def allLogs(self):
        for event in self.getAllObjects(None):
            printLogs(event)

    def getAllObjects(self, _filter, limit=100, offset=0):
        """Pages through all results from the Event_Log. This might take long time."""
        notDone = True
        newdate = lastdate
        while notDone:
            events = self.client.call('SoftLayer_Event_Log', 'getAllObjects', filter=_filter, limit=limit,
                                      offset=offset)
            print("Getting logs since %s, %s from getAllObjects, offset = %s" % (lastdate, len(events), offset))

            for event in events:
                if event["eventCreateDate"] > newdate:
                    newdate = event["eventCreateDate"]
                yield event
            if len(events) < limit:
                notDone = False
            offset = offset + limit
        tempfile = open(".lastdate", "w")
        tempfile.write(newdate)
        tempfile.close()

    def getServer(self, id):
        try:
            hardwareServer = self.client.call('SoftLayer_Hardware_Server', 'getObject', id=id,
                                            mask='hostname, memoryCapacity, processorCoreAmount, fullyQualifiedDomainName, datacenter, primaryIpAddress, primaryBackendIpAddress, networkVlans, frontendRouters, backendRouters')
        except SoftLayer.SoftLayerAPIError as e:
            logging.warning("SoftLayer_Hardware_Server::getObject(): %s, %s" % (e.faultCode, e.faultString))
            return {}

        hostName = hardwareServer['hostname']
        fullyQualifiedDomainName = hardwareServer['fullyQualifiedDomainName']
        processorCoreAmount = hardwareServer['processorCoreAmount']
        memory = hardwareServer['memoryCapacity']

        if "networkVlans" in hardwareServer:
            publicVlan = hardwareServer['networkVlans'][0]['vlanNumber']
            if len(hardwareServer['networkVlans']) > 1:
                privateVlan = hardwareServer['networkVlans'][1]['vlanNumber']
            else:
                privateVlan = ""
        else:
            privateVlan = ""
            publicVlan = ""

        if "backendRouters" in hardwareServer:
            if len(hardwareServer['backendRouters']) > 1:
                backendRouter = hardwareServer['backendRouters'][0]['hostname']
            else:
                backendRouter = hardwareServer['backendRouters']['hostname']
        else:
            backendRouter = ""

        if "frontendRouters" in hardwareServer:
            if len(hardwareServer['frontendRouters']) > 1:
                frontendRouter = hardwareServer['frontendRouters'][0]['hostname']
            else:
                frontendRouter = hardwareServer['frontendRouters']['hostname']

        if "datacenter" in hardwareServer:
            datacenter = hardwareServer['datacenter']['name']
        else:
            datacenter = ""

        if "primaryBackendIpAddress" in hardwareServer:
            primaryBackendIpAddress = hardwareServer['primaryBackendIpAddress']
        else:
            primaryBackendIpAddress = ""

        if "primaryIpAddress" in hardwareServer:
            primaryIpAddress = hardwareServer['primaryIpAddress']
        else:
            primaryIpAddress = ""

        return {"hostName": hostName,
                "fullyQualifiedDomainName": fullyQualifiedDomainName,
                "cores": processorCoreAmount,
                "memory": memory,
                "privateVlan": privateVlan,
                "publicVlan": publicVlan,
                "primaryBackendIpAddress": primaryBackendIpAddress,
                "primaryIpAddress": primaryIpAddress,
                "frontendRouter": frontendRouter,
                "backendRouter": backendRouter,
                "datacenter": datacenter
                }

    def getVirtualGuest(self, id):
        try:
            virtualGuest = self.client.call('SoftLayer_Virtual_Guest', 'getObject', id=id,
                                            mask='hostname, maxMemory, maxCpu, fullyQualifiedDomainName, datacenter, primaryIpAddress, primaryBackendIpAddress, networkVlans, frontendRouters, backendRouters, blockDeviceTemplateGroup')
        except SoftLayer.SoftLayerAPIError as e:
            logging.warning("SoftLayer_VirtualGuest::getObject(): %s, %s" % (e.faultCode, e.faultString))
            return {}

        hostName = virtualGuest['hostname']
        fullyQualifiedDomainName = virtualGuest['fullyQualifiedDomainName']
        maxCpu = virtualGuest['maxCpu']
        maxMemory = virtualGuest['maxMemory']

        if 'blockDeviceTemplateGroup' in virtualGuest:
            templateImage = virtualGuest['blockDeviceTemplateGroup']['name']
        else:
            templateImage = "Stock Image"

        if "networkVlans" in virtualGuest:
            publicVlan = virtualGuest['networkVlans'][0]['vlanNumber']
            if len(virtualGuest['networkVlans']) > 1:
                privateVlan = virtualGuest['networkVlans'][1]['vlanNumber']
            else:
                privateVlan = ""
        else:
            privateVlan = ""
            publicVlan = ""

        if "backendRouters" in virtualGuest:
            if len(virtualGuest['backendRouters']) > 1:
                backendRouter = virtualGuest['backendRouters'][0]['hostname']
            else:
                backendRouter = virtualGuest['backendRouters']['hostname']
        else:
            backendRouter = ""

        if "frontendRouters" in virtualGuest:
            frontendRouter = virtualGuest['frontendRouters']['hostname']
        else:
            frontendRouter = ""

        if "datacenter" in virtualGuest:
            datacenter = virtualGuest['datacenter']['name']
        else:
            datacenter = ""

        if "primaryBackendIpAddress" in virtualGuest:
            primaryBackendIpAddress = virtualGuest['primaryBackendIpAddress']
        else:
            primaryBackendIpAddress = ""

        if "primaryIpAddress" in virtualGuest:
            primaryIpAddress = virtualGuest['primaryIpAddress']
        else:
            primaryIpAddress = ""

        return {"hostName": hostName,
                "fullyQualifiedDomainName": fullyQualifiedDomainName,
                "maxCpu": maxCpu,
                "maxMemory": maxMemory,
                "image": templateImage,
                "privateVlan": privateVlan,
                "publicVlan": publicVlan,
                "primaryBackendIpAddress": primaryBackendIpAddress,
                "primaryIpAddress": primaryIpAddress,
                "frontendRouter": frontendRouter,
                "backendRouter": backendRouter,
                "datacenter": datacenter
                }

    def debug(self):
        for call in self.client.transport.get_last_calls():
            print(self.client.transport.print_reproduceable(call))


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'):

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        if "handlers" in config:
            if "logdna" in config["handlers"]:
                config["handlers"]["logdna"]["key"] = os.getenv("logdna_ingest_key")
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def printLogs(event):
    timestamp = datetime.fromisoformat(event["eventCreateDate"]).strftime('%s')
    meta = {}
    if 'resource' in event:
        meta.update(event['resource'])


    if event["metaData"] != "":
        metaData = {"eventChange": event['metaData']}
        try:
            meta.update(metaData)
        except:
            logging.error("Error parsing metaData: %s" % event['metaData'])

    if "label" in event:
        label = event["label"]
    else:
        if event["eventName"] == "Host Authorization":
            label = event["ipAddress"]
        else:
            label = ""
    if event['objectName'] == "CCI" and (event['eventName'] == "Power On"  or
                                         event['eventName'] == "Reboot" or event['eventName'] == "Rename"):
        main = event_logs()
        cci = main.getVirtualGuest(event["objectId"])
        meta.update(cci)

    if event['objectName'] == "Server" and (event['eventName'] == "Power On" or event['eventName'] == "IPMI On"  or
                                            event['eventName'] == "Reboot" or event['eventName'] == "Rename"):
        main = event_logs()
        server = main.getServer(event["objectId"])
        meta.update(server)

    logging.info(f"{event['eventName']} {label}", {"timestamp": timestamp, "meta": meta})

if __name__ == "__main__":
    setup_logging()
    while True:
        if os.path.exists('.lastdate'):
            f = open('.lastdate')
            lastdate = f.readlines()[0].strip()
        else:
            lastdate = datetime.now(tzlocal()).isoformat()
        main = event_logs()
        main.recentLogs(lastdate)
        time.sleep(30)
