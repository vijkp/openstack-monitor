#!/usr/bin/python

import subprocess
import time
import thread
import threading
from collect_virt_top_data import collect_virt_top_data
from disk_stats import collect_disk_stats 

class diskThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting disk"
        while(1): 
            collect_disk_stats()
            time.sleep(5)
        print "Exiting disk "

class cpuThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print "Starting cpu"
        collect_virt_top_data()
        print "Exiting cpu "

#Create threads
disk_thread = diskThread()
cpu_thread = cpuThread()

#Run threads
disk_thread.start()
cpu_thread.start()



