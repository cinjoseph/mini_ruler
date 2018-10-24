# -*- coding:utf-8 -*-


import re
from lexer import RuleLexer
from factor import Var, Func, FactorFactory

import copy
import datetime
import pprint
from utils import array_printable


class ConditionMap(object):

    def __init__(self, s, factors_map):
        self.s = s
        self.factors_map = factors_map

    def match(self, p):
        factors_map = self.factors_map
        match_result = self._match(factors_map, p)
        return match_result

    def _match(self, factors_map, p):
        stack = []
        # print array_printable(factors_map)
        for f in factors_map:
            # print f,"stack = %s" % array_printable(stack)
            if len(stack) == 0 or len(stack) == 2:
                if type(f) == list:
                    f = self._match(f, p)
                elif isinstance(f, Var):
                    f = f.value(p)
                elif isinstance(f, Func):
                    f = f.value(p)
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


def split_rule(rule):
    pattern = r"^IF (?P<cond>[\S ]+) THEN (?P<action>[\S ]+)"
    reg = re.compile(pattern)
    match = reg.match(rule)
    if not match:
        return None
    match = match.groupdict()
    return match['cond'], match['action']


def lexer_build(s, rule_lexer, factor_factory):
    tokens = rule_lexer.parse_toekns(s)
    factors = [factor_factory.new(tok[0], tok[1]) for tok in tokens]
    return factors


def build_rule(rule, rule_lexer, cond_factor_factory, act_factor_factory):
    cond_str, action_str = split_rule(rule)

    factors_map = lexer_build(cond_str, rule_lexer, cond_factor_factory)
    condition = ConditionMap(cond_str, factors_map)

    factors_map = lexer_build(action_str, rule_lexer, act_factor_factory)
    """ action 中只能是一个 Func 类型的 Factor """
    if not (isinstance(factors_map[0], Func) and len(factors_map) == 1):
        raise Exception("Error Action '%s' in rule '%s'" % (action_str, rule))
    action = factors_map[0]

    return rule, condition, action


class RuleSet:

    def __init__(self, name, rule_list, rule_lexer, cond_factor_factory, act_factor_factory):
        self.name = name
        self.rule_obj_set = []
        for rule in rule_list:
            rule_obj = build_rule(rule, rule_lexer, cond_factor_factory, act_factor_factory)
            self.rule_obj_set.append(rule_obj)

    def foreach(self, d):
        """
        遍历规则集，获得规则集的结果。
        每条规则由 Condition 和 Action 组成， Condition 若匹配中则执行 Action
        若Action有返回值，则返回Action的返回值，不再向后匹配，直接返回 Action 的返回值
        若Action执行未有返回值或返回值为None，继续向后匹配
        :param d:
        :return:
            None 可能是未匹配中condition，也可能是condition命中的action未有返回值
        """
        for rule_obj in self.rule_obj_set:
            rule, condition, action = rule_obj[0], rule_obj[1], rule_obj[2]
            result = condition.match(d)
            print("In rule set '%s' run '%s'. is result matching? %s" % (self.name, rule, result))
            if not result:
                continue
            action_result = action.value(d)
            if action_result: return action_result
        return None


class Ruler:

    class NoRuleSet(Exception):
        pass

    class RuleSetAlreadyExist(Exception):
        pass

    def __init__(self, name, default_entry):
        self.rule_map = {}
        self.name = name
        self.lexer = RuleLexer()
        self.condition_factor_factory = FactorFactory()
        self.action_factor_factory = FactorFactory()
        self.default_entry = default_entry
        self.init()

    def init(self):
        self.register_condition_func('basic_action.in_num_range', 'in_num_range')
        self.register_condition_func('basic_action.exist', 'exist')
        self.register_condition_func('basic_action.re_match', 're_match')

        self.register_action_func(self.__bulitin_goto_rule__, 'GOTO')


    def register_rule_set(self, name, rule_list):
        if name in self.rule_map:
            raise self.RuleSetAlreadyExist()
        self.rule_map[name] = RuleSet(name, rule_list, self.lexer,
                                      self.condition_factor_factory,
                                      self.action_factor_factory)

    def register_condition_func(self, f, name):
        self.condition_factor_factory.register(f, name)

    def register_action_func(self, f, name):
        self.action_factor_factory.register(f, name)

    def entry(self, d):
        return self._entry(self.default_entry, d)

    def _entry(self, name, d):
        if name not in self.rule_map:
            raise self.NoRuleSet()
        rule_set = self.rule_map[name]
        return rule_set.foreach(d)

    def __bulitin_goto_rule__(self, name, d):
        print("GOTO %s" % name)
        return self._entry(name, d)


if __name__ == "__main__":

    rule_main = [
        "IF exist(pkt.id1) THEN print('test print 1')",
        "IF exist(pkt.id1) THEN print('test print 2')",
        "IF exist(pkt.id1) THEN print('test print 3')",
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id1 == 2048 THEN GOTO('rule_1', __builtin_raw__)",
    ]

    rule_1 = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id2 == 778 THEN GOTO('rule_2', __builtin_raw__)",
    ]

    rule_2 = [
        "IF in_num_range(pkt.id1, 1, 10000) && pkt.id3 == 22 THEN accept()",
    ]


    p = {
        'pkt': {
            'id1': 2048,
            'id2': 778,
            'id3': 22,
            's': 'string',
        }
    }

    rule_map = Ruler('testRuleMap', 'main')

    # 注册条件匹配中的动作函数

    # 注册匹配成功后的结果动作函数
    def accept():
        print("ACCEPT !!!!")
        return 0, (), ()

    def drop():
        print("DROP !!!!")
        return -1, (), ()

    def print_s(s):
        print("print: %s" % s)

    rule_map.register_action_func(accept, 'accept')
    rule_map.register_action_func(drop, 'drop')
    rule_map.register_action_func(print_s, 'print')

    # 注册规则
    rule_map.register_rule_set('main', rule_main)
    rule_map.register_rule_set('rule_1', rule_1)
    rule_map.register_rule_set('rule_2', rule_2)


    ret = rule_map.entry(p)

    pprint.pprint(p)
    print ret


