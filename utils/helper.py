import time
from datetime import datetime, timedelta


class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        print('>>> Elapsed time: {0}\n'.format(str(timedelta(seconds=time.time() - self.start_time))[:-3]))


def strify(lst, delim=','):
    return delim.join(map(str, lst))


def intify(lst_str, delim=','):
    return list(map(int, lst_str.split(delim)))


def bias_metric(a, b):
    return (b - a) / (a + b)
