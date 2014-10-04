#!/usr/bin/python

#   Openstack Monitor
#   File description: Routines to process collected stats
#   Authors: Vijay P, Sneha S
#   Email: {vijaykp, snehas}@cs.umass.edu

import time
import datetime
import libvirt
import stats as st
import subprocess
import rrdtool
import os
import thresholds as th
import glob
import json
import collections
import socket

# Globals
stat_types = ["cpu", "mem", "disk_io", "disk", "net_io"]
instance_list = []
metrics_table = {}  # stores pointers to avg_stats and avg_minmax_stats for each inst, stype, mt
stype_metrics = {}  # stores stype to stype metrics list
host_cpu = {}
host_mem = {}
stype_metrics["cpu"] = ["cpu_percent"]
stype_metrics["mem"] = ["mem_percent"]
stype_metrics["disk_io"] = ["read_queue", "write_queue"]
stype_metrics["disk"] = ["size_used", "size_available", "util_percent"]
stype_metrics["net_io"] = ["rx_bytes", "tx_bytes"]
calc_interval = 600 
calc_delay = 10
file_list = collections.deque([], 10) # list with max length 10

def get_hostname():
    if socket.gethostname().find('.')>=0:
        name=socket.gethostname()
    else:
        name=socket.gethostbyaddr(socket.gethostname())[0]
    return name

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

def fetch_host_value(stype, starttime, resolution):
    cmd = "rrdtool fetch host_{}_stats.rrd AVERAGE -s {} -r {}".format(stype, 
            starttime, resolution)
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

def get_reftime_value():
    rlist =  glob.glob("*cpu_stats*.rrd")
    if len(rlist) == 0:
        print "error: no rrd files"
        exit(1)
    filename = rlist[0]
    cmd = "rrdtool fetch {} {} -s {} -r {}".format(filename, "AVERAGE", "-2hr", str(calc_interval))
    output = subprocess.check_output(cmd, shell=True)
    lines = output.split('\n')
    lineindex = len(lines) - 2
    index =  lines[lineindex].find(':')
    timestamp = int(lines[lineindex][:index])
    return timestamp

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

def fetch_and_update_stats():
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
    #for key, value in metrics_table.iteritems():
    #    print key, value.instance_name, value.stype, value.stype_m, value.avg_5s, value.avg_2hr, value.avg_1hr, value.avg_1d, value.avg_12hr, value.avg_1w

def update_host_stats(stype, duration, values):
    global host_cpu
    global host_mem
    if values == None:
        return
    values = map(float, values)
    if stype == "cpu":
        host_cpu.update(duration, values[0])
    elif stype == "mem":
        host_mem.update(duration, values[0])

def fetch_and_update_host_stats():
    global host_cpu
    global host_mem
    host_cpu = st.avg_host_stats()
    host_mem = st.avg_host_stats()
    
    update_host_stats("cpu", "5s", fetch_host_value("cpu", "-10s", "5"))
    update_host_stats("cpu", "1hr", fetch_host_value("cpu", "-2hr", "3600"))
    update_host_stats("cpu", "2hr", fetch_host_value("cpu", "-4hr", "7200"))
    update_host_stats("cpu", "12hr", fetch_host_value("cpu", "-14hr", "43200"))
    update_host_stats("cpu", "1d", fetch_host_value("cpu", "-2d", "86400"))
    update_host_stats("cpu", "1w",fetch_host_value("cpu", "-2w", "604800"))

    update_host_stats("mem", "5s", fetch_host_value("mem", "-10s", "5"))
    update_host_stats("mem", "1hr", fetch_host_value("mem", "-2hr", "3600"))
    update_host_stats("mem", "2hr", fetch_host_value("mem", "-4hr", "7200"))
    update_host_stats("mem", "12hr", fetch_host_value("mem", "-14hr", "43200"))
    update_host_stats("mem", "1d", fetch_host_value("mem", "-2d", "86400"))
    update_host_stats("mem", "1w",fetch_host_value("mem", "-2w", "604800"))

def generate_host_recommendations(ctime):
    message = "Nothing"
    host_cpu_percent = host_cpu.avg_5s

    if host_cpu_percent > th.max_host_vm_util:
        vm_max_cpu = 0
        max_inst = ""
        #Deal with CPU
        for inst in instance_list:
            if (metrics_table[inst, "cpu", "cpu_percent"].avg_5s > vm_max_cpu):
                vm_max_cpu = metrics_table[inst, "cpu", "cpu_percent"].avg_5s
                max_inst = inst;
        
        message = "Instance: " + max_inst + " is taking up most of the Host CPU. Request you to move it."
        message = message + " Host is running at: {} %". format(str(host_cpu_percent))
        #Write to JSON
        host_json_file = open("../web/host_level_stats.json","w")
        jsonfinal = {}
        jsonfinal.clear()
        jsonfinal["timestamp"] = ctime.strftime("%Y-%m-%d %H:%M:%S")
        jsonfinal["message"] = message

        inst_json = json.JSONEncoder().encode(jsonfinal)
        host_json_file.write(inst_json + "\n")
        host_json_file.close()

