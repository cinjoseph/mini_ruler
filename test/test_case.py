# -*- coding:utf-8 -*-

import unittest
from pprint import pprint

import actions

from mini_ruler.ruler import Ruler, RulerEnv
from mini_ruler.lexer import RuleLexer

from mini_ruler.calc_tokens import calc



def func_action(param1):
    return param1


class RulerTestCase(unittest.TestCase):

    def test_string_action(self):
        rule_set = [ "IF TRUE THEN stringAction" ]
        ruler = Ruler()
        ruler.register_action('stringAction', 'stringAction')
        ruler.register_rule_set('test', rule_set)
        (result, line) = ruler.entry('test', {})
        self.assertEqual(result, 'stringAction')

    def test_int_action(self):
        rule_set = [ "IF TRUE THEN intAction" ]
        ruler = Ruler()
        ruler.register_action('intAction', 1)
        ruler.register_rule_set('test', rule_set)
        (result, line) = ruler.entry('test', {})
        self.assertEqual(result, 1)

    def test_ip_in_range(self):
        rule_set = [ "IF ip_in_net('192.168.1.100', '192.168.1.0/24') THEN TRUE" ]
        ruler = Ruler()
        ruler.register_rule_set('test', rule_set)
        (result, line) = ruler.entry('test', {})
        self.assertEqual(result, True)

    def test_num_in_range(self):
        rule_set = [ "IF num_in_range(1, 100, 200) THEN FALSE" ]
        ruler = Ruler()
        ruler.register_rule_set('test', rule_set)
        ret = ruler.entry('test', {})
        self.assertEqual(ret, None)

        rule_set = ["IF num_in_range(110, 100, 200) THEN TRUE"]
        ruler = Ruler()
        ruler.register_rule_set('test', rule_set)
        (result, line) = ruler.entry('test', {})
        self.assertEqual(result, True)

    def test_calc_priority_1(self):
        # 测试 &&  ||
        lexer = RuleLexer()
        env = RulerEnv()
        tokens = lexer.parse_tokens("TRUE || FALSE && TRUE ")
        result = calc(env, tokens)
        self.assertEqual(result, True)

    def test_calc_21(self):
        rule_set = [ "IF id==1 && userinfo.username=='laowang' THEN TRUE" ]
        ruler = Ruler()
        ruler.register_rule_set('test', rule_set)
        pkt = {
            'id': 1,
            'userinfo': {'username': 'laowang'}
        }
        ret = ruler.entry('test', pkt)
        self.assertNotEqual(ret, None)
        (result, line) = ret
        self.assertEqual(result, True)

    # def test_var_exist_1(self):
    #     ruler = Ruler()
    #     pkt = {
    #         'userinfo': {'username': 'laowang'}
    #     }
    #
    #     rule_set = [ "IF userinfo.username THEN TRUE" ]
    #     ruler.register_rule_set('test', rule_set)
    #     (result, line) = ruler.entry('test', {})
    #     self.assertEqual(result, True)
    #
    #     rule_set = [ "IF userinfo.username THEN TRUE" ]
    #     ruler.register_rule_set('test', rule_set)
    #     (result, line) = ruler.entry('test', {})
    #     self.assertEqual(result, True)


