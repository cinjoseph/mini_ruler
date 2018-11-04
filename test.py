# -*- coding:utf-8 -*-
from pprint import pprint

from mini_ruler.env import RulerEnv
from mini_ruler.calc import calc
from mini_ruler.lexer import RuleLexer

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

        lexer = RuleLexer()

        # data = 'a.b == "test" + "str" && 1 + 2047 == 2048 '
        data = 're_match("\d", "1")'


        tokens = lexer.parse_toekns(data)


        env = RulerEnv()

        # resiger action function
        env.set_var('re_match', re_match)

        env.push()

        env.set_var('a', {'b': 'teststr'})

        print calc(env, tokens)

        env.pop()

