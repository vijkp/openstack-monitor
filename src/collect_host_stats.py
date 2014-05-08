#!/usr/bin/python

"""
Collect host cpu and mem stats
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


def save_to_rrdfile(ts, value, stype):
    if stype == "host_cpu":
        rrd_file = str(cpufile+'.rrd')
        arguments = "{}:{}".format(ts, value)
    elif stype == "host_mem":
        rrd_file = str(memfile+'.rrd')
        arguments = "{}:{}".format(ts, value)
    else:
        print "error: invalid stat type"
        exit(1)
    rrdtool.update(rrd_file, arguments)

def parse_each_line(timestamp, line):
    tokens = line.split()
    idletoken = tokens[4]
    host_cpu = 100.0 - float(tokens[4][:tokens[4].find('%')])
    save_to_rrdfile(timestamp, host_cpu, "host_cpu")

memfile = "host_mem_stats"
cpufile = "host_cpu_stats"
time_interval = 5

def create_rrd_files():
    start_time = int(time.time())
    timeout = str(2*time_interval)
    rrdtool.create(str(cpufile+'.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:cpu_percent:GAUGE:'+timeout+':0:U',
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks
    rrdtool.create(str(memfile+'.rrd'), '--step', str(time_interval),
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
     
def get_timestamp(line):
    tokens = line.split()
    dt1 = datetime.datetime.strptime(tokens[2], "%H:%M:%S").time()
    dt2 = datetime.datetime.combine(datetime.date.today(), dt1)
    timestamp = int(time.mktime(dt2.timetuple()))
    return timestamp

# Globals
# subprocess to start virt-top
def collect_host_stats():
    create_rrd_files()
    
    time.sleep(5)
    top_command = ['top', '-b', '-d' ,'5']
    top_proc = subprocess.Popen(top_command,stdout=subprocess.PIPE)
   
    # process each line of the output
    while True:
        line = top_proc.stdout.readline()
        if line != '':
            #get vcpus info
            if ("top" in line) and ("users" in line) and ("load average" in line):
                timestamp = get_timestamp(line)
            if "Cpu(s)" in line:
                parse_each_line(timestamp, line)
        else:
            break

#if __name__ == "__main__":
#    collect_host_stats()
