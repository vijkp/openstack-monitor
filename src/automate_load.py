#!/usr/bin/python

import subprocess
import os
import random
import time

def cpu_stress(cpu_percent, time_sec):
    pid = subprocess.Popen(["./lookbusy", "-c", str(cpu_percent)]).pid
    time.sleep(time_sec)
    subprocess.Popen(["sudo","kill","-9", str(pid)])

def mem_stress(mem_mb, time_sec):
    pid = subprocess.Popen(["./lookbusy", "-m", str(mem_mb) + "MB"]).pid
    time.sleep(time_sec)
    subprocess.Popen(["sudo","kill","-9", str(pid)])

def disk_stress(disk_mb, time_sec):
    pid = subprocess.Popen(["./lookbusy", "-d", str(disk_mb) + "KB"]).pid
    time.sleep(time_sec)
    subprocess.Popen(["sudo","kill","-9", str(pid)])

def random_stress():
    scenario = int(random.random()*3)
    if(scenario == 0):
        cpu_stress(int(random.random()*90), int(random.random()*7200))
    elif(scenario == 1):
        mem_stress(int(random.random()*1400), int(random.random()*7200))
    elif(scenario == 3):
        minBlockSize = 32768;
        disk_stress(int(random.random()*256) + minBlockSize, int(random.random()*7200))

while True:
    random_stress()
    time.sleep(60)
