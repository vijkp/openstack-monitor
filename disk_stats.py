#!/usr/bin/python

"""
Code to extract Disk utilization in VMs
"""
import subprocess 
import time
import libvirt
import rrdtool

def create_rrd_files(instance_name):
    time_interval = 5
    start_time = int(time.time())
    timeout = str(2*time_interval)
    rrdtool.create(str(instance_name+'_disk_stats.rrd'), '--step', str(time_interval),
            '--start', str(start_time),
            'DS:size_used:GAUGE:'+timeout+':0:U',
            'DS:size_available:GAUGE:'+timeout+':0:U',
            'DS:util_percent:GAUGE:'+timeout+':0:U',
            'RRA:AVERAGE:0.5:1:17280', # stores samples collected for 1 day 5*60*24
            'RRA:AVERAGE:0.5:360:240', # 30min averages for 5 days
            'RRA:AVERAGE:0.5:720:240', # 1 hour averages for 10 days
            'RRA:AVERAGE:0.5:1440:240', # 2 hour averages for 20 days
            'RRA:AVERAGE:0.5:8640:40', # 12 hour averages for 20 days
            'RRA:AVERAGE:0.5:12780:60', # 1 day averages for 60 days
            'RRA:AVERAGE:0.5:89460:10') # 1 week for 10 weeks

def write_to_rrdfile(timestamp, instance_name, stats):
    rrd_file = str(instance_name+'_disk_stats.rrd')
    args = "{}:{}:{}:{}".format(timestamp, stats[0], stats[1], stats[2])
    rrdtool.update(rrd_file, args)

def initialize():
    #Open connection to libvirt
    conn = libvirt.openReadOnly(None)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
        return False

    domain_list = conn.listAllDomains()
    for dl in domain_list:
        create_rrd_files(dl.name())
    return True

# subprocess to start virt-df
def collect_disk_stats():
    if not initialize():
        exit()
    
    while True:
 #       time.sleep(5)

        #Get output of virt-df command
        out = subprocess.check_output("virt-df --csv", shell=True)    
        lines = out.split('\n')
        timestamp = int(time.time())
        for i in range(1, len(lines) - 1):
            stats = lines[i].split(',')
            #timestamp, hostname, VirtualMachine,Filesystem,1K-blocks,Used,Available,Use %
            instance_name = stats[0]
            log = [stats[3], stats[4], stats[5]]
            write_to_rrdfile(timestamp, instance_name, log) 

#if __name__ == "__main__":
 #   collect_disk_stats()
