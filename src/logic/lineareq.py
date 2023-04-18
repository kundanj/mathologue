import re
import numpy as np

regexes = [ re.compile(p) for p in [ r"(?P<sign_x>[+-]?)(?P<var_x>\d{0,5}[a-zA-Z])\s*(?P<sign_y>[+-]{1})\s*(?P<var_y>\d{0,5}[a-zA-Z])\s*=\s*(?P<sign_n>[+-]?)(?P<var_n>-?\d{1,6})",  # 3x + 2y = -1
        r"(?P<sign_x>[+-]?)(?P<var_x>\d{0,5}[a-zA-Z])\s*(?P<sign_y>[+-]{1})\s*(?P<var_y>\d{0,5}[a-zA-Z])\s*(?P<sign_n1>[+-]{1})\s*(?P<var_n1>\d{1,6})\s*=\s*(?P<sign_n2>[+-]?)(?P<var_n2>\d{1,6})"  # -3x + 2y -1 = 0
                                     ] ]

def str_to_sign(str_sign):
    if ((str_sign is None) or (str_sign == '+') or (str_sign == '')):
        return 1
    else:
        return -1


def process_lineareq(question):
    num_arrs=[]
    var_arrs=[]
    var_names=[]
    eq_len=0
    stmt = None
    finish = False
    input_question = question
    for i, regex in enumerate(regexes):
        for match in re.finditer(regex, input_question):
            if (i == 0 or i == 1):
                if eq_len == 0:
                    eq_len = 2
                elif eq_len != 2:
                    stmt = "All equations must have similar number of variables"
                    return stmt
                vars = match.groupdict()

                numv1= re.search("\d*", vars.get('var_x')).group()
                numv2= re.search("\d*", vars.get('var_y')).group()
                if len(numv1) == 0:
                    numv1 = '1'
                if len(numv2) == 0:
                    numv2 = '1'
                varv1= re.search("[A-Za-z]+", vars.get('var_x')).group()
                varv2= re.search("[A-Za-z]+", vars.get('var_y')).group()
                temp_numarr=[None] * 2
                if (len(var_names) > 0):
                    if (set(var_names) != set([varv1, varv2])):
                        stmt = "All equations must have the same variables {0} {1}".format(var_names[0], var_names[1])
                        return stmt
                    temp_numarr[var_names.index(varv1)] = float(numv1) * str_to_sign(vars.get('sign_x'))
                    temp_numarr[var_names.index(varv2)] = float(numv2) * str_to_sign(vars.get('sign_y'))
                    num_arrs.append(temp_numarr)
                else:
                    num_arrs.append([float(numv1) * str_to_sign(vars.get('sign_x')), float(numv2) * str_to_sign(vars.get('sign_y'))])
                    var_names= [varv1, varv2]
                if (i == 1):
                    var_arrs.append(float(vars.get('var_n2')) * str_to_sign(vars.get('sign_n2')) - float(vars.get('var_n1')) * str_to_sign(vars.get('sign_n1')))
                else:
                    var_arrs.append(float(vars.get('var_n')) * str_to_sign(vars.get('sign_n')) )

                if (len(var_arrs) == eq_len):
                    finish = True
                    break

        if finish:
            break

    if finish:
        a = np.array(num_arrs)
        b = np.array(var_arrs)
        result = np.linalg.solve(a, b)
        ques = str(num_arrs[0][0]) + var_names[0] + ' + ' + str(num_arrs[0][1]) + var_names[1] + '=' + str(var_arrs[0]) + ' and '  + str(num_arrs[1][0]) + var_names[0] + ' + ' + str(num_arrs[1][1]) + var_names[1] + '=' + str(var_arrs[1])
        if (eq_len == 2):
            stmt = "Solution of {} : {} = {:.2f} and {} = {:.2f}".format(ques, var_names[0], result[0], var_names[1], result[1])

    return stmt
