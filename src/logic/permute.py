import re
import math
import spacy

regexes = [ re.compile(p, re.IGNORECASE) for p in [ r"lett?ers?\sof\s*(the)*\s*wo?rd\s+[A-Z|a-z]{2,12}\s+how\s*many\s*(distinct|unique|diff?err?ent)|how\s*many\s*(distinct|unique|diff?err?ent)*[\s\S]*arrange\s*lett?ers?\s*of\s*(the)*\s*wo?rd\s*[A-Z|a-z]{2,12}",
                                     r"how\smany\s*(?P<var_r>\d)*\s(digits?|numbers?|permutations)[\s\S]*(forme?d?|arrange?d?)\sfrom[\s\S]*(?P<var_n>(\s(\d,?)+\s?)|(\d\-\d))",
                                     r"(how\s*many\s*(ways|permutations|arrangements))\D{1,14}(arrange|line|make)+\s*(of)?\s*(?P<var_tot>[0-9]+)\s*(?P<var_ent>[A-Z|a-z]{3,30})\b\D{0,15}",
                                     r"(?P<var_tot>[0-9]+)\s*(?P<var_ent>[A-Z|a-z]{4,30})\b\D{1,40}(how\s*many\s*(ways|permutations))\D{1,20}(?:choose|pick|arrange|line|select)?\s*(?P<var_r1>[0-9]+)\s*(?P<var_ent1>[A-Z|a-z]+)\D{1,10}(?P<var_r2>[0-9]*)\s*(?P<var_ent2>[A-Z|a-z]*)\D{1,10}(?:chosen|won|arranged|lined)?",
                                     r"from\s*(:?among)?\s*\D{1,12}(?P<var_tot>[0-9]+)\s*(?P<var_ent>[A-Z|a-z]+)\b\D{1,20}(?P<var_r1>[0-9]+)\s*(?P<var_ent1>[A-Z|a-z]+)\D{1,10}(?P<var_r2>[0-9]*)\s*(?P<var_ent2>[A-Z|a-z]*)\D{1,25}\s*(?:chosen|selected|picked|arranged|grouped|appointed)\D{1,6}\s*(how\s*many\s*(ways|permutations|pos?sibilities|arrangements|groups))",
                                     r"(how\s*many\s*(ways|permutations|selections|choices))\D{1,10}(?:choose|male|pick|arrange|line|select|possible|made)?\s*\D{1,10}(?P<var_r1>[0-9]+)\s*(?P<var_ent1>[A-Z|a-z]+)\D{1,10}(?P<var_r2>[0-9]*)\s*(?P<var_ent2>[A-Z|a-z]*)\s*(?:fro?m|out\s*of|from\s*amo?n?g)\D{1,15}(?P<var_tot>[0-9]+)\s*(?P<var_ent>[A-Z|a-z]{3,30})\b"
                                     ] ]


def process_permute(question, nlp):
    stmt = None
    doc = nlp(question)
    result = 0
    for i, regex in enumerate(regexes):
        match = regex.search(doc.text)
        if (match and i == 0):
            s = match.start()
            e = match.end()
            span = doc.char_span(s, e)
            if span is not None:
                for x in range(len(span)):
                    if (x > 0) and ((span[x - 1].text.lower() == 'word') or (span[x - 1].text.lower() == 'wrd')):
                        word_to_perm = span[x].text
                        break
                div = 1
                for i in [word_to_perm.count(x) for x in set(word_to_perm)]:
                    div = div * math.factorial(i)

                result = math.factorial(len(word_to_perm))/div
                stmt = "Number of distinct permutations of the word {0} are {1}".format(word_to_perm, result)
                break

        elif (match and i == 1):
            vars = match.groupdict()
            nvar = ''.join([x for x in vars.get('var_n') if x.isdigit() or x == '-'])
            if (nvar.find("-") > -1 ):
                nvar_val = int(nvar[2]) - int(nvar[0]) + 1
            else:
                nvar_val = len(nvar)
            if vars.get('var_r') is None:
                result = math.factorial(nvar_val)
                stmt = "Permutations of numbers formed from digits {0} are {1}".format(vars.get('var_n'), result)
            else:
                result = math.factorial(nvar_val)/ math.factorial(nvar_val - int(vars.get('var_r')))
                stmt = "Number of {0} digit numbers formed from digits {1} are {2}".format(vars.get('var_r'), vars.get('var_n'), result)
            break

        elif (match and i == 2):
            # In how many ways can I arrange 10 people in a line
            vars = match.groupdict()
            s = match.start()
            e = match.end()
            var_tot = int(vars.get('var_tot'))
            span = doc.char_span(s, e)
            # it is a permutation problem only if entity is a human noun that can be "arranged" and ordered
            permute = False
            for x in range(len(span)):
                # very dirty way of identifing human entity in the subject - find a proper method!
                # also more complex logic for identifying charaters/nouns
                # Train spacy custom model here later to identify NER that are human denoting common nouns
                if (span[x].text == vars.get('var_ent')) and (span[x].pos_ == 'NOUN'):
                    permute = True
            if permute:
                result = math.factorial(var_tot)
                stmt = "Number of permutations of {0} {1} are {2}".format(var_tot, vars.get('var_ent'),  result)
                break

        elif (match and i in (3,4,5)):
            # from among the 36 students in a class, 1 leader and 1 class representative are to be appointed. In how many ways can this be done?
            # 10 participants are participating in a competition. In how many ways can the first 3 prizes be won?
            vars = match.groupdict()
            s = match.start()
            e = match.end()
            var_tot = int(vars.get('var_tot'))
            var_r1 = int(vars.get('var_r1'))
            var_r2 = None
            if (vars.get('var_r2') is not None) and (len(vars.get('var_r2')) > 0) :
                var_r2 = int(vars.get('var_r2'))
            span = doc.char_span(s, e)
            permute = False

            for x in range(len(span)):
                if (span[x].text == vars.get('var_ent')) and (span[x].pos_ == 'NOUN'):
                    permute = True

            if permute:
                if var_r2 is None:
                    result = math.factorial(var_tot)/ math.factorial(var_tot - var_r1)
                    stmt = "Number of permutations of {0} {1} from {2} {3} are {4}".format(var_r1, vars.get('var_ent1'), var_tot, vars.get('var_ent'), result)
                else:
                    result = math.factorial(var_tot)/ math.factorial(var_tot - var_r1) * math.factorial(var_tot - var_r1)/ math.factorial(var_tot - var_r1 - var_r2)
                    stmt = "Number of permutations of {0} {1} and {2} {3} from {4} {5} are {6}".format(vars.get('var_r1'), vars.get('var_ent1'), vars.get('var_r2'), vars.get('var_ent2'), vars.get('var_tot'), vars.get('var_ent'), result)
                break

    return stmt
