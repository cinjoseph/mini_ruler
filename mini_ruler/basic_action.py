# -*- coding:utf-8 -*-

import re
import ipaddr

def in_ip_range(ip, ip_range):
    ipNet = ipaddr.IPv4Network(ip_range)
    ip = ipaddr.IPv4Address(ip)
    if ip in ipNet:
        return True
    return False

def re_match(pattern, s):
    if type(s) != str:
        return False
    if type(pattern) != str:
        return False

    if re.match(pattern, s):
        return True
    return False


def in_num_range(x, low, high):
    if high >= x >= low:
        return True
    return False


def exist(p):
    if not p:
        return False
    return True
