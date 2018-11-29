# -*- coding:utf-8 -*-

import unittest
from pprint import pprint

import actions

from mini_ruler.ruler import Ruler, RulerEnv, RulerNoMatch
from mini_ruler.lexer import RuleLexer

from mini_ruler.calc_tokens import calc



def func_action(param1):
    return param1


class LexerTestCase(unittest.TestCase):

    lexer = RuleLexer()

    def test_lexer_1(self):
        # 测试 &&  ||
        rule = "TRUE || FALSE && TRUE "
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

    def test_lexer_2(self):
        # 测试 &&  ||
        rule = "1 == 1 && 'str' == 'str' "
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "1 != 1 && 'str' == 'str' "
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

        rule = "1 >= 1 && 1 <= 1 && 'str' == 'str' "
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "2 > 1 && 1 < 2.5 && 'str' != 'str' "
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

    def test_lexer_3(self):
        # 非运算针对 BOOL, INT, FLOAT 等类型的运算
        rule = "!TRUE"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

        rule = "!FALSE"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "!0"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "!1"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

        rule = "!0.0000"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "!1.123"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

    def test_lexer_4(self):
        # 非运算针对 + - * / 等类型的运算
        rule = "1 == 2 - 1"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        rule = "5 == 10 - 1 * 5"
        result = calc(RulerEnv(), self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

    def test_lexer_5(self):
        # 针对ID的运算
        env = RulerEnv()
        env.set_var('id', 1024)
        rule = "1024 == id"
        result = calc(env, self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        env = RulerEnv()
        var = {'id': 1024}
        env.set_var('var', var)
        rule = "1024 == var.id"
        result = calc(env, self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        env = RulerEnv()
        var = {'dict':{'id': 1024}}
        env.set_var('var', var)
        rule = "1024 == var.dict.id"
        result = calc(env, self.lexer.parse_tokens(rule))
        self.assertEqual(result, True)

        env = RulerEnv()
        var = {'dict':{'id': 1024}}
        env.set_var('var', var)
        rule = "1111 == var.dict.id"
        result = calc(env, self.lexer.parse_tokens(rule))
        self.assertEqual(result, False)

        env = RulerEnv()
        var = {'dict':{'id': 1024}}
        env.set_var('var', var)
        rule = "var.dict.id"
        result = calc(env, self.lexer.parse_tokens(rule))
        self.assertEqual(result, 1024)


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

    def test_no_rule_match(self):
        rule_set = [ "IF FALSE THEN TRUE" ]
        ruler = Ruler()
        ruler.register_rule_set('test', rule_set)
        with self.assertRaises(RulerNoMatch):
            ret = ruler.entry('test', {})

    def test_goto_1(self):
        # Rule Pass
        rule_goto_stbu = [
            "IF FALSE THEN 'goto_rule_match'"
        ]
        rule_main = [
            "IF FALSE THEN 'action1'",
            "IF TRUE THEN goto('rule_goto_stbu')",
            "IF TRUE THEN 'action2'"
        ]
        ruler = Ruler()
        ruler.register_rule_set('main', rule_main)
        ruler.register_rule_set('rule_goto_stbu', rule_goto_stbu)
        result, rule = ruler.entry('main', {})
        self.assertEqual(result, 'action2')


    def test_goto_2(self):
        # Rule Pass
        rule_goto_stbu = [
            "IF TRUE THEN 'goto_rule_match'"
        ]
        rule_main = [
            "IF FALSE THEN 'action1'",
            "IF TRUE THEN goto('rule_goto_stbu')",
            "IF TRUE THEN 'action2'"
        ]
        ruler = Ruler()
        ruler.register_rule_set('main', rule_main)
        ruler.register_rule_set('rule_goto_stbu', rule_goto_stbu)
        result, rule = ruler.entry('main', {})
        self.assertEqual(result, 'goto_rule_match')

    def test_goto_3(self):
        # Rule Pass
        rule_goto_stbu = [
            "IF TRUE THEN 'goto_rule_match'"
        ]
        rule_main = [
            "IF FALSE THEN 'action1'",
            "IF TRUE THEN 'action2'",
            "IF TRUE THEN goto('rule_goto_stbu')",
        ]
        ruler = Ruler()
        ruler.register_rule_set('main', rule_main)
        ruler.register_rule_set('rule_goto_stbu', rule_goto_stbu)
        result, rule = ruler.entry('main', {})
        self.assertEqual(result, 'goto_rule_match')


    def test_goto_4(self):
        # Rule Pass
        rule_goto_stbu = [
            "IF TRUE THEN 'goto_rule_match'"
        ]
        rule_main = [
            "IF TRUE THEN goto('rule_goto_stbu')",
            "IF TRUE THEN 'action1'",
            "IF TRUE THEN 'action2'",
        ]
        ruler = Ruler()
        ruler.register_rule_set('main', rule_main)
        ruler.register_rule_set('rule_goto_stbu', rule_goto_stbu)
        result, rule = ruler.entry('main', {})
        self.assertEqual(result, 'action1')


    def test_var_exist_1(self):
        ruler = Ruler()

        rule_set = [ "IF userinfo.username && TRUE THEN TRUE" ]
        ruler.register_rule_set('test', rule_set)

        pkt = {'userinfo': {'username': 'laowang'}}
        (result, line) = ruler.entry('test', pkt)
        self.assertEqual(result, True)

        with self.assertRaises(RulerNoMatch):
            pkt = {'userinfo': []}
            ruler.entry('test', pkt)

        with self.assertRaises(RulerNoMatch):
            pkt = {'userinfo': ()}
            ruler.entry('test', pkt)

        with self.assertRaises(RulerNoMatch):
            pkt = {'userinfo': 'this is str'}
            ruler.entry('test', pkt)

        with self.assertRaises(RulerNoMatch):
            pkt = {'userinfo': 1}
            ruler.entry('test', pkt)


    def test_var_exist_2(self):
        ruler = Ruler()

        rule_set = [ "IF !userinfo.username THEN TRUE" ]
        ruler.register_rule_set('test', rule_set)

        # pkt = {'userinfo': {'username': 'laowang'}}
        pkt = {'userinfo': []}

        (result, line) = ruler.entry('test', pkt)
        self.assertEqual(result, True)

        # with self.assertRaises(RulerNoMatch):
        #     pkt = {'userinfo': []}
        #     ruler.entry('test', pkt)
        #
        # with self.assertRaises(RulerNoMatch):
        #     pkt = {'userinfo': ()}
        #     ruler.entry('test', pkt)
        #
        # with self.assertRaises(RulerNoMatch):
        #     pkt = {'userinfo': 'this is str'}
        #     ruler.entry('test', pkt)
        #
        # with self.assertRaises(RulerNoMatch):
        #     pkt = {'userinfo': 1}
        #     ruler.entry('test', pkt)



