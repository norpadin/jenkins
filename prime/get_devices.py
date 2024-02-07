#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import requests
import json
from argparse import ArgumentParser
import pandas as pd

requests.packages.urllib3.disable_warnings()
from pi_config import PI, USER, PASSWORD

BASE="https://%s:%s@%s/webacs/api/v4/" %(USER,PASSWORD,PI)

class NoDeviceFound(Exception):
    pass

dev = []
gru = []
sit = []
udg = []
dev_gru = []

def all_devices():
    print ("\nGetting all devices")
    print ("Device ID", "  Device Name", "               IP address", "  Software Type", "  Software Version")
    result = requests.get(BASE + "data/Devices.json?.full=true&.sort=ipAddress", verify=False)
    result.raise_for_status()
    for device in result.json()['queryResponse']['entity']:
        print (device['devicesDTO']['@id'], '   ', device['devicesDTO']['deviceName'], '   ', device['devicesDTO']['ipAddress'], '  ', device['devicesDTO']['softwareType'], '          ', device['devicesDTO']['softwareVersion'])
        dev.append([device['devicesDTO']['@id'], device['devicesDTO']['deviceName'], device['devicesDTO']['ipAddress'], device['devicesDTO']['softwareType'], device['devicesDTO']['softwareVersion']])
    df = pd.DataFrame(dev)
    df = df.replace(r'\s+', '', regex=True)
    # Save the dataframe to a CSV file
    df.to_csv('bbva_devices_database.csv', index=False, header=False)

def all_sites():
    print ("\nGetting all sites")
    print ("{0:7s} {0:11s}".format("Site ID", "Site Name"))
    result = requests.get(BASE + "/op/groups/userDefinedGroups.json?groupType=NETWORK_DEVICE", verify=False)
    result.raise_for_status()
    for site in result.json()['mgmtResponse']['grpDTO']:
        print (site['groupId'], ' ', site['groupName'])
        sit.append([site['groupId'], site['groupName']])
    df = pd.DataFrame(sit)
    df = df.replace(r'\s+', '', regex=True)
    # Save the dataframe to a CSV file
    df.to_csv('bbva_sites_database.csv', index=False, header=False)

def devices_in_groups():
    print('\n')
    df = pd.DataFrame(dev)
    for ind in df.index:
        dev_id = df[0][ind]
        result = requests.get(BASE + "data/DevicesWithGroups/" + str(dev_id) + ".json", verify=False)
        result.raise_for_status()
        for dwg in result.json()['queryResponse']['entity']:
            udg = dwg['devicesWithGroupsDTO']['groups']['group']
            for row in udg:
                if row['fullName'] == "Location/All Locations":
                    dev_gru.append([dev_id, row['id']])
    df = pd.DataFrame(dev_gru)
    df = df.replace(r'\s+', '', regex=True)
    # Save the dataframe to a CSV file
    df.to_csv('bbva_devices_in_groups_database.csv', index=False, header=False)

def all_groups():
    print ("Getting all groups")
    result = requests.get(BASE + "/op/groups/sites.json", verify=False)
    result.raise_for_status()
    print ("{0:11s} {1:16s} {2:11s}".format("Group ID", "Group Name", "# Devices"))
    for device in result.json()['mgmtResponse']['siteOpDTO']:
        print ('{0:8} {1:16} {2:8}'.format(device['groupId'], device['groupName'], device['deviceCount']))
        gru.append([device['groupId'], device['groupName'], device['deviceCount']])
    df = pd.DataFrame(gru)
    df = df.replace(r'\s+', '', regex=True)
    # Save the dataframe to a CSV file
    df.to_csv('bbva_groups_database.csv', index=False, header=False)

if __name__ == "__main__":
    all_devices()
    all_groups()
    devices_in_groups()
    # all_sites()
