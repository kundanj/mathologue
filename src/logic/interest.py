import re
import spacy
import numpy as np
from tools import redis_adapter

regexes = [ re.compile(p, re.IGNORECASE) for p in [ r"(find|what)?\s*.?s?(will\s*be)?\s*(the)?\s*(co?mpound\s*inte?re?st|interest|comp\s*inte?re?s?t?)\s*(on|for)\D{0,10}(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(compounded|per|paid|calculated)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?",
                                     r"(find|what)?\s*.?s?(will\s*be)?\s*(the)?\s*(co?mpound\s*inte?re?st|interest|comp\s*inte?re?s?t?)\s*(on|for)\D{0,10}(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(compounded|per|paid|calculated)?\s*(?P<var_tenuremetric>(annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?\D{1,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))",
                                     r"(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(invested|borrowed|kept|saved|deposite?d?)?\D{1,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(compounded)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?\D{1,15}(find|what|how\s*much)\D{1,20}(the)*\s*(co?mpound\s*inte?re?st|comp\s*inte?re?s?t?|maturity|amount)",
                                     r"(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(invested|borrowed|kept|saved|deposite?d?)\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(compounded)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?\D{0,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,15}(find|what|how\s*much)\D{1,20}(the)*\s*(co?mpound\s*inte?re?st|comp\s*inte?re?s?t?|maturity|amount)",
                                     r"(find|what)?\s*.?s?(will\s*be)?\s*(the)?\s*(principal|original|invested|sum)?\s*(amount)?\s*(if|that|will)\s*\D{0,14}?(((sums\s*(up)?|adds\s*(up)?|amounts?)\s*to)|((maturity|final|compounded)?(amount)?\s*is))\s*\D{1,7}(?P<var_amount>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(in|after)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly)?\s*(compound\s*interest)?\s*(compounded|per|paid|calculated)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?",
                                     r"(principal|original|invested|sum)?\s*(amount)?\s*\D{0,14}?((sums\s*(up)?|adds\s*(up)?|amounts?)\s*to)\D{0,10}?((maturity|final|compounded)?(amount)?)\s*\D{1,7}?(?P<var_amount>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(in|after)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(p.?\s*a.?|per\s*annum|annuall?y?|yearly)?\s*(compound\s*interest)?\s*(compounded|per|paid|calculated)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?\D{0,14}?(find|what)\s*.?s?(will\s*be)?\s*(the)?\s*",
                                     r"(principal|original|invested|sum)?\s*(amount)?\s*(will)?\s*\D{0,14}?((sums\s*(up)?|adds\s*(up)?|amounts?)\s*to)\D{0,5}((maturity|final|compounded)?\s*(amount)?)\s*\D{1,7}(?P<var_amount>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(in|after)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(p.?\s*a.?|per\s*annum|annuall?y?|yearly)?\s*((compound)?\s*interest)?\s*(compounded|per|paid|calculated)?\s*(?P<var_tenuremetric>(p.?\s*a.?|(per)?\s*annum|annuall?y?|yearly|half\s*yearly|monthly|quarterly))?\D{0,10}(find|what)?\s*.?s?(will\s*be)?\s*(the)?(sum|amount|original|principal)",
                                     r"(find|what)?\s*.?s?\s*(will\s*be)?\s*(the)*\s*(si?mple\s*inte?re?st|simp\s*inte?re?s?t?)\s*on\D{0,10}(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)",
                                     r"(find|what)?\s*.?s?\s*(will\s*be)?\s*(the)*\s*(si?mple\s*inte?re?st|simp\s*inte?re?s?t?)\s*on\D{0,10}(sum|amount|principal)?\s*(of)?\s*\D{1,7}(?P<var_prin>(\d{1,20}.?\s*,?\s*)+)\s*\D{1,18}(at|rate\s*o?f?|@)\s*(?P<var_rate>(\d{1,7}.?\s*,?\s*)+)\s?(%|percent|perc)\s*(p.?\s*a.?|per\s*annum|annuall?y?|yearly)?\D{1,10}(for|after|period)\D{1,8}(?P<var_tenure>[0-9]{1,4})\s*(?P<var_termtype>(years|yrs|mon|months|days))" ] ]


# 0 what will be the compound interest on a sum of Rs. 7500 after 2 years at the rate of 4 % annually
# 1 what will be the compound interest on a sum of Rs. 25,000 at the rate of 12 % annual for 3 years
# 0 find compound interest on Rs. 7500 at 4% per annum for 2 years, compounded annually
# 2 a sum of USD 25,000 is deposited for 2 years at an interest rate of 3%  quarterly what is the final amount
# 3 if you deposit an  4000 into an for 5 years at 6% compounded quarterly how much final amount will I get
#a sum of USD 25,000 is deposited at  rate of 3% for 2 years  what is the final amount
# 4 find the principal that amounts to Rs. 4913 in 3 years at 6.25 % per annum  compounded annually| what investment will amount to Rs.4913 in 3 years at 4.33% per annum compound interest compounded annually


