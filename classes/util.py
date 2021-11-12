import time
import re

def get_time_since_epoch(str_time):

    split_time = re.split("[T.]",str_time)
    t = time.strptime(split_time[0]+' '+split_time[1], "%Y-%m-%d %H:%M:%S")
    return time.mktime(t)

print(get_time_since_epoch("2021-11-12T14:38:46.449560550Z"))