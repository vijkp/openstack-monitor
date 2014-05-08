#!/usr/bin/python

"""
Collect network tx/rx stats from Virtual Machines
"""
import rrdtool
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
    cur_time = time.localtime()
    filename = str(cur_time.tm_year) + "_" + str(cur_time.tm_mon) + "_" + str(cur_time.tm_mday) + "_" + string + ".csv"
    return filename

def save_to_file(outlist, filesuffix):
    outputfile = get_file_name(filesuffix)
    output = csv.writer(open(outputfile, 'a+'), delimiter=',', quotechar='|')
    output.writerow(outlist)

def convert_to_bytes(size):
    size = str(size)
    if size.endswith("K") or size.endswith("KB"):
        value = (int(size.split("K")[0]))
    elif size.endswith("M") or size.endswith("MB"):
        value = (int(size.split("M")[0]))*1024
    elif size.endswith("G") or size.endswith("GB"):
        value = (int(size.split("G")[0]))*1024*1024
    else:
        value = float(int(size)/1024)
    return value

def save_to_rrdfile(ts, instance_name, statlist, stype):
    if stype == "cpu":
        rrd_file = str(instance_name+'_'+cpufile+'.rrd')
        arguments = "{}:{}".format(ts, statlist[0])
    elif stype == "mem":
        rrd_file = str(instance_name+'_'+memfile+'.rrd')
        arguments = "{}:{}".format(ts, statlist[0])
    elif stype == "disk_io":
        rrd_file = str(instance_name+'_'+diskiofile+'.rrd')
        arguments = "{}:{}:{}".format(ts, convert_to_bytes(statlist[0]), convert_to_bytes(statlist[1]))
    elif stype == "net_io":
        rrd_file = str(instance_name+'_'+netfile+'.rrd')
        arguments = "{}:{}:{}".format(ts, convert_to_bytes(statlist[0]), convert_to_bytes(statlist[1]))
    else:
        print "error: invalid stat type"
        exit(1)
    rrdtool.update(rrd_file, arguments)

def save_all_stats(tokens):
    # ID S RDRQ WRRQ RXBY TXBY %CPU %MEM   TIME    NAME 
    instance_id = tokens[0]
    read_queue  = tokens[2]
    write_queue = tokens[3]
    rx_bytes    = tokens[4]
    tx_bytes    = tokens[5]
    mem_percent = tokens[7]
    vm_time     = tokens[8]
    instance_name = tokens[9]
    vcpus = vcpus_dict[instance_name]
    cpu_percent = float((float(tokens[6])*total_cores)/int(vcpus))
    #save_to_file([timestamp, hostname, instance_id, instance_name, cpu_percent, vcpus, hostcpus, vm_time], cpufile)
    #save_to_file([timestamp, hostname, instance_id, instance_name, mem_percent, hostmem], memfile)
    #save_to_file([timestamp, hostname, instance_id, instance_name, rx_bytes, tx_bytes], netfile) 
    #save_to_file([timestamp, hostname, instance_id, instance_name, read_queue, write_queue], diskiofile) 
    save_to_rrdfile(timestamp, instance_name, [cpu_percent], "cpu")
    save_to_rrdfile(timestamp, instance_name, [mem_percent], "mem")
    save_to_rrdfile(timestamp, instance_name, [rx_bytes, tx_bytes], "disk_io")
    save_to_rrdfile(timestamp, instance_name, [read_queue, write_queue], "net_io")

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
memfile = "mem_stats"
cpufile = "cpu_stats"
diskiofile = "disk_io_stats"
netfile    = "net_io_stats"
time_interval = 5
total_cores = 1

# dictionary to hold vcpus info
vcpus_dict = {}
def create_rrd_files(instance_name):
    start_time = int(time.time())
    timeout = str(2*time_interval)
    rrdtool.create(str(instance_name+'_'+cpufile+'.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:cpu_percent:GAUGE:'+timeout+':0:U',
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks
    rrdtool.create(str(instance_name+'_'+netfile+'.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:rx_bytes:GAUGE:'+timeout+':0:U',
            'DS:tx_bytes:GAUGE:'+timeout+':0:U',
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks
    rrdtool.create(str(instance_name+'_'+diskiofile+'.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:read_queue:GAUGE:'+timeout+':0:U',
            'DS:write_queue:GAUGE:'+timeout+':0:U',
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks
    rrdtool.create(str(instance_name+'_'+memfile+'.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:mem_percent:GAUGE:'+timeout+':0:U',
            'RRA:MAX:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:MAX:0.5:720:240', # 1 hour averages for 5 days
            'RRA:MAX:0.5:12780:10', # 1 day averages for 10 days
            'RRA:MIN:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:MIN:0.5:720:240', # 1 hour averages for 5 days
            'RRA:MIN:0.5:12780:10', # 1 day averages for 10 days
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks
    
def get_vcpus_info():
    global total_cores
    #Open connection to libvirt
    conn = libvirt.openReadOnly(None)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
        return False
    
    res = conn.getInfo()
    total_cores = int(res[2])
    domain_list = conn.listAllDomains()
    for dl in domain_list:
        dlname = dl.name()
        dom = conn.lookupByName(dlname)
        dominfo = dom.info()
        dl_vcpus = dominfo[3]
        vcpus_dict[dlname] = dl_vcpus
        create_rrd_files(dlname)
    return True

# Globals
# subprocess to start virt-top
def collect_virt_top_data():
    if not get_vcpus_info():
        exit()
    
    time.sleep(5)

    virt_top_command = ['virt-top', '-d', str(time_interval), '--script', '--stream']
    virt_top_proc = subprocess.Popen(virt_top_command,stdout=subprocess.PIPE)
    virt_top_output_processing = False
   
    # process each line of the output
    while True:
        line = virt_top_proc.stdout.readline()
        if line != '':
            #get vcpus info
            parse_each_line(line)
        else:
            break

#if __name__ == "__main__":
#    collect_virt_top_data()
