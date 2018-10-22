# -*- coding:utf-8 -*-


import re
import datetime
import copy
from lexer import RuleLexer, tokens_polymerize, relational_operator_polymerize

from factor import Var, Func, FactorFactory

import pprint

from utils import array_printable


def lexer_build(s, rule_lexer, factor_factory):
    tokens = rule_lexer.analyse(s)
    polymerized_tokens = tokens_polymerize(tokens)
    factors = [factor_factory.new(tok[0], tok[1]) for tok in polymerized_tokens]
    ret = relational_operator_polymerize(factors)
    return ret


def split_rule(rule):
    pattern = r"^IF (?P<cond>[\S ]+) THEN (?P<action>[\S ]+)"
    reg = re.compile(pattern)
    match = reg.match(rule)
    if not match:
        return None
    match = match.groupdict()
    return match['cond'], match['action']


def build_rule(rule, rule_lexer, cond_factor_factory, act_factor_factory):
    cond_str, action_str = split_rule(rule)

    factors_map = lexer_build(cond_str, rule_lexer, cond_factor_factory)
    condition = FactorMap(cond_str, factors_map)

    factors_map = lexer_build(action_str, rule_lexer, act_factor_factory)
    if not (isinstance(factors_map[0], Func) and len(factors_map) == 1):
        raise Exception("Error Action '%s' in rule '%s'" % (action_str, rule))
    action = FactorMap(action_str, factors_map)

    return rule, condition, action


class FactorMap(object):

    def __init__(self, s, factors_map):
        self.s = s
        self.factors_map = factors_map

    def match(self, p):
        factors_map = self.factors_map
        return self._match(factors_map, p)

    def _match(self, factors_map, p):
        stack = []
        # print array_printable(factors_map)
        for f in factors_map:
            # print f,"stack = %s" % array_printable(stack)
            if len(stack) == 0 or len(stack) == 2:
                if type(f) == list:
                    f = self._match(f, p)
                elif isinstance(f, Var):
                    f = f.get_value(p)
                elif isinstance(f, Func):
                    f = f.do(p)
                stack.append(f)
            elif len(stack) == 1:
                stack.append(f)

            if len(stack) == 3:
                operand_1, operator, operand_2 = stack[0], stack[1], stack[2]
                ret = operator.calc(operand_1, operand_2)
                stack = [ret]

            if len(stack) > 3:
                raise Exception("Error...")

        if len(stack) != 1:
            raise Exception("Error Rule: %s" % self.s)

        return stack[0]


class RuleSet:

    def __init__(self, name, rule_list, rule_lexer, cond_factor_factory, act_factor_factory):
        self.name = name
        self.rule_obj_list = []
        for rule in rule_list:
            rule_obj = build_rule(rule, rule_lexer, cond_factor_factory, act_factor_factory)
            self.rule_obj_list.append(rule_obj)

    def foreach(self, p):
        for rule_obj in self.rule_obj_list:
            rule, condition, action = rule_obj[0], rule_obj[1], rule_obj[2]
            result = condition.match(p)
            print("In rule set '%s' run '%s'. is result matching? %s" % (self.name, rule, result))
            if result :
                return action
        return None


class RuleMap:

    class NoRuleSet(Exception):
        pass

    class RuleSetAlreadyExist(Exception):
        pass

    def __init__(self, name, first_entry):
        self.rule_map = {}
        self.name = name
        self.lexer = RuleLexer()
        self.condition_factor_factory = FactorFactory()
        self.action_factor_factory = FactorFactory()
        self.first_entry = first_entry
        self.init()

    def init(self):
        self.register_action_func(self.__bulitin_goto_rule__, 'GOTO')

    def register_rule_set(self, name, rule_list):
        if name in self.rule_map:
            raise self.RuleSetAlreadyExist()
        self.rule_map[name] = RuleSet(name, rule_list, self.lexer,
                                      self.condition_factor_factory,
                                      self.action_factor_factory)

    def register_condition_func(self, f, name):
        self.condition_factor_factory.func_factory.register(f, name)

    def register_action_func(self, f, name):
        self.action_factor_factory.func_factory.register(f, name)

    def entry(self, d):
        self._entry(self.first_entry, d)

    def _entry(self, name, d):
        if name not in self.rule_map:
            raise self.NoRuleSet()

        rule_set = self.rule_map[name]
        action = rule_set.foreach(d)
        if action:
            action.match(d)

    def __bulitin_goto_rule__(self, name, d):
        print("GOTO %s" % name)
        self._entry(name, d)

if __name__ == "__main__":


    rule_main = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id1 == 1 THEN accept()",
        "IF FALSE == exist(pkt.not_exist) THEN accept()",
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id1 == 2048 THEN GOTO('rule_1', __builtin_raw__)",
    ]

    rule_1 = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id2 == 778 THEN GOTO('rule_2', __builtin_raw__)",
    ]

    rule_2 = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id3 == 22 THEN accept()",
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id3 == 22 THEN GOTO('rule_3', __builtin_raw__)",
    ]

    rule_3 = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.s == string THEN accept()",
    ]


    p = {
        'pkt': {
            'id1': 2048,
            'id2': 778,
            'id3': 22,
            's': 'string',
        }
    }

    rule_map = RuleMap('testRuleMap', 'main')

    # 注册条件匹配中的动作函数
    rule_map.register_condition_func('basic_action.in_num_range', 'in_num_range')
    rule_map.register_condition_func('basic_action.exist', 'exist')

    # 注册匹配成功后的结果动作函数
    rule_map.register_action_func('basic_action.accept', 'accept')

    rule_map.register_rule_set('main', rule_main)
    rule_map.register_rule_set('rule_1', rule_1)
    rule_map.register_rule_set('rule_2', rule_2)
    rule_map.register_rule_set('rule_3', rule_3)

    rule_map.entry(p)


