#!/usr/bin/python

"""
Code to extract Disk utilization in VMs
"""
import socket
import subprocess 
import time
import csv
from time import gmtime

#Get hostname
def get_host_name():
    if socket.gethostname().find('.')>=0:
        hostname = socket.gethostname()
    else:
        hostname = socket.gethostbyaddr(socket.gethostname())[0]
    return hostname

def get_file_name(string):
    cur_time = gmtime()
    filename = str(cur_time.tm_year) + "_" + str(cur_time.tm_mon) + "_" + str(cur_time.tm_mday) + "_" + string + ".csv"
    return filename

#Create/Open file for logging
def writeToFile(log):
    logfile = csv.writer(open(get_file_name("disk_stats"), 'a+'), delimiter=',', quotechar='|')
    logfile.writerow(log)

def collect_disk_stats():
    #Get hostname
    hostname = get_host_name()    

    #Get current timestamp
    timestamp = int(time.time())

    #Get output of virt-df command
    out = subprocess.check_output("virt-df --csv", shell=True)    
    lines = out.split('\n')
    for i in range(1, len(lines) - 1):
        stats = lines[i].split(',')
        log = [timestamp, hostname, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]]
        writeToFile(log)

#Calling code
collect_disk_stats()
