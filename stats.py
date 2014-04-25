#!/usr/bin/python

""" classes for storing computed stats """

class avg_stats:
    def __init__(self, sname, instance_id):
        self.name = sname
        self.instance_id = instance_id
        self.ts = 0
        self.avg_2week = 0
        self.avg_1week = 0
        self.avg_1day = 0
        self.avg_12hrs = 0
        self.avg_6hrs = 0
        self.avg_3hrs = 0
        self.avg_1hr = 0
        self.avg_30min = 0
    def update(self, t, a2w, a1w, a1d, a12h, a6h, a3h, a1h, a30m):
        self.ts = t
        self.avg_2week = a2w
        self.avg_1week = a1w
        self.avg_1day = a1d
        self.avg_12hrs = a12h
        self.avg_6hrs = a6h
        self.avg_3hrs = a3h
        self.avg_1hr = a1h
        self.avg_30min = a30m
    def show(self):
        print "{} {} {} {} {} {} {} {} {} {}".format(self.name, self.instance_id, self.avg_2week, self.avg_1week, self.avg_1day, self.avg_12hrs, self.avg_6hrs, self.avg_3hrs, self.avg_1hr, self.avg_30min)

    def get_values(self):
        return [self.avg_2week, self.avg_1week, self.avg_1day, self.avg_12hrs, self.avg_6hrs, self.avg_3hrs, self.avg_1hr, self.avg_30min]

    def get_all(self):
        return [self.ts, self.name, self.instance_id, self.avg_2week, self.avg_1week, self.avg_1day, self.avg_12hrs, self.avg_6hrs, self.avg_3hrs, self.avg_1hr, self.avg_30min]


class maxmin_stats:
    def __init__(self, timestamp):
        ts = timestamp
        minm = 0
        maxm = 0
        minm_ts = 0
        maxm_ts = 0
    def show(self):
        print "{} {} {} {} {} {} {} {} {} {}".format(self.name, self.instance_id, self.)

    def get_values(self):
        return [self.avg_2week, self.avg_1week, self.avg_1day, self.avg_12hrs, self.avg_6hrs, self.avg_3hrs, self.avg_1hr, self.avg_30min]

    def get_all(self):
        return [self.ts, self.name, self.instance_id, self.avg_2week, self.avg_1week, self.avg_1day, self.avg_12hrs, self.avg_6hrs, self.avg_3hrs, self.avg_1hr, self.avg_30min]

def get_stat(time1, time2, stype):
    return dummystat

