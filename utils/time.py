import numpy as np
from math import radians, degrees
from cmath import rect, phase
from datetime import datetime as dt


def stamp2str(stamp, form='%Y-%m-%d %H:%M:%S'):
    return dt.utcfromtimestamp(stamp).strftime(form)


def str2stamp(string, form='%Y-%m-%d %H:%M:%S'):
    return dt.strptime(string, form).timestamp()


def getfromstr(string, info, form='%Y-%m-%d %H:%M:%S'):
    time = dt.strptime(string, form)
    if info == 'seconds':
        return time.second
    if info == 'minutes':
        return time.minute
    if info == 'hours':
        return time.hour


def mean_time(times, form='%H:%M:%S'):
    rad = []
    for time in times:
        time = dt.strptime(time, form)
        seconds = time.second + time.minute * 60 + time.hour * 3600
        rad.append(rect(1, radians(seconds * 360 / 86400)))
    mean = degrees(np.mean(rad)) * 86400 / 360
    if mean < 0:
        mean += 86400
    return mean