def generate_recommendations(ctime):
    # for each instance 
    recos = []
    message = "Dummy reco message. Value: 0)"
    timemsg = "1 hour"
    for inst in instance_list:
        for stype in stat_types:
            message = "no-reco"
            if stype == 'cpu':
                value = metrics_table[inst, stype, "cpu_percent"].avg_5s
                if(value > th.avg_cpu_1w_upperlimit):
                    level = st.level[1]
                    message = "High cpu utilization (Average for the past 5 seconds: {}%).".format(float(round(value, 2)))
                if(value < th.avg_cpu_1w_lowerlimit):
                    level = st.level[0]
                    message = "CPUs under utilized (Average for the past {}: {}%).".format(timemsg, float(round(value, 2)))

            elif stype == 'disk':
                value = metrics_table[inst, stype, "util_percent"].avg_1hr
                if( value > th.avg_disk_1w_upperlimit):
                    level = st.level[1]
                    message = "High disk utilization (Average for the past {}: {}%).".format(timemsg, float(round(value, 2)))
            
            elif stype == 'net_io':
                value = metrics_table[inst, stype, "rx_bytes"].avg_1hr
                if(value > th.avg_net_io_1w_upperlimit):
                    level = st.level[1]
                    message = "High network utilization (Average received bytes for the past {}: {}).".format(timemsg, float(round(value, 2)))
                if(value < th.avg_net_io_1w_lowerlimit):
                    level = st.level[0]
                    message = "Low network utilization (Average receved bytes for the past {}: {}).".format(timemsg, float(round(value, 2)))
                
                value = metrics_table[inst, stype, "tx_bytes"].avg_1hr
                if(value > th.avg_net_io_1w_upperlimit):
                    level = st.level[1]
                    message = "High network utilization (Average transfered bytes for the past {}: {}).".format(timemsg, float(round(value, 2)))
                if(value < th.avg_net_io_1w_lowerlimit):
                    level = st.level[0]
                    message = "Low network utilization (Average transfered bytes for the past {}: {}).".format(timemsg, float(round(value, 2)))

            elif stype == 'mem':
                value = metrics_table[inst, stype, "mem_percent"].avg_1hr
                if(value > th.avg_mem_1w_upperlimit):
                    level = st.level[1]
                    message = "High memory utilization (Average for the past {}: {}%).".format(timemsg, float(round(value, 2)))
                if(value < th.avg_mem_1w_lowerlimit):
                    level = st.level[0]
                    message = "Low memory utilization (Average for the past {}: {}%).".format(timemsg, float(round(value, 2)))

            elif stype == 'disk_io':
                value = metrics_table[inst, stype, "read_queue"].avg_1hr
                if(value > th.avg_disk_io_1w_upperlimit):
                    level = st.level[1]
                    message = "High disk utilization (Average read queue for the past {}: {}).".format(timemsg, float(round(value, 2)))
                if(value > th.avg_disk_io_1w_lowerlimit):
                    level = st.level[0]
                    message = "Low disk utilization (Average read queue for the past {}: {}).".format(timemsg, float(round(value, 2)))
                
                value = metrics_table[inst, stype, "write_queue"].avg_1hr
                if(value > th.avg_disk_io_1w_upperlimit):
                    level = st.level[1]
                    message = "High disk utilization (Average write queue for the past {}: {}).".format(timemsg, float(round(value, 2)))
                if(value > th.avg_disk_io_1w_lowerlimit):
                    level = st.level[0]
                    message = "Low disk utilization (Average write queue for the past {}: {}).".format(timemsg, float(round(value, 2)))
            
            if not (message == "no-reco"):
                # add recommendation to reco list
                recos.append(st.reco(inst, stype, value, level, message))
    
    # write down all recos into a file with a timestamp
    fjsonname = ctime.strftime("%Y%m%d-%H%M-%S") + "_recos.json"
    fjson = open(fjsonname, "w")
    # write recos into a json file whose name is the current timestamp
    jrecos = []
    hostname = get_hostname()
    for r in recos:
        jrecos.append({"reco":{"instance_name": r.instance_name, 
            "level": r.level,   
            "stype": r.stype, "value": r.value, "recomsg": r.recomsg}})
    jsonfinal = {}
    jsonfinal.clear()
    jsonfinal["timestamp"] = ctime.strftime("%Y-%m-%d %H:%M:%S")
    jsonfinal["allrecos"] = jrecos
    
    jsonrecos = json.JSONEncoder().encode(jsonfinal)
    fjson.write(jsonrecos + "\n")
    fjson.close()
    file_list.append(fjsonname)
    file_list_length = len(file_list)
    file_list_index = file_list_length - 1
    while file_list_index >= 0:
        os.system("ln -s  -f ../data/{} ../web/session{}.json".format(file_list[file_list_index], file_list_length - file_list_index - 1))
        file_list_index -= 1
    
    #Write all instances associated with hostname into json
    host_json_file = open("../web/host_inst.json","w")
    inst_dict = {}
    inst_dict.clear()
    inst_dict["hostname"] = hostname
    inst_dict["instances"] = instance_list

    inst_json = json.JSONEncoder().encode(inst_dict)
    host_json_file.write(inst_json + "\n")
    host_json_file.close()

def main():
    global instance_list

    current_ts = int(time.time())
    ref_ts = get_reftime_value ()
    
    tdiff = ref_ts - current_ts
    if tdiff >= 0:
        print "waiting {} seconds".format(tdiff + calc_delay)
        time.sleep(tdiff + calc_delay)
    else:
        print "waiting {} seconds".format(calc_interval + tdiff + calc_delay)
        time.sleep(calc_interval + tdiff + calc_delay)
            
    while True:
        time_now = datetime.datetime.now()
        print "{}: processing rrd files to generate recommendations".format(time_now.strftime("%Y-%m-%d %H:%M:%S"))
        instance_list = get_instance_list()
        create_metrics_table()

        # fetch values from rrd files
        fetch_and_update_stats()
        fetch_and_update_host_stats()

        # generate recos
        generate_recommendations(time_now)
        generate_host_recommendations(time_now)

        current_ts = int(time.time())
        tdiff = (current_ts - ref_ts)%calc_interval
        time.sleep(calc_interval - tdiff + calc_delay)

if __name__ == "__main__":
    main()


