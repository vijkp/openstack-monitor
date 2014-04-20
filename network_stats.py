#!/usr/bin/python

"""
Collect network tx/rx stats from Virtual Machines
"""

import libvirt
import sys
import os
from subprocess import call as cmd_call
import re



