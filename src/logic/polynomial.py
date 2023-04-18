import re
from numpy.polynomial import Polynomial

regexes = [ re.compile(p) for p in [ r"(?P<sign>(^[+-]?)|([+-]))\s*(?P<coeff>[0-9]{0,4})\s*(?P<variab>[a-z]{1}(?=(\d|\s|\+|-|squar|cub)))(?P<expo>[0-5]|(\s*square?d?)|(\s*cubed?))?\s*(?P<const>[+|-]\s*\d{1,4}\b)?" ] ]

def str_to_sign(str_sign):
    if ((str_sign is None) or (str_sign == '+') or (str_sign == '')):
        return 1
    else:
        return -1


def process_polynomial(question):
    stmt = None
    result = 0
    for i, regex in enumerate(regexes):
        prev_varx = ''
        coeff_arr=[]
        coeff_arr = [0 for x in range(6)]
        solved = False
        for match in re.finditer(regex, question):
            solved=True
            vars = match.groups()
            vars_named = match.groupdict()
            varsign = 1
            varcoef = 1
            if (vars_named.get("sign") is not None) and (vars_named.get("sign").strip() == '-'):
                varsign = -1
            if vars_named.get("coeff").strip() != '':
                varcoef = int(vars_named.get("coeff"))
            varx = vars_named.get("variab").strip()
            varexpo = vars_named.get("expo")
            if varexpo is None:
                varexpo = 1
            elif varexpo.strip().startswith('squa'):
                varexpo = 2
            elif varexpo.strip().startswith('cub'):
                varexpo = 3
            coeff_arr[int(varexpo)] = varcoef * varsign
            if vars_named.get("const") is not None:
                coeff_arr[0] = int( vars_named.get("const").replace(' ','') )
            if prev_varx == '':
                prev_varx = varx
            elif varx != prev_varx:
                return stmt
        if solved:
            p = Polynomial(coeff_arr)
            root_arr = [round(x,2) for x in p.roots() if isinstance(x, float)]
            stmt = "$POLYNOMIAL$ {} {}".format(coeff_arr, root_arr)
            return stmt

    return stmt
