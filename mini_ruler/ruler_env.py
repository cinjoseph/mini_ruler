
class EnvError(Exception):
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

    def set_var(self, var, value):
        if value != None:
            self.stack_top[var] = value

    def get_var(self, var_str):
        var_str_list = var_str.split('.')
        var = var_str_list[0]
        var_list = var_str_list[1:]

        for level in self.variables_stack:
            tmp = level.get(var, None)
            if tmp:
                var = tmp
                break
        else:
            raise Exception("name '%s' is not defind" % var)

        tmp = var
        s = var_str_list[0]
        for k in var_list:
            v = tmp.get(k, None)
            if not v:
                raise EnvError("No name '%s' found in %s " % (k, s))
            tmp = v
            s += '.%s' % k

        return tmp


#     self.var_symbol_tbl = {'local': {}, 'global': {}}
    #
    # def set_var(self, var, value, area='local'):
    #     if value != None:
    #         self.var_symbol_tbl[area][var] = value
    #
    # def get_var(self, var_str, area = 'local'):
    #     var_str_list = var_str.split('.')
    #     var = var_str_list[0]
    #     var_list = var_str_list[1:]
    #
    #     var = self.var_symbol_tbl[area].get(var, None)
    #     if not var:
    #         raise Exception("name %s' is not defind" % var)
    #
    #     tmp = var
    #     s = var_str_list[0]
    #     for k in var_list:
    #         v = tmp.get(k, None)
    #         if not v:
    #             raise EnvError("No name '%s' found in %s " % (k, s))
    #         tmp = v
    #         s += '.%s' % k
    #
    #     return tmp



# env = RulerEnv()
#
# env.set_var('a', {'b': {'c': 1}})
#
# print env.get_var('a.b.d')
