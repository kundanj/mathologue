import re
import spacy
from spacy.matcher import Matcher

def process_percent(question, nlp):
    matcher = Matcher(nlp.vocab)
    pattern = [[{"LIKE_NUM": True}, {"ORTH": "%"}, {"ORTH": "out", "OP": "*"}, {"TEXT": {"REGEX": "(from|of)"}}, {"LIKE_NUM": True}],
              [{"LIKE_NUM": True}, {"IS_ASCII": True, "OP": "*"}, {"LIKE_NUM": True}, {"ORTH": "%"}]]
    matcher.add("percent1", pattern)
    pattern = [[{"ORTH": "%"}, {"IS_ASCII": True, "OP": "*"}, {"LIKE_NUM": True}, {"ORTH": "out", "OP": "*"}, {"TEXT": {"REGEX": "(from|of)"}}, {"LIKE_NUM": True}],
                [{"LIKE_NUM": True}, {"ORTH": "out", "OP": "*"}, {"TEXT": {"REGEX": "(from|of)"}}, {"LIKE_NUM": True}, {"IS_ASCII": True, "OP": "*"}, {"ORTH": "%"}, {"IS_ASCII": True, "OP": "*"}, {"TEXT": {"REGEX": "(remainder|remaining|left)"}} ],
              [{"LIKE_NUM": True}, {"ORTH": "out", "OP": "*"}, {"TEXT": {"REGEX": "(from|of)"}}, {"LIKE_NUM": True}, {"IS_ASCII": True, "OP": "*"}, {"ORTH": "%"}, {"IS_ASCII": True, "OP": "*"} ]]
    matcher.add("percent2", pattern)
    pattern = [[{"LIKE_NUM": True}, {"POS": "NOUN"}, {"IS_ASCII": True, "OP": "*"}, {"IS_PUNCT": True, "OP": "*"}, {"LIKE_NUM": True},{"POS": "NOUN"}, {"IS_PUNCT": True, "OP": "*"}, {"IS_ASCII": True, "OP": "*"}, {"ORTH": "%"},{"LEMMA": "be", "OP": "*"}, {"POS": "NOUN"}],
              [{"LIKE_NUM": True}, {"POS": "NOUN"}, {"IS_ASCII": True, "OP": "*"}, {"IS_PUNCT": True, "OP": "*"}, {"LIKE_NUM": True},{"POS": "NOUN"}, {"IS_PUNCT": True, "OP": "*"}, {"IS_ASCII": True, "OP": "*"}, {"ORTH": "%"},{"IS_ASCII": True, "OP": "*"}, {"POS": "NOUN"},{"LEMMA": "be", "OP": "*"}, {"POS": "NOUN"}]]
    matcher.add("percent3", pattern) # forgot the contextof this type of question
    pattern = [[{"IS_ASCII": True, "OP": "*"}, {"LIKE_NUM": True}, {"IS_PUNCT": True, "OP": "*"}, {"IS_ASCII": True, "OP": "*"}, {"TEXT": {"REGEX": "(decrea?se?d|incre?a?se?d|changed)"}}, {"TEXT": {"REGEX": "(to|by)"}}, {"LIKE_NUM": True},{"IS_PUNCT": True, "OP": "*"}, {"IS_ASCII": True, "OP": "*"},  {"TEXT": {"REGEX": "(%|percent|percentage)"}} ],
              [{"TEXT": {"REGEX": "(up|down|decrea?se?d|incre?a?se?d|changed)"}}, {"TEXT": {"REGEX": "(from|by|to)"}}, {"LIKE_NUM": True}, {"ORTH": "%", "OP": "*"}, {"TEXT": {"REGEX": "(from|by|to)"}}, {"LIKE_NUM": True}, {"ORTH": "%", "OP": "*"}, {"IS_PUNCT": True, "OP": "*"}, {"IS_ASCII": True, "OP": "*"}, {"IS_PUNCT": True, "OP": "*"}, {"TEXT": {"REGEX": "(original|initial|change|new)"}} ]]
    matcher.add("percent4", pattern)

    stmt = None
    doc = nlp(question.lower())
    matches = matcher(doc)

    if matches:
        matches.sort(key = lambda x: x[2], reverse = True)
        (match_id, start, end) = matches[0]
        string_id = nlp.vocab.strings[match_id]
        if string_id == 'percent1':
            p, a = None, None
            if doc[start + 1].text == '%':
                p = int(doc[start].text)
                a = int(doc[end - 1].text)
            else:
                a = int(doc[start].text)
                p = int(doc[end - 2].text)

            if p is None or a is None:
                stmt = "You need to provide both percentage and amount to calculate"
            else:
                stmt = "{0} % of {1} is {2:f}".format(p,a, p/100 * a)
        elif string_id == 'percent2':
            p1, p2 = None, None
            for x in range(start, end):
                if (doc[x].pos_ == 'NUM'): #change this to detect numbers better... POS does not give check for only numbers but also words likee billion etc
                    if p1 is None:
                        p1 = int(doc[x].text)
                    else:
                        p2 = int(doc[x].text)

            if doc[end - 1].text in ['remaining', 'remainder','left']:
                stmt = "% of remainder is {:f}".format((p2 - p1)/p2 * 100)
            else:
                stmt = "% of {0} out of {1} is {2:f}".format(p1,p2, p1/p2 * 100)
        elif string_id == 'percent3':
            p1, p2 = None, None
            tx1, tx2, tx3 = None, None, None
            for x in range(start, end):
                if (doc[x].pos_ == 'NUM'):
                    if p1 is None:
                        p1 = int(doc[x].text)
                    else:
                        p2 = int(doc[x].text)
                if (doc[x].pos_ == 'NOUN' and doc[x].text != '%'):
                    if tx1 is None:
                        tx1 = doc[x].text
                    elif tx2 is None:
                        tx2 = doc[x].text
                    elif doc[x].text in [tx1, tx2]:
                        tx3 = doc[x].text

            if (tx3 is not None):
                if tx1 == tx3:
                    stmt = "% of {0} is {1:f}".format(tx1, p1/(p1 + p2) * 100)
                elif tx2 == tx3:
                    stmt = "% of {0} is {1:f}".format(tx2, p2/(p1 + p2) * 100)
            else:
                    stmt = "You haven't provided data for " + tx3 + " for me to calculate %"
        # price of a pair of trousers was decreased by 22% to 30. What was the original price of the trousers?
        elif string_id == 'percent4':
            a1, a2, p, a = None, None, None, None
            by = ''
            rev = False
            sign = 0
            for x in range(start, end):
                if (doc[x].pos_ == 'NUM'):
                    if (x < (len(doc) - 1)) and (('%' in doc[x + 1].text) or ( 'percent' in doc[x + 1].text )):
                        p = int(doc[x].text)
                        if (doc[x - 1].text == 'to'):
                            rev = True
                        elif (doc[x - 1].text == 'by'):
                            by = 'p'
                    else:
                        if (doc[x - 1].text == 'to'):
                            rev = True
                            a2 = int(doc[x].text)
                        elif (doc[x - 1].text == 'from'):
                            a1 = int(doc[x].text)
                        else:
                            if a1 is None:
                                a1 = int(doc[x].text)
                                if (doc[x - 1].text == 'by'):
                                    by = 'a1'
                            elif a2 is None:
                                a2 = int(doc[x].text)
                                if (doc[x - 1].text == 'by'):
                                    by = 'a2'
                elif (doc[x].pos_ == 'VERB' or doc[x].pos_ == 'ADV'): # include words like revenue down/up from etc
                    if re.match('incr|up|raise', doc[x].text.lower()): # check lemma here instead of word
                        sign = 1
                    elif re.match('decr|down|lower', doc[x].text.lower()):
                        sign = -1
                    elif ("change" in doc[x].text.lower()):
                        sign = -1

            if (p is not None):
                if (a2 is not None):
                    a = a2
                else:
                    a = a1
                if rev:
                    if by == 'p':
                        newval = a/ (1 + sign * p/100) # to take care of "decreased to 30 by 40%" types
                        offset = newval * p/100
                    else:
                        if by == 'a': # to take care of "decreased to 30% by 40" typs
                            newval = a / (1 + sign * p/100)
                            offset = newval * p/100
                        else:
                            newval = a * p/100 # to take care of "decreaed to 30% from 40" type
                            offset = abs(a + sign * newval)
                else: # to take care of "decreased by 30% from 40" types
                    if by == 'p':
                        offset = a * p/100
                        newval = a + sign * offset

                if doc[end - 1].text in ['original','initial','new','final']:
                    stmt = " {0} ".format(newval)
                else:
                    stmt = " {0} ".format(offset)
            else:
                if (rev):
                    if (by == 'a1'):
                        offset = (a1 / (a2 - sign* a1) ) * 100
                    elif (by == 'a2'):
                        offset = (a2 / (a1 - sign* a2) ) * 100
                    else:
                        if (sign == 1):
                            offset = ((a2 - a1) / a1) * 100
                        elif (sign == -1):
                            offset = ((a1 - a2) / a1) * 100
                elif by == 'a1':
                    offset = (a1/a2) * 100
                elif by == 'a2':
                    offset = (a2/a1) * 100

                stmt = "{0}%".format(offset)

    return stmt
