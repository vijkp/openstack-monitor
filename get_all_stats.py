#!/usr/bin/python

import subprocess
import time
from disk_stats import collect_disk_stats 

for i in range(5):
    print "run: " + str(i)
    collect_disk_stats()
    time.sleep(5)


