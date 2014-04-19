#!/usr/bin/python

import subprocess
import time

#Create log file
logfile = open("log_cpu_stats.log","w+")
logfile.close()

for i in range(50):
    subprocess.call("./cpu_stats.py")
    print "run: " + str(i)
    time.sleep(5)


