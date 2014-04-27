#!/usr/bin/python

"""
Code to process stats collected
"""

import time
import datetime
import libvirt
import stats as st
import subprocess
import rrdtool

stat_types = ["cpu", "mem", "disk_io", "disk", "net_io"]
instance_list = []
metrics_table = {}  # stores pointers to avg_stats and avg_minmax_stats for each inst, stype, mt
stype_metrics = {}  # stores stype to stype metrics list
stype_metrics["cpu"] = ["cpu_percent"]
stype_metrics["mem"] = ["mem_percent"]
stype_metrics["disk_io"] = ["read_queue", "write_queue"]
stype_metrics["disk"] = ["size_used", "size_available", "util_percent"]
stype_metrics["net_io"] = ["rx_bytes", "tx_bytes"]


def create_metrics_table():
    global metrics_table
    for inst in instance_list:
        for stype in stat_types:
            for stype_m in stype_metrics[stype]:
                #print "creating dict {} {} {}".format(inst, stype, stype_m)
                if stype == "mem":
                    metrics_table[inst, stype, stype_m] = st.avg_maxmin_stats(inst, stype, stype_m) 
                else:
                    metrics_table[inst, stype, stype_m] = st.avg_stats(inst, stype, stype_m)

def get_instance_list():
    result = []
    #Open connection to libvirt
    conn = libvirt.openReadOnly(None)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
        sys.exit(1)

    domain_list = conn.listAllDomains()
    for dl in domain_list:
        result.append(dl.name())
    return result


def fetch_value(instance_name, stype, cfg, starttime, resolution):
    cmd = "rrdtool fetch {}_{}_stats.rrd {} -s {} -r {}".format(instance_name, 
            stype, cfg, starttime, resolution)
    output = subprocess.check_output(cmd, shell=True)
    current_ts = int(time.time())
    lines = output.split('\n')
    lineslen = len(lines)
    lineindex = lineslen - 1
    while lineindex >= 0:
        index =  lines[lineindex].find(':')
        if index != -1:
            timestamp = int(lines[lineindex][:index])
            if (current_ts - timestamp) <= 2*int(resolution):
                outvalues = lines[lineindex].split()
                if ('-nan' in outvalues) or ('nan' in outvalues):
                    lineindex -= 1
                    continue
                return outvalues[1:]
                break
        lineindex -= 1

def update_value(inst, stype, duration, values, cftype = "AVERAGE"):
    if values == None:
        return
    values = map(float, values)
    if stype == "cpu":
        metrics_table[inst, stype, "cpu_percent"].update(duration, values[0])
    elif stype == "disk":
        metrics_table[inst, stype, "size_used"].update(duration, values[0])
        metrics_table[inst, stype, "size_available"].update(duration, values[1])
        metrics_table[inst, stype, "util_percent"].update(duration, values[2])
    elif stype == "mem":
        metrics_table[inst, stype, "mem_percent"].update(duration, values[0], cftype)
    elif stype == "disk_io":
        metrics_table[inst, stype, "read_queue"].update(duration, values[0])
        metrics_table[inst, stype, "write_queue"].update(duration, values[1])
    elif stype == "net_io":
        metrics_table[inst, stype, "rx_bytes"].update(duration, values[0])
        metrics_table[inst, stype, "tx_bytes"].update(duration, values[1])


instance_list = get_instance_list()
create_metrics_table()


for inst in instance_list:
    for stype in stat_types:
        update_value(inst, stype, "5s", fetch_value(inst, stype, "AVERAGE", "-10s", "5"))
        update_value(inst, stype, "1hr", fetch_value(inst, stype, "AVERAGE", "-2hr", "3600"))
        update_value(inst, stype, "2hr", fetch_value(inst, stype, "AVERAGE", "-4hr", "7200"))
        update_value(inst, stype, "12hr", fetch_value(inst, stype, "AVERAGE", "-14hr", "43200"))
        update_value(inst, stype, "1d", fetch_value(inst, stype, "AVERAGE", "-2d", "86400"))
        update_value(inst, stype, "1w", fetch_value(inst, stype, "AVERAGE", "-2w", "604800"))
        if stype == "mem":
            update_value(inst, stype, "5s", fetch_value(inst, stype, "MAX", "-10s", "5"))
            update_value(inst, stype, "1hr", fetch_value(inst, stype, "MAX", "-2hr", "5"))
            update_value(inst, stype, "1d", fetch_value(inst, stype, "MAX", "-2d", "5"))
            update_value(inst, stype, "5s", fetch_value(inst, stype, "MIN", "-10s", "5"))
            update_value(inst, stype, "1hr", fetch_value(inst, stype, "MIN", "-2hr", "5"))
            update_value(inst, stype, "1d", fetch_value(inst, stype, "MIN", "-2d", "5"))



for key, value in metrics_table.iteritems():
    print key, value.instance_name, value.stype, value.stype_m, value.avg_5s, value.avg_2hr, value.avg_1hr, value.avg_1d, value.avg_12hr, value.avg_1w

