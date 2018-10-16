# -*- coding:utf-8 -*-

import copy
import ply.lex as lex

from factor import Var, Func, Operator
from utils import array_printable


class RuleLexer:

    states = (
        ('in_func', 'inclusive'),
        ('paren', 'inclusive'),
    )

    tokens = (
        'LOGICAL_OPERATOR',
        'RELATIONAL_OPERATOR',

        'FUNCSTART',
        'FUNCSTOP',

        'LPAREN',
        'RPAREN',

        'VAR',
        'NUMBER',
        'STRING',
    )

    t_ANY_ignore = ' \t,'
    t_ANY_ignore_COMMENT = r'\#.*'

    t_LOGICAL_OPERATOR = r'&&|\|\|'
    t_RELATIONAL_OPERATOR = r'==|\!=|>=*|<=*'

    t_ANY_VAR = r'[a-zA-Z_@][0-9a-zA-Z._-]*'


    def t_ANY_NUMBER(self, t):
        r'\d+(.\d+)?'
        t.value =  float(t.value) if '.' in t.value else int(t.value)
        return t

    def t_ANY_STRING(self, t):
        r'\'([^\'\\]|\\\'|\\)*\''
        t.value = t.value[1:-1]
        return t

    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        # t.lexer.skip(1)

    def t_ANY_begin_func(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]+\('
        t.lexer.push_state('in_func')
        t.value = t.value[:-1]
        t.type = 'FUNCSTART'
        return t

    def t_func_end(self, t):
        r'\)'
        t.lexer.pop_state()
        t.type = 'FUNCSTOP'
        return t

    def t_begin_paren(self, t):
        r'\('
        t.lexer.push_state('paren')
        t.type = 'LPAREN'
        return t

    def t_paren_end(self, t):
        r'\)'
        t.lexer.pop_state()
        t.type = 'RPAREN'
        return t

    def analyse(self, data):
        try:
            self.lexer.input(data)
            tokens = []
            for tok in self.lexer:
                # DEBUG PRINT
                print self.lexer.lexstatestack, self.lexer.lexstate, (tok.type, tok.value)
                tokens.append((tok.type, tok.value))
        except lex.LexError, e:
            print "Error: %s" % e
            print data
            print ''.join([' ' for i in range(self.lexer.lexpos) ]) + '^'
            raise e

        return tokens

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)



def is_operand_type(operand):
    if isinstance(operand, Var) \
            or isinstance(operand, Func) \
            or type(operand) in [int, float, str, list]:
        return True
    return False


def is_operator_type(operator):
    if isinstance(operator, Operator):
        return True
    return False


def tokens_polymerize(tokens):
    """
    聚合 Tokens 中的 函数, 双括号
    :param tokens:
    :return:
    """
    # first polymerize FUNC tokens
    stack = [[]]
    for tok in tokens:
        if tok[0] == 'FUNCSTART':
            # stack push
            stack.append([])
        elif tok[0] == 'FUNCSTOP':
            func_args = tuple(stack.pop())
            tok = ('FUNC', (func_args[0][1], func_args[1:]))
        if tok[0] == 'LPAREN':
            stack.append([])
        elif tok[0] == 'RPAREN':
            func_args = tuple(stack.pop())
            tok = ('PAREN', func_args[1:])
        stack[-1].append(tok)

    if len(stack) != 1:
        raise Exception("TODO: 格式错误")

    return stack[0]


def relational_operator_polymerize(factors):
    """
    将 <比较运算: == != ...> 聚合为一个优先计算单元
    一个优先计算单元以 [] 记录
    :param factors:
    :return:
    """

    # factors 数量必须是单数:
    if len(factors) % 2 != 1:
        raise Exception("Error factors len %s" % len(factors))
    # 当只有一个函数作为条件时： if exist(pki.id) then accept()
    if len(factors) == 1 and isinstance(factors[0], Func):
        return factors

    i = 0
    while True:
        if i+2 > len(factors):
            break
        operand1, operator, operand2 = factors[i], factors[i+1], factors[i+2]
        if not is_operand_type(operand1):
            raise Exception("Operand1 type Error, %s " % str(operand1))
        if not is_operand_type(operand2):
            raise Exception("Operand2 type Error, %s " % str(operand1))
        if not is_operator_type(operator):
            raise Exception("Operator type Error, %s " % str(operator))
        operand1 = relational_operator_polymerize(operand1) if type(operand1) == list else operand1
        operand2 = relational_operator_polymerize(operand2) if type(operand2) == list else operand2

        prefix = factors[:i]
        tail = factors[i + 3:]
        new = [operand1, operator, operand2]
        if operator.t == 'RELATIONAL_OPERATOR':
            prefix.append(new)
        else:
            prefix.extend(new)
            i += 2
        prefix.extend(tail)
        factors = prefix

    return factors[0] if len(factors) == 1 else factors


