# -*- coding:utf-8 -*-

class RulerEnvError(Exception):
    def __init__(self, err):
        Exception.__init__(self, err)


class RulerEnv:

    def __init__(self):
        self.variables_stack = [{}]
        self.stack_top = self.variables_stack[-1]

    def push(self):
        self.variables_stack.append({})
        self.stack_top = self.variables_stack[-1]

    def pop(self):
        if len(self.variables_stack) == 1:
            raise Exception('variables_stack is 1, can not pop variable stack, ')
        self.variables_stack.pop()
        self.stack_top = self.variables_stack[-1]

    def foreach_get_var(self, var_str):
        for level in self.variables_stack:
            var = level.get(var_str, None)
            if var:  break
        else:
            raise Exception("name '%s' is not defind" % var_str)
        return var

    def set_var(self, var, value):
        if value != None:
            self.stack_top[var] = value

    def get_var(self, var_str):
        var_str_list = var_str.split('.')
        var_name, var_list = var_str_list[0], var_str_list[1:]

        var = self.foreach_get_var(var_name)

        result, s = var, var_str_list[0]
        for k in var_list:
            v = result.get(k, None)
            if not v:
                raise RulerEnvError("No name '%s' found in %s " % (k, s))
            result = v
            s += '.%s' % k

        return result


