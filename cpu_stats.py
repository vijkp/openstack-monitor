#!/usr/bin/python

"""
Code to extract CPU utilization percentage
"""

import libvirt
import sys
import os
import subprocess 
import re

def convertToSeconds(strTime):
    #Split the input string as dd-hh:mm:ss
    time = re.split(':|-',strTime)
   
    #Initialize uptimeSec as a double
    uptimeSec = 0.0
    if len(time) == 1:
        uptimeSec = int(time[0])
    if len(time) == 2:
        uptimeSec = int(time[0])*60 + int(time[1])
    if len(time) == 3:
        uptimeSec = int(time[0])*3600 + int(time[1])*60 + int(time[2])
    if len(time) == 4:
        uptimeSec = int(time[0])*24*3600 + int(time[1])*3600 + int(time[2])*60 + int(time[3])
    
    #Uptime has to be in nanoseconds
    return uptimeSec*1000000000.0

#Create/Open file for logging
logFile = open('log_cpu_stats.log','a+')

#Open connection to libvirt
conn = libvirt.openReadOnly(None)
if conn == None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

#Command used: ps -o etime `cat /var/run/libvirt/qemu/$vmid.pid`
uptimeCmdPrefix = "ps -o etime `cat /var/run/libvirt/qemu/"
uptimeCmdSuffix = ".pid`"
domain_list = conn.listAllDomains()
for dl in domain_list:
    dom = conn.lookupByName(dl.name())
    
    #Getting the CPU uptime
    cmd = uptimeCmdPrefix + dl.name() + uptimeCmdSuffix
    out = subprocess.check_output(cmd, shell=True)
    uptimeList = out.split('\n');
    # Uptime always stored as the second element in the list
    uptime = convertToSeconds(uptimeList[1])
    
    #Getting the CPU utilized time
    out = dom.getCPUStats(True)
    dom_cpu_stats = out[0]
    cputime = dom_cpu_stats['cpu_time']

    #Calculating CPU utilization
    cpu_util =  (cputime*100)/uptime

    #Get current timestamp
    timestamp = subprocess.check_output("date +%s", shell=True)
    timestamp = timestamp.translate(None,'\n')
    
    #Log to file
    #vm-id, timestamp, total-uptime, total-cpu_time, cpu utilization
    line = "{},{},{},{},{}".format(dl.name(), timestamp, uptime, cputime, cpu_util)
    line = line + '\n'
    logFile.write(line)


