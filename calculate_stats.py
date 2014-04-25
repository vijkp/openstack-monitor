#!/usr/bin/python

"""
Code to process stats collected
"""

import csv
import glob
import time
import datetime
import stats as st


# Initialize calculate stat variables

cpu_stats = st.avg_stats("cpu", "instance-0000001") 
print st.get_stat(0, 0, 0)

cpu_stats.show()
values = cpu_stats.get_values()
print values
print cpu_stats.get_all()

