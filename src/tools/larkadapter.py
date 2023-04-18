import re
import math
import numbers
from lark import Lark, Transformer, v_args


def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True


calc_grammar = """
    ?start: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" product  -> mul
        | product "/" product  -> div
        | log
        | trig

    ?log: /log\s*(of)?/ ("(")?  NUMBER (")")? (/(to)?\s*(the)?\s*base\s*/ NUMBER)? -> logr
    | /log\s*(of)?/ ("(")?  log (")")? (/(to)?\s*(the)?\s*base\s*/ NUMBER)? -> logr

    ?trig: /(sin|cos|tan)\s*(of)?/ ("(")?  NUMBER  (/(degrees|degree|deg)/)? (")")? -> trignom
        | /(sin|cos|tan)\s*(of)?/ ("(")?  trig (")")? -> trignom

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = float

    def __init__(self):
        self.vars = {}

#    def assign_var(self, name, value):
#        self.vars[name] = value
#        return value

    def logr(self, *args):
        a, b = None, 10
        for x in args:
            if is_number(x):
                if a is None:
                    a = float(x)
                else:
                    b = float(x)
        value = math.log(a,b)
        return value

    def trignom(self, *args):
        value = 0
        deg = True
        param = None
        for x in args:
            if is_number(x):
                param = float(x)
            elif x.startswith('deg'):
                deg = True
        if (args[0].strip().startswith('sin')):
            if deg:
                value = math.sin(math.radians(param))
            else:
                value = math.sin(param)
        elif (args[0].strip().startswith('cos')):
            if deg:
                value = math.cos(math.radians(param))
            else:
                value = math.cos(param)
        elif (args[0].strip().startswith('tan')):
            if deg:
                value = math.tan(math.radians(param))
            else:
                value = math.tan(param)
        return value


def parse_expression(stmt):
    s = stmt
    while re.search(r"[\d.]+\s+(X|multiply(\s+by)?)\s+[\d.]+", s, flags=re.IGNORECASE) is not None:
        s = re.sub(r"\s(X|multiply(\s+by)?)\s" , " * ", s, 1, flags=re.IGNORECASE)
    while re.search(r"[\d.]+\s+(X|divide(\s+by)?)\s+[\d.]+", s, flags=re.IGNORECASE) is not None:
        s = re.sub(r"\s(X|divide(\s+by)?)\s" , " / ", s, 1, flags=re.IGNORECASE)
    return calc(s)

calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse
