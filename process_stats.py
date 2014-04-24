#!/usr/bin/python

"""
Code to process stats collected
"""

import csv
import glob
import time
import datetime

def isDateInRange(fileDate, dayCount):
    
    yearString = fileDate[0:4]
    #Get the occurence of '_'
    monthIndexBegin = fileDate.find('_')
    monthIndexEnd = fileDate.find('_', monthIndexBegin +1)
    monthString = fileDate[(monthIndexBegin +1): monthIndexEnd]
    dayString = fileDate[(monthIndexEnd + 1):]
    
    fileDateTime = datetime.datetime(int(yearString), int(monthString), int(dayString), 0, 0, 0)
    dayDiffFromCurrentDate = datetime.datetime.now() - fileDateTime
    
    if dayDiffFromCurrentDate < datetime.timedelta(days=dayCount):
        return True
    else:
        return False

def process_disk_stats(dayCount):
    csvFileList = glob.glob("*.csv")
    average = 0.0
    for csvFile in csvFileList:
        if csvFile.find("disk_stats") != -1:
            fileDate = csvFile[:9]
            if isDateInRange(fileDate, dayCount):
                logfile = csv.reader(open(csvFile, 'r'), delimiter=',', quotechar='|')
                counter = 1
                for line in logfile:
                    #Isolating the disk utilization percentage
                    average = (average*counter + float(line[len(line)-1]))/(counter + 1)
                    counter = counter + 1
                
    return average

print "Within 3 days: " + str(process_disk_stats(3))
print "Within 2 days: " + str(process_disk_stats(2))
print "Within 4 days: " + str(process_disk_stats(4))
print "Within 1 days: " + str(process_disk_stats(1))



