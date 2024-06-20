import re
import logging
from datetime import timedelta

def mus1ca_timestamp(description, delimited = ' /'):
    timestamps = []
    for i in open(description, 'r', encoding='UTF-8'):
        if len(re.findall('\d+:\d+', i)) == 0:
            continue
        i = i.replace('\n','').replace('」', '').replace('~',' ')\
            .replace('「', ' ').replace('『', ' ').replace('』', ' ')
        if ':' in i:
            timestamps.append([i[:i.find(' ')], i[i.find(' ')+1:]])
            #timestamps[-1][1] = timestamps[-1][1][1:]
            if delimited in timestamps[-1][1]:
                timestamps[-1][1] = [timestamps[-1][1][:timestamps[-1][1].find('/')],
                                     timestamps[-1][1][timestamps[-1][1].find('/')+1:]
                                     ]
                timestamps[-1][1] = ' by '.join(timestamps[-1][1])
            #timestamps[-1][1].replace('/', ' by ')
            #timestamps[-1][1] = ' by '.join(timestamps[-1][1].split('/'))
            #timestamps[-1][1] = timestamps[-1][1].replace('-', 'by')
            while timestamps[-1][1][0] == ' ':
                timestamps[-1][1] = timestamps[-1][1][1:]
            while timestamps[-1][1][-1] == ' ':
                timestamps[-1][1] = timestamps[-1][1][:-1]

    return timestamps


def timestamp2sec(timestamp):
    # hurr durr...
    timestamp = timestamp.split(':')
    timestamp.reverse()
    seconds = 0
    for i in range(len(timestamp)):
        seconds += int(float(timestamp[i])) * pow(60, i)
    return seconds

def is_stamp_missing(stamp, stamps, secrange = 40):
    stamp_sec = timestamp2sec(stamp[0])
    for i in stamps:
        i_sec = timestamp2sec(i[0])
        if i_sec > stamp_sec + secrange:
            return True
        if abs(i_sec-stamp_sec) < secrange:
            return False
    return True

def fix_missing_stamps(stamps, stamps2):
    r = []
    for i in stamps:
        if not is_stamp_missing(i, stamps2):
            r.append(i)
        else:
            logging.warning([i, 'is missing and gone(puff)'])
    return r

def sec2timestamp(sec):
    try:
        return str(timedelta(seconds=sec))
    except Exception:
        return "infinity"
        