# -*- coding:utf-8 -*-

import ply.lex as lex


class RuleLexer:

    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        # t.lexer.skip(1)

    t_ANY_ignore            = ' \t,'
    t_ANY_ignore_COMMENT    = r'\#.*'

    states = (
        ('func', 'exclusive'),
    )

    tokens = (
        'LOGICAL_OPERATOR',
        'RELATIONAL_OPERATOR',
        'ARITHMEITC_OPERATOR',

        'FUNCSTART',
        'FUNCSTOP',

        'LPAREN',
        'RPAREN',

        # 'COMMA',

        'ID',

        'INTEGER',
        'STRING',
        'BOOL',
        # 'NULL',
    )

    t_ANY_LOGICAL_OPERATOR      = r'&&|\|\|'
    t_ANY_RELATIONAL_OPERATOR   = r'==|\!=|>=*|<=*|~='
    t_ANY_ARITHMEITC_OPERATOR   = r'\+|-|\*|/'

    t_ANY_LPAREN  = r'\('
    t_ANY_RPAREN  = r'\)'

    # t_func_COMMA = r','


    def t_ANY_BOOL(self, t):
        r'\b(TRUE|FALSE)\b'
        t.value = True if t.value == "TRUE" else False
        return t

    # def t_ANY_NULL(self, t):
    #     r'\bNULL\b'
    #     t.value = None
    #     return t

    def t_ANY_INTEGER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ANY_STRING(self, t):
        r'\"[^\"]*\"'
        t.value = t.value[1:-1]
        return t

    def t_ANY_begin_func(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]+\('
        t.lexer.push_state('func')
        t.value = t.value[:-1]
        t.type = 'FUNCSTART'
        return t

    def t_func_end(self, t):
        r'\)'
        t.lexer.pop_state()
        t.type = 'FUNCSTOP'
        return t

    def t_ANY_ID(self, t):
        r'[a-zA-Z_@][\w_-]*(\.[a-zA-Z_@][\w_-]*)*'
        # r'[a-zA-Z_][\w_-]*'
        return t

    def parse_call(self, start_tok):
        try:
            args = []
            for tok in self.lexer:
                tok = (tok.type, tok.value)
                if tok[0] == 'FUNCSTOP':
                    break
                elif tok[0] == 'FUNCSTART':
                    tok = self.parse_call()
                args.append(tok)
        except StopIteration:
            raise Exception('Lost FUNCSTOP')

        tok = ('CALL', (start_tok[1], tuple(args)))
        return tok


    def parse_toekns(self, data):
        try:
            self.lexer.input(data)
            lex_tokens = []
            for tok in self.lexer:
                # DEBUG PRINT
                # print(self.lexer.lexstatestack, self.lexer.lexstate, (tok.type, tok.value))
                tok = (tok.type, tok.value)
                print tok

                if tok[0] == 'FUNCSTART':
                    tok = self.parse_call(tok)

                lex_tokens.append(tok)

        except(lex.LexError) as e:
            print("Error: %s" % e)
            print(data)
            print(''.join([' ' for i in range(self.lexer.lexpos) ]) + '^')
            raise e
        return lex_tokens

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)



if __name__ == "__main__":

    from pprint import pprint

    from calc import calc

    from ruler_env import RulerEnv

    from basic_action import re_match

    lexer = RuleLexer()

    env = RulerEnv()

    env.set_var('re_match', re_match)



    # data = 'a.b == "test" + "str" && 1 + 2047 == 2048 '
    data = 're_match("\d", "1")'

    tokens = lexer.parse_toekns(data)


    # print
    # pprint(tokens)
    # print

    env.push()

    env.set_var('a', {'b': 'teststr'})

    print calc(env, tokens)

    env.pop()
