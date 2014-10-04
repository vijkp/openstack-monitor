#!/usr/bin/python

#   Openstack Monitor
#   File description: Collect network tx/rx stats from Virtual Machines
#   Authors: Vijay P, Sneha S
#   Email: {vijaykp, snehas}@cs.umass.edu

import subprocess
import time
import thread
import threading
from collect_virt_top_data import collect_virt_top_data
from disk_stats import collect_disk_stats 
from collect_host_stats import collect_host_stats

class diskThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting disk"
        collect_disk_stats()
        print "Exiting disk "

class cpuThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting cpu"
        collect_virt_top_data()
        print "Exiting cpu "

class hostThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting host stat collection"
        collect_host_stats()
        print "Exiting host stat colelction "

print "Please run this as a daemon, otherwise this command will not return unless killed"

#Create threads
disk_thread = diskThread()
cpu_thread = cpuThread()
host_thread = hostThread()

#Run threads
disk_thread.start()
cpu_thread.start()
host_thread.start()



