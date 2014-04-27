#!/usr/bin/python

import os
import subprocess
import fabric 

def executeCommand(machine, command):
    process = subprocess.Popen("ssh " + machine + " " + command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output,stderr = process.communicate()
    status = process.poll()
    print output

executeCommand("ubuntu@10.0.0.3", "ls")
