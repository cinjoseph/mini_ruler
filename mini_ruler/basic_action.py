# -*- coding:utf-8 -*-

import re


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
