#!/usr/bin/python

""" classes for storing computed stats """

class avg_stats:
    def __init__(self, sname, stype, stype_m):
        self.instance_name = sname
        self.stype = stype
        self.stype_m = stype_m
        self.avg_5s = 0.0
        self.avg_1hr = 0.0
        self.avg_2hr = 0.0
        self.avg_12hr = 0.0
        self.avg_1d = 0.0
        self.avg_1w = 0.0
    def update(self, duration, value, cftype = 'AVERAGE'):
        if duration == "5s":
            self.avg_5s = value
        elif duration == "1hr":
            self.avg_1hr = value
        elif duration == "2hr":
            self.avg_2hr = value
        elif duration == "12hr":
            self.avg_12hr = value
        elif duration == "1d":
            self.avg_1d = value
        elif duration == "1w":
            self.avg_1w = value

class avg_maxmin_stats:
    def __init__(self, sname, stype, stype_m):
        self.instance_name = sname
        self.stype = stype
        self.stype_m = stype_m
        self.max_5s = 0.0
        self.max_1hr = 0.0
        self.max_1d = 0.0
        self.min_5s = 0.0
        self.min_1hr = 0.0
        self.min_1d = 0.0
        self.avg_5s = 0.0
        self.avg_1hr = 0.0
        self.avg_2hr = 0.0
        self.avg_12hr = 0.0
        self.avg_1d = 0.0
        self.avg_1w = 0.0
    def update(self, duration, value, cftype = 'AVERAGE'):
        if cftype == 'AVERAGE':
            if duration == "5s":
                self.avg_5s = value
            elif duration == "1hr":
                self.avg_1hr = value
            elif duration == "2hr":
                self.avg_2hr = value
            elif duration == "12hr":
                self.avg_12hr = value
            elif duration == "1d":
                self.avg_1d = value
            elif duration == "1w":
                self.avg_1w = value
        elif cftype == 'MAX':
            if duration == "5s":
                self.max_5s = value
            elif duration == '1hr':
                self.max_1hr = value
            elif duration == '1d':
                self.max_1d = value
        elif cftype == 'MIN':
            if duration == "5s":
                self.min_5s = value
            elif duration == '1hr':
                self.min_1hr = value
            elif duration == '1d':
                self.min_1d = value

