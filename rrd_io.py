#!/usr/bin/python

import rrdtool
import time
import random
import os

data_sources=[ 'DS:speed1:GAUGE:2:U:U',
               'DS:speed2:GAUGE:2:U:U',
               'DS:speed3:GAUGE:2:U:U' ]

start_time = int(time.time())
print start_time

os.system("rm -rf speed.rrd")


rrdtool.create( 'speed.rrd',
                 '--step','1','--start', str(start_time),
                 data_sources,
                 'RRA:AVERAGE:0.5:1:50',
                 'RRA:AVERAGE:0.5:2:40',
                 'RRA:AVERAGE:0.5:10:3' )
time.sleep(1)

for i in range(0,50):
    args = "{}:{}:{}:{}".format(int(time.time()), 100*random.random(), 100*random.random(), 100*random.random())
    print args 
    rrdtool.update( 'speed.rrd',
                    args)
    time.sleep(1)

#output = rrdtool.fetch('speed.rrd',
#                        'AVERAGE')

#print output
