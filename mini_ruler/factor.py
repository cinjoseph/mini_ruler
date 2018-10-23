# -*- coding:utf-8 -*-
import importlib


def get_plugin_module(module_path):
    m = module_path.rsplit('.', 1)
    plugin_name = m[1]
    m = importlib.import_module(m[0])
    plugin = getattr(m, plugin_name, None)
    return plugin


class FactorFactory:

    def __init__(self):
        self.func_factory = FuncFactory()

    def register(self, func, func_name):
        self.func_factory.register(func, func_name)

    def create_factor(self, t, v):
        """
        转化 token 为 基础因子
        :param t:
        :param v:
        :return:
        """
        if t in ['NUMBER', 'STRING']:
            return v
        elif t == 'VAR':
            return Var(v)
        elif t == 'FUNC':
            func_name, arg_list = v
            arg_list = [self.create_factor(*f) for f in arg_list]
            return self.func_factory.new(func_name, arg_list)
        elif t == 'RELATIONAL_OPERATOR' or t == 'LOGICAL_OPERATOR':
            return Operator(t, v)
        elif t == 'PAREN':
            return [self.create_factor(*f) for f in v]
        else:
            raise Exception('(%s,%s)' % (str(t), str(v)))

    def new(self, t, v):
        return self.create_factor(t, v)


class FuncFactory:

    class RegisterError(Exception):
        def __init__(self, err):
            Exception.__init__(self, err)

    def __init__(self):
        self.func_set = {}

    def register_module(self, func, func_name):
        if func_name in self.func_set:
            raise self.RegisterError('Duplicate register func_set: %s' % func_name)
        self.func_set[func_name] = func

    def register(self, func, func_name):
        if not hasattr(func, '__call__'):
            func = get_plugin_module(func)
        if not func_name:
            func_name = func.func_name
        self.register_module(func, func_name)

    def new(self, name, arg_list):
        if name not in self.func_set:
            raise self.RegisterError('No register func_set: %s' % name)
        rannable = self.func_set[name]
        return Func(rannable, arg_list)


class Func:

    def __init__(self, runnable, arg_list):
        self.runnable = runnable
        self.arg_list = arg_list

    def __str__(self):
        s = ''
        for i, a in enumerate(self.arg_list):
            s += ' ' if i!=0 else ''
            s += str(a)
            s += ',' if i!=len(self.arg_list) - 1 else ''
        return "%s(%s)" % (self.runnable.func_name, s)

    def do(self, p):
        new_arg_list = []
        for arg in self.arg_list:
            if isinstance(arg, Var):
                arg = arg.get_value(p)
            elif isinstance(arg, Func):
                arg = arg.do()
            else:
                pass
            new_arg_list.append(arg)
        return self.runnable(*new_arg_list)


class VarNotExist(Exception):
    def __init__(self, err=None):
        Exception.__init__(self, err)


class Var:

    def __init__(self, var):
        self.var = var
        self.key_list = var.split('.')

    def __str__(self):
        return "VAR(%s)" % self.var

    def get_value(self, d):
        if len(self.key_list) == 1:
            if self.key_list[0] == '__builtin_raw__':
                return d
            if self.key_list[0] == 'TRUE':
                return True
            if self.key_list[0] == 'FALSE':
                return False
            if self.key_list[0] == 'NONE':
                return None

        return self._get_value(d)

    def _get_value(self, d):
        value = d
        for key in self.key_list:
            try:
                value = value[key]
            except KeyError:
                return None
                # raise VarNotExist(self.var)
        return value


class NotOperator:

    def __init__(self, v):
        self.v = v


class Operator:

    def __init__(self, t, v):
        self.t = t
        self.v = v

    def __str__(self):
        return "Operator(%s)" % self.v

    def calc(self, x, y):
        if self.v == '==':
            return x == y
        elif self.v == '!=':
            return x != y
        elif self.v == '>':
            return x > y
        elif self.v == '>=':
            return x >= y
        elif self.v == '<':
            return x < y
        elif self.v == '<=':
            return x <= y
        elif self.v == '||':
            return x or y
        elif self.v == '&&':
            return x and y
        else:
            Exception('Unkonw operator %s ' % (str(self.t), str(self.v)))

