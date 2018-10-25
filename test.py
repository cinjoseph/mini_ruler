from mini_ruler.ruler import Ruler, parse_rule_file
from pprint import pprint

if __name__ == "__main__":

    p = {
        'pkt': {
            'id1': 2048,
            'id2': 778,
            'id3': 22,
            's': 'string',
            'level1': [1, 2, 3]
        }
    }

    print "input packet is :"
    pprint(p)
    print ""

    ruler = Ruler('testRuleMap')

    def accept():
        print("ACCEPT !!!!")
        return 0, (), ()

    def drop():
        print("DROP !!!!")
        return -1, (), ()

    def print_s(s):
        print("print: %s" % s)

    ruler.register_func(accept, 'accept')
    ruler.register_func(drop, 'drop')
    ruler.register_func(print_s, 'print')

    rules = parse_rule_file('./test.rule')
    for rule_name, rules in rules.items():
        ruler.register_rule_set(rule_name, rules)



    ret = ruler.entry('main', p)


    print ret
