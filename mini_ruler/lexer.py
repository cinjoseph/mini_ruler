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
        ('paren', 'exclusive'),
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

    t_INITIAL_paren_LOGICAL_OPERATOR      = r'&&|\|\|'
    t_INITIAL_paren_RELATIONAL_OPERATOR   = r'==|\!=|>=*|<=*'

    t_ANY_VAR               = r'[a-zA-Z_@][0-9a-zA-Z._-]*'

    def t_ANY_NUMBER(self, t):
        r'\d+(.\d+)?'
        t.value =  float(t.value) if '.' in t.value else int(t.value)
        return t

    def t_ANY_STRING(self, t):
        r'\'([^\'\\]|\\\'|\\)*\''
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

    def t_ANY_begin_paren(self, t):
        r'\('
        t.lexer.push_state('paren')
        t.type = 'LPAREN'
        return t

    def t_paren_end(self, t):
        r'\)'
        t.lexer.pop_state()
        t.type = 'RPAREN'
        return t

    def parse_toekns(self, data):
        try:
            self.lexer.input(data)
            lex_tokens = []
            for tok in self.lexer:
                # DEBUG PRINT
                # print(self.lexer.lexstatestack, self.lexer.lexstate, (tok.type, tok.value))
                tok = (tok.type, tok.value)

                if tok[0] == 'FUNCSTOP':
                    func_name, args = None, []
                    while len(lex_tokens):
                        history_tok = lex_tokens.pop()
                        if history_tok[0] == 'FUNCSTART':
                            func_name = history_tok[1]
                            break
                        args.insert(0, history_tok)
                    if not func_name:
                        raise Exception("Can not find FUNCSTART")
                    tok = ('FUNC', (func_name, tuple(args)))
                elif tok[0] == 'RPAREN':
                    args = []
                    while len(lex_tokens):
                        history_tok = lex_tokens.pop()
                        if history_tok[0] == 'LPAREN':
                            break
                        args.insert(0, history_tok)
                    tok = ('PAREN', tuple(args))

                lex_tokens.append(tok)

                if len(lex_tokens) >= 3 \
                    and lex_tokens[-3][0] in ['VAR', 'NUMBER', 'STRING', 'FUNC'] \
                    and lex_tokens[-2][0] in ['RELATIONAL_OPERATOR'] \
                    and lex_tokens[-1][0] in ['VAR', 'NUMBER', 'STRING', 'FUNC'] \
                    :
                    oprd2, optr, oprd1 = lex_tokens.pop(), lex_tokens.pop(), lex_tokens.pop()
                    tok = ('PAREN', (oprd1, optr, oprd2))
                    lex_tokens.append(tok)
        except(lex.LexError) as e:
            print("Error: %s" % e)
            print(data)
            print(''.join([' ' for i in range(self.lexer.lexpos) ]) + '^')
            raise e
        return lex_tokens

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
