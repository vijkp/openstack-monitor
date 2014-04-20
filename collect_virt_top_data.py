#!/usr/bin/python

"""
Collect network tx/rx stats from Virtual Machines
"""

import libvirt
import sys
import os
import subprocess
import tokenize
import re
import time
import calendar
import datetime
import csv

def get_file_name(string):
    cur_time = time.gmtime()
    filename = str(cur_time.tm_year) + "_" + str(cur_time.tm_mon) + "_" + str(cur_time.tm_mday) + "_" + string + ".csv"
    return filename

def save_to_file(outlist, filesuffix):
    outputfile = get_file_name(filesuffix)
    output = csv.writer(open(outputfile, 'a+'), delimiter=',', quotechar='|')
    output.writerow(outlist)

def save_all_stats(tokens):
    memfile = "mem_stats"
    cpufile = "cpu_stats"
    diskiofile = "disk_io_stats"
    netfile    = "net_io_stats"
    # ID S RDRQ WRRQ RXBY TXBY %CPU %MEM   TIME    NAME 
    instance_id = tokens[0]
    read_queue  = tokens[2]
    write_queue = tokens[3]
    rx_bytes    = tokens[4]
    tx_bytes    = tokens[5]
    cpu_percent = tokens[6]
    mem_percent = tokens[7]
    vm_time     = tokens[8]
    instance_name = tokens[9]
    vcpus = 1 # get it from libvirt
    save_to_file([timestamp, hostname, instance_id, instance_name, cpu_percent, vcpus, hostcpus, vm_time], cpufile)
    save_to_file([timestamp, hostname, instance_id, instance_name, mem_percent, hostmem], memfile)
    save_to_file([timestamp, hostname, instance_id, instance_name, rx_bytes, tx_bytes], netfile) 
    save_to_file([timestamp, hostname, instance_id, instance_name, read_queue, write_queue], diskiofile) 

def parse_each_line(line):
    global timestamp
    global hostname
    global hostmem
    global hostcpus
    
    tokens = line.split()
    if len(tokens) < 8:
        return
    if tokens[0] == "virt-top":
        dt1 = datetime.datetime.strptime(tokens[2], "%H:%M:%S").time()
        dt2 = datetime.datetime.combine(datetime.date.today(), dt1)
        timestamp = int(time.mktime(dt2.timetuple()))
        hostname = tokens[4]
        hostmem = tokens[8]
        hostcpus = tokens[6]
    elif tokens[0] == "ID":
        return
    else:
        save_all_stats(tokens)

timestamp = -1
hostname = ""
hostmem  = ""
hostcpus = ""

# Globals
# subprocess to start virt-top
def collect_virt_top_data():
    virt_top_command = ['virt-top', '-d', '5', '--script', '--stream', '-n', '10']
    virt_top_proc = subprocess.Popen(virt_top_command,stdout=subprocess.PIPE)
    virt_top_output_processing = False
   
    # process each line of the output
    while True:
        line = virt_top_proc.stdout.readline()
        if line != '':
            parse_each_line(line)
        else:
            break


