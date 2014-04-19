#!/usr/bin/python
import libvirt
import sys

conn = libvirt.openReadOnly(None)
if conn == None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

try:
    domain_list = conn.listAllDomains()
    for dl in domain_list:
        dom0 = conn.lookupByName(dl.name())
        output = dom0.getCPUStats(True)
        print output
except:
    print 'Failed to find the main domain'
    sys.exit(1)

print "Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())

