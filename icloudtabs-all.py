#!/usr/bin/python
#
# Alfred2 workflow for listing iCloud tabs
#

import os
import subprocess
import shutil
import getpass
import sqlite3



local_user = getpass.getuser()
cloudtabs_db = '/Users/%s/Library/Safari/CloudTabs.db' % local_user

conn = sqlite3.connect(cloudtabs_db)
cursor = conn.cursor()

cursor.execute("select device_uuid, device_name from cloud_tab_devices")
cloud_tab_devices = cursor.fetchall()

# Structure of cloud_tab_devices:
#
# [
#     (device1_uuid, device1_name),
#     (device2_uuid, device2_name)
# ]

cloud_tab_devices_lookup = {}

for device in cloud_tab_devices:
        cloud_tab_devices_lookup[device[0]] = device[1]

cloud_tab_devices_uuid_list = []

for device in cloud_tab_devices:
        cloud_tab_devices_uuid_list.append(device[0])

cursor.execute("select device_uuid, title, url from cloud_tabs")
cloud_tabs = cursor.fetchall()

# Structure of cloud_tabs:
#
# [
#     (device_uuid, tab_title, tab_url),
#     (device_uuid, tab_title, tab_url),
# ]

conn.close()


# Structure needed for all_device_tabs:
#
# all_device_tabs = [
#     ['device1_name', [
#         {'Title': 'device1_tab1_title', 'URL': 'device1_tab1_url'},
#         {'Title': 'device1_tab2_title', 'URL': 'device1_tab2_url'}
#     ]
#     ]
#     ['device2_name', [
#         {'Title': 'device2_tab1_title', 'URL': 'device2_tab1_url'},
#         {'Title': 'device2_tab2_title', 'URL': 'device2_tab2_url'}
#     ]
#     ]
# ]

all_device_tabs = []

for device_uuid in cloud_tab_devices_uuid_list:
    lookup_name = cloud_tab_devices_lookup[device_uuid]
    device_tabs = []
    for tab in cloud_tabs:
        if tab[0] == device_uuid:
            tabinfo = {'Title': tab[1], 'URL': tab[2]}
            device_tabs.append(tabinfo)
    all_device_tabs.append([lookup_name, device_tabs])

# Get local machine's host and computer names to exclude both from the list

hostname_proc = subprocess.Popen(
    ['scutil --get LocalHostName'], stdout=subprocess.PIPE, shell=True)
(hostname_out, hostname_err) = hostname_proc.communicate()
hostname = hostname_out.strip()

computername_proc = subprocess.Popen(
    ['scutil --get ComputerName'], stdout=subprocess.PIPE, shell=True)
(computername_out, computername_err) = computername_proc.communicate()
computername = computername_out.strip()

# Run the os 'open' command for each link found

for device in all_device_tabs:
    device_name = device[0]
    if device_name not in [hostname, computername.decode("utf-8")]:
        for tab in device[1]:
            os.system('open %s' % tab['URL'])
