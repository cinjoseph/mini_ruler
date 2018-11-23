# -*- coding:utf-8 -*-


calc_tbl = {
    '!': lambda x, y=None: not x,
    '~=': lambda x, y: x in y,

    '&&': lambda x, y: x and y,
    '||': lambda x, y: x or y,

    '>': lambda x, y: x > y,
    '>=': lambda x, y: x >= y,
    '<': lambda x, y: x < y,
    '<=': lambda x, y: x <= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y,

    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
}

def baisc_calc(op, x, y=None):
    result = calc_tbl[op](x, y)
    return result

def get_token_value(env, tok):
    if tok[0] == 'ID':
        value = env.get_var(tok[1])
    elif tok[0] == 'CALL':
        call, args = tok[1][0], tok[1][1]
        call = env.get_var(call)
        new_args = [ get_token_value(env, arg) for arg in args ]
        value = call(*new_args)
    else:
        value = tok[1]
    return value


def create_token(x):
    if type(x) == unicode: x = str(x)
    if type(x) == int: return ('INTEGER', x)
    if type(x) == float: return ('FLOAT', x)
    if type(x) == str: return ('STRING', x)
    if type(x) == bool:  return ('BOOL', x)
    if type(x) == type(None):  return ('NULL', None)
    if type(x) == tuple:  return ('TUPLE', x)
    raise Exception('Unknow token type %s %s' % (type(x), x))


def token_calc(env, op, x, y=None):
    op = op[1]
    x = get_token_value(env, x)
    y = get_token_value(env, y) if y else None

    result = baisc_calc(op, x, y)

    result = create_token(result)
    return result

class OperatorError(Exception):
    def __init__(self, err):
        Exception.__init__(self, err)


class Operator():
    op_tbl = [
        # 优先级低
        ['='],
        ['||'],
        ['&&'],
        ['==', '!=', '~='],
        ['>', '>=', '<', '<='],
        ['+', '-'],
        ['*', '/'],
        ['!'],
        ['.'],
        ['call', 'item'],
        # 优先级高
    ]

    op_level = {}
    for i, one_level in enumerate(op_tbl):
        for op in one_level:
            op_level[op] = i

    @classmethod
    def level(cls, op):
        if not op in cls.op_level:
            raise OperatorError("operator `%s` does not support" % op)
        return cls.op_level[op]


class CalcStack:

    def __init__(self):
        self.stack = [([], [])]
        self.operands = self.stack[-1][0]
        self.operators = self.stack[-1][1]

    def push(self):
        self.stack.append(([], []))
        self.operands = self.stack[-1][0]
        self.operators = self.stack[-1][1]

    def pop(self):
        operands, operators = self.stack.pop()
        self.operands = self.stack[-1][0]
        self.operators = self.stack[-1][1]
        return operands, operators

def calc(env, tokens):

    result = []

    stack = CalcStack()

    def calc_stack_top():
        # print "calc_stack_top"
        optr = stack.operators.pop()
        if optr[0] in ['NOT_OPERATOR']: # 单目运算符
            oprd2, oprd1 = None, stack.operands.pop()
        else: # 双目运算符
            oprd2, oprd1 = stack.operands.pop(), stack.operands.pop()
        result = token_calc(env, optr, oprd1, oprd2)
        stack.operands.append(result)

    def flush_out_stack():
        # print "flush_out_stack"
        while len(stack.operators):
            # print("optr: " + str(stack.operators))
            # print("oprd: " + str(stack.operands))
            calc_stack_top()
            # print("optr: " + str(stack.operators))
            # print("oprd: " + str(stack.operands))

        if len(stack.operands) > 1:
            raise Exception('Stack is not balance')
        result.append(stack.operands[0])

    tok_iter = iter(tokens)

    tok = tok_iter.next()
    while True:
        try:
            # print tok

            if tok[0] in ['INTEGER', 'FLOAT', 'STRING', 'BOOL', 'NULL']:
                stack.operands.append(tok)
                tok = tok_iter.next()
            elif tok[0] in ['ID', 'CALL']:
                stack.operands.append(create_token(get_token_value(env, tok)))
                tok = tok_iter.next()
            elif tok[0] in ['LOGICAL_OPERATOR', 'RELATIONAL_OPERATOR', 'ARITHMEITC_OPERATOR', 'NOT_OPERATOR']:
                if not len(stack.operators):
                    stack.operators.append(tok)
                    tok = tok_iter.next()
                else:
                    if Operator.level(stack.operators[-1][1]) < Operator.level(tok[1]):
                        stack.operators.append(tok)
                        tok = tok_iter.next()
                    else:
                        calc_stack_top()
            elif tok[0] == 'LPAREN':
                stack.push()
                tok = tok_iter.next()
            elif tok[0] == 'RPAREN':
                flush_out_stack()
                operands, _ = stack.pop()
                stack.operands.append(operands)
                tok = tok_iter.next()
            else:
                raise Exception('Unknow tok %s' % str(tok))
        except(StopIteration):
            flush_out_stack()
            break
        finally:
            # print("")
            # print("optr: " + str(stack.operators) )
            # print("oprd: " + str(stack.operands) )
            pass

    return stack.operands[0][1]
