import numpy as np
import hashlib
from itertools import chain, combinations


def sigmoid(x, a=0, b=1, c=1, k=1, q=1, v=1):
    return a + ((k-a) / (c + q*np.exp(-b*x)))**(1/v)


def poisson_points(intensity=1, rect=(0,0,1,1)):
    dx, dy = rect[2] - rect[0], rect[3] - rect[1]
    pts = np.random.poisson(intensity * dx * dy)
    xx = rect[0] + dx * np.random.uniform(0, 1, pts)
    yy = rect[1] + dy * np.random.uniform(0, 1, pts)
    return xx, yy


def powerset(lst):
    return chain.from_iterable(combinations(lst, r) for r in range(len(lst)+1))


def str2hash(string, max_num=2**128):
    num = int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16)
    return num % max_num
