# -*- coding:utf-8 -*-

import re
from lexer import RuleLexer
from factor import Var, Func, FactorFactory
import basic_action


def parse_rule_file(path):
    with open(path, 'r') as f:
        rule_lines = f.readlines()
        current_rule = None
        result = {}

        for i, line in enumerate(rule_lines):
            line = line.replace('\n', '')
            line_no = i + 1

            regMatch = re.match(r'^(?P<rule_name>[a-zA-Z_][a-zA-Z0-9_]*):\s*$', line)
            if regMatch: # is rule_name line
                rule_name = regMatch.groupdict()['rule_name']
                #print "start rule %s: " % rule_name
                if rule_name in result:
                    raise Exception("Duplicate rule '%s' at line %s" % (rule_name, line_no))
                result[rule_name] = []
                current_rule = rule_name
            elif re.match(r'^(\t|    )IF', line): # is rule line
                # print "rule: ", line
                if not current_rule:
                    raise Exception("No rule_name found befroe line %s" % line_no)
                line =  ' '.join(line.split()).lstrip().rstrip()
                result[current_rule].append(line)
            elif re.match(r'^\s*#', line): # is comment line
                #print "comment: ", line
                continue
            elif re.match(r'^\s*$', line): # is empty line
                #print "empty: ", line
                continue
            else:
                raise Exception("Error rule at line %s :\n`%s`" % (line_no, line))
        return result
    return None


def split_rule_if_else(rule):
    rule_pattern  = r'IF (?P<cond>[\S ]+) THEN '
    rule_pattern += r'(((?P<then_action>[\S ]+) (?=ELSE)ELSE (?P<else_action>[\S ]+))|(?P<action>[\S ]+))'
    rule_pattern += r' END'
    match_reg = re.match(rule_pattern, rule)
    if not match_reg:
        raise Exception("Error rule %s" % rule)
    gdict = match_reg.groupdict()
    if gdict['action'] and not gdict['else_action'] and not gdict['then_action']:
        return gdict['cond'], gdict['action'], None
    if not gdict['action'] and gdict['else_action'] and gdict['then_action']:
        return gdict['cond'], gdict['then_action'], gdict['else_action']
    raise Exception("Error rule %s" % rule)


def split_rule(rule):
    pattern = r"^IF (?P<cond>[\S ]+) THEN (?P<action>[\S ]+)"
    reg = re.compile(pattern)
    match = reg.result(rule)
    if not match:
        return None
    match = match.groupdict()
    return match['cond'], match['action']


def lexer_build(s, rule_lexer, factor_factory):
    tokens = rule_lexer.parse_toekns(s)
    factors = [factor_factory.new(tok[0], tok[1]) for tok in tokens]
    return factors


def build_rule(rule, rule_lexer, factor_factory):
    cond_str, then_str, else_str = split_rule_if_else(rule)

    factors_map = lexer_build(cond_str, rule_lexer, factor_factory)
    condition = FactorMap(cond_str, factors_map)

    factors_map = lexer_build(then_str, rule_lexer, factor_factory)
    then_action = FactorMap(cond_str, factors_map)

    else_action = None
    if else_str:
        factors_map = lexer_build(else_str, rule_lexer, factor_factory)
        else_action = FactorMap(cond_str, factors_map)

    return rule, condition, then_action, else_action


class FactorMap(object):

    def __init__(self, s, factors_map):
        self.s = s
        self.factors_map = factors_map

    def result(self, p):
        factors_map = self.factors_map
        match_result = self._result(factors_map, p)
        return match_result

    def _result(self, factors_map, p):
        stack = []
        # print array_printable(factors_map)
        for f in factors_map:
            # print f,"stack = %s" % array_printable(stack)
            if len(stack) == 0 or len(stack) == 2:
                if type(f) == list:
                    f = self._result(f, p)
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


class RuleSet:

    def __init__(self, name, rule_list, rule_lexer, factor_factory):
        self.name = name
        self.rule_obj_set = []
        for rule in rule_list:
            rule_obj = build_rule(rule, rule_lexer, factor_factory)
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
            rule, condition, then_action, else_action = rule_obj[0], rule_obj[1], rule_obj[2], rule_obj[3]
            result = condition.result(d)
            print("In rule set '%s' run '%s'. is result matching? %s" % (self.name, rule, result))
            action_result = None
            if result is True:
                action_result = then_action.result(d)
            else:
                if else_action:
                    action_result = else_action.result(d)
            if action_result:
                return action_result
        return None


class Ruler:

    class NoRuleSet(Exception):
        pass

    class RuleSetAlreadyExist(Exception):
        pass

    def __init__(self, name):
        self.rule_map = {}
        self.name = name
        self.lexer = RuleLexer()
        self.factor_factory = FactorFactory()
        self.init()

    def init(self):
        self.register_func(self.__bulitin_goto_rule__, '__goto__')

        self.register_func(basic_action.exist, 'exist')
        self.register_func(basic_action.re_match, 're_match')
        self.register_func(basic_action.in_num_range, 'in_num_range')

    def register_rule_set(self, name, rule_list):
        if name in self.rule_map:
            raise self.RuleSetAlreadyExist()
        self.rule_map[name] = RuleSet(name, rule_list, self.lexer,
                                      self.factor_factory)
    def register_func(self, f, name):
        self.factor_factory.register(f, name)

    def entry(self, name, d):
        if name not in self.rule_map:
            raise self.NoRuleSet()
        rule_set = self.rule_map[name]
        return rule_set.foreach(d)

    def __bulitin_goto_rule__(self, name, d):
        print("__goto__ %s" % name)
        return self.entry(name, d)
