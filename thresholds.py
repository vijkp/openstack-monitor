#!/usr/bin/python

# recommendations and their definitions

""" cpu utilization """
avg_cpu_1w_upperlimit = 80  # 80%, to recommend user to upgrade hardware 
avg_cpu_1w_lowerlimit = 20  # 20%, to alert user about resource under utilization

avg_cpu_30min_upperlimit = 90  # 90%, Alert user about high CPU utilization 

""" memory utilization """
avg_mem_1w_upperlimit = 90  # 90%, to recommend user to upgrade hardware 
avg_mem_1w_lowerlimit = 20  # 20%, to alert user about resource under utilization

max_mem_upperlimit = 95 #95%, to alert the user regarding high RAM usage

""" disk utilization """
avg_disk_1w_upperlimit = 75  # 75%, to recommend user to add more disks
max_disk_30min_upperlimit = 95 #95%, alert user to increase disks now!

""" net io """
avg_net_io_1w_upperlimit = 90  # 90% of the allocated bandwidth, 
                               # to recommend user to increase bandwidth allocation
avg_net_io_1w_lowerlimit = 20  # 20% of the allocated bandwidth, 
                               # to alert user to downgrade bandwidth for instance

""" disk io """
avg_disk_io_1w_upperlimit = 90  # 90%, alert user about high IO 
avg_disk_io_1w_lowerlimit = 20  # 20%, to alert user about resource under utilization




