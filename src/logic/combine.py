import re
import math
import spacy

regexes = [ re.compile(p, re.IGNORECASE) for p in [
                                    "(from\s*a?\s*group\s*of)?\D*(?P<var_tot1>[0-9]+)\s*(?P<var_ent1>[A-Z|a-z]{3,30})\s*(and)?\s*(?P<var_tot2>[0-9]*)\s*(?P<var_ent2>[A-Z|a-z]{4,30})?\s*\D*(t?o?\s*choose|choices|form|how\s*many)\D*(committees?|groups?|collections?)?\s*(of)?\s*(?P<var_r1>[0-9]+)\s*(?P<var_r_ent1>[A-Z|a-z]+)\s*(and)?\s*(?P<var_r2>[0-9]*)\s*(?P<var_r_ent2>[A-Z|a-z]*)",
                                    "(how\s*many\s*(groups|collections|com?mitt?ees|selections|ways|choices)\s*o?f?)\D{1,15}(?P<var_r1>[0-9]+)\s*(?P<var_r_ent1>[A-Z|a-z]{3,30})\s*(and)?\s*(?P<var_r2>[0-9]*)\s*(?P<var_r_ent2>[A-Z|a-z]{4,30})?\s*((can)?\s*(be|I|you|one|we)\s*(choose|chosen|selecte?d?|groupe?d?|forme?d?|done|made))?\s*(from|out\s*of)\s*\D*(?P<var_tot1>[0-9]+)\s*(?P<var_ent1>[A-Z|a-z]+)\s*(and)?\s*(?P<var_tot2>[0-9]*)\s*(?P<var_ent2>[A-Z|a-z]*)"
                                     ] ]

# temp fix - not required for combination? this has to be determied by a trained Spacy program to find human entities that are handled by permutation
# below list is a crude/ridiculous way  of identifying human entities - train custom Spacy model
lemma_list = ['participant','student','worker','people','person','man','woman','runner','sportsman','boy','girl','candidate','guy','gal', 'player']

def process_combine(question, nlp):
    stmt = None
    doc = nlp(question)
    result = 0
    for i, regex in enumerate(regexes):
        match = regex.search(doc.text)
        if (match and i in (0,1)):
            # from group of 6 men  4 women how can you choose a group of 5 guys. How many committees are possible
            # from a group of 6 men and 4 women how can you form a committee of 3 men and 2 women
            # from group of 7 men  4 women how many groups of 5 guys
            # if we have a group of 6 men  and 4 women how many ways can you form a committee of 5 people
            vars = match.groupdict()
            s = match.start()
            e = match.end()
            var_tot1 = int(vars.get('var_tot1'))
            var_r = int(vars.get('var_r1'))
            var_tot2 = None
            var_r2 = None
            if (vars.get('var_tot2') is not None) and (len(vars.get('var_tot2')) > 0):
                var_tot2 = int(vars.get('var_tot2'))
            if (vars.get('var_r2') is not None) and (len(vars.get('var_r2')) > 0):
                var_r2 = int(vars.get('var_r2'))
            span = doc.char_span(s, e)
            # Just doing combinations based on regex! not analyzing NER of ent values now.
            # bad form: we should identfy common nouns objects like toys etc that are similar in character? just assuming human entity now without checking
            # we are doing a crude entity match to make sure it is combination and not permute! e.g how many ways can I select 2 prizes from 10 students???!!!!
            combine = True
            for x in range(len(span)):
                # very dirty way of identifing human denoting noun in the subject - find a proper method!
                # also more complex logic for identifying charaters/nouns
                # Train spacy model here to identify entities that are human denoting common nouns
                if (span[x].text in (vars.get('var_ent1'), vars.get('var_ent2'), vars.get('var_r_ent1'), vars.get('var_r_ent1')) ):
                    if (span[x].lemma_ not in lemma_list):
                        combine = False
            if not combine:
                break

            var_tot = var_tot1
            from_str = str(var_tot) + " " + vars.get('var_ent1')
            if var_tot2 is not None:
                var_tot = var_tot1 + var_tot2
                from_str = str(var_tot1) + " " + vars.get('var_ent1') + " " + str(var_tot2) + " " +  vars.get('var_ent2')

            if var_r2 is None:
                result = math.factorial(var_tot)/ (math.factorial(var_r) * math.factorial(var_tot - var_r))
                stmt = "Number of combinations of {0} {1} from {2} are {3}".format(var_r, vars.get('var_r_ent1'),from_str, result)
            else:
                if vars.get('var_r_ent1') == vars.get('var_ent2'):
                    tmp = var_r
                    var_r = var_r2
                    var_r2 = tmp
                result = (math.factorial(var_tot1)/ (math.factorial(var_r) * math.factorial(var_tot1 - var_r))) * (math.factorial(var_tot2)/ (math.factorial(var_r2) * math.factorial(var_tot2 - var_r2)))
                stmt = "Number of combinations of {0} {1} and {2} {3} from {4} are {5}".format(var_r, vars.get('var_r_ent1'),var_r2, vars.get('var_r_ent2'),from_str, result)
            break

    return stmt