def compound_int(principle, amount, rate, time, n):
    if (amount is None):
        result = principle * (pow((1 + ((rate / 100)/ n ) ), n * time))
    elif (principle is None):
        result = amount / (pow((1 + ((rate / 100)/ n ) ), n * time))
    return result


def simple_int(principle, amount, rate, time, interest):
    if (interest is None):
        if (amount is None):
            result = principle * rate * time /100
        elif (principle is None):
            result = amount - principle * rate * time /100
    else:
        result = (100 * interest) / (rate * time)
    return result


def format_params(principle, amount, rate, time, term_type, comp_freq):
    prin = None
    amt = None
    if principle is not None:
        prin = float(re.sub(',','',principle))
    if amount is not None:
        amt = float(re.sub(',','',amount))
    rt = float(rate)
    t = float(time)
    freq = None

    if any(c in term_type for c in ['year','yrs']):
        t = t
    elif any(c in term_type for c in ['months', 'mon']):
        t = float(t/12)
    elif any(c in term_type for c in ['days', 'day']):
        t = float(t/365)

    if (comp_freq is None):
        freq = 1
    elif any(c in comp_freq for c in ['half year']):
        freq = 2
    elif any(c in comp_freq for c in ['quarter']):
        freq = 4
    elif any(c in comp_freq for c in ['p.a.','pa','p.a','annual','year','annum','p. a.']):
        freq = 1
    return (prin, amt, rt, t, freq)


def process_interest(ques, nlp):
    stmt = None
    result = 0
    ques_code = ''
    question = re.sub(r'[,?!;]','',ques)
    for i, regex in enumerate(regexes):
        match = regex.search(question)
        if (match and i in (0,1,2,3,4,5,6,7)):
            vars = match.groupdict()
            if vars.get('var_tenuremetric') is None:
                tenuremet = 'p.a'
            else:
                tenuremet = vars.get('var_tenuremetric')
            if (i in (0,1)):
                (p, a, r, t, f) = format_params(vars.get('var_prin'), None, vars.get('var_rate'), vars.get('var_tenure'), vars.get('var_termtype'), vars.get('var_tenuremetric'))
                result = compound_int(p, None, r, t, f) - p
                stmt = "Compound interest for {:.2f} @ {} % {} for {} {} is {:.2f}".format(p,r,tenuremet, vars.get('var_tenure'), vars.get('var_termtype'), result)
                ques_code = 'int-ci'
                break
            elif (i in (2,3)):
                (p, a, r, t, f) = format_params(vars.get('var_prin'), None, vars.get('var_rate'), vars.get('var_tenure'), vars.get('var_termtype'), tenuremet)
                result = compound_int(p, None, r, t, f)
                stmt = "Maturity amount for {:.2f} @ {} % {} for {} {} is {:.2f}".format(p,r,tenuremet, vars.get('var_tenure'), vars.get('var_termtype'), result)
                ques_code = 'int-amt'
                break
            elif (i in (4, 5, 6)):
                (p, a, r, t, f) = format_params(None, vars.get('var_amount'), vars.get('var_rate'), vars.get('var_tenure'), vars.get('var_termtype'), tenuremet)
                result = compound_int(None, a, r, t, f)
                stmt = "The principal that gives an amount of {:.2f} for a rate of {} % {} and tenure of {} {} is {:.2f}".format(a,r,vars.get('var_tenuremetric'), vars.get('var_tenure'), vars.get('var_termtype'), result)
                ques_code = 'int-prin'
                break
            elif (i in (7,6)):
                (p, a, r, t, f) = format_params(vars.get('var_prin'), None, vars.get('var_rate'), vars.get('var_tenure'), vars.get('var_termtype'), tenuremet)
                result = simple_int(p, None, r, t, None)
                stmt = "Simple interest for {:.2f} @ {} % for {} {} is {:.2f}".format(p,r, vars.get('var_tenure'), vars.get('var_termtype'), result)
                ques_code = 'int-si'
                break

    if len(ques_code) > 0:
        vars = {"p": p, "a": a, "r": r, "t": t, "f": f}
        subcontext = { "ques_code" : ques_code, "vars": vars }
        context_obj = {}
        context_obj['context'] = "interest"
        context_obj['subcontext'] = subcontext

    return stmt
