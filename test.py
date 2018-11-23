# -*- coding:utf-8 -*-
from pprint import pprint

from mini_ruler.ruler import Ruler, parse_rule_file

from mini_ruler.basic_action import re_match


def test_accept():
    print("ACCEPT !!!!")
    return 0, (), ()


def test_drop():
    print("DROP !!!!")
    return -1, (), ()


def test_print_s(s):
    print("print: %s" % s)


if __name__ == "__main__":
    ruler = Ruler()

    rule_conf = parse_rule_file('./test.rule')

    pprint(rule_conf)


    ruler.register_action('test_accept', test_accept)
    ruler.register_action('test_drop', test_drop)
    ruler.register_action('test_print_s', test_print_s)

    for name, rlist in rule_conf.items():
        ruler.register_rule_set(name, rlist)

    # pprint(ruler.env.variables_stack)

    d = {
        'str': 'teststr',
        'num1': 2047,
        'num2': 10,
        'num3': 99,
        'ip': "192.168.1.100"
    }
    result = ruler.entry('main', d)

    print "result is %s" % (str(result))


