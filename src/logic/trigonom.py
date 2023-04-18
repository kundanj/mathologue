import spacy
from math import sqrt, sin, cos, tan, radians, asin, atan, degrees
from spacy.symbols import nsubj, dobj, pobj, prep, nn, conj, NOUN, VERB


def get_left(token):
    left_arr = [left for index, left in enumerate(token.lefts) if index == (token.n_lefts - 1)]
    if len(left_arr):
        return left_arr[0]
    else:
        return None


def get_right(token):
    right_arr = [right for index, right in enumerate(token.rights) if index == 0]
    if len(right_arr):
        return right_arr[0]
    else:
        return None


def prep_trigonom(question, nlp):
    stmt = None
    populated_vars={}
    known_vars=[]
    doc = nlp(question)
    mainobject=None
    objecttype=set()
    unknown_index=-1

    for index, token in enumerate(doc):
        # BUG here in spacy model if 'the' is not used before dobjs then it is not classified as NOUN!!! e,g "angle opposite it is..." should be "the angle opposte is"
        left = get_left(token.head)
        left = left.pos_ if left is not None else ''
        if (unknown_index == -1) and token.pos == NOUN and (token.head.pos_ == 'VERB' or (token.head.pos_ == 'AUX' and left in ('PRON','ADJ','AUX'))):
            if not any(t for t in ('area','hypotenuse','side','base','height','angles') if token.text in t):
                right = get_right(token)
                right =  get_right(right) if right is not None else None
                idx=right.i
                right = right.text if right is not None else ' '
                if any(t for t in ('area','hypotenuse','side','base','height','angles') if right in t):
                    populated_vars[right] = "-?"
                    unknown_index=idx
                    known_vars.append(right)
                    continue
            else:
                populated_vars[token.text] = "-?"
                unknown_index=index
                known_vars.append(token.text)
                continue

        if (token.pos == NOUN) and (index != unknown_index):
            if token.dep in (dobj, nsubj, pobj, conj)  or token.tag_ in ('NN','NNS'): # rare case where conj is dependency parse for "height"
                if any(t for t in ('area','hypotenuse','side','base','height','angles') if token.text in t):  # normal case
                    # to take care of "angle adjaent to that side" case where side and angle are vars
                    # for cases like "angle opposie to that side is 60"....in which case 2nd side sould be ignored
                    if (len(known_vars) > 0) and (populated_vars[known_vars[len(known_vars) - 1]] != "-?") and (populated_vars[known_vars[len(known_vars) - 1]] == "-1") and (known_vars[len(known_vars) - 1] in [ancestor.text for ancestor in token.ancestors][:3]) and token.head.dep_ == 'prep':
                        # skip this variable as it is already pupulated
                        pass
                    else:
                        if token.text in populated_vars:
                            varname = token.text + str(len([x for x in known_vars if token.text in x]))
                        else:
                            varname = token.text
                        populated_vars[varname] = "-1"
                        known_vars.append(varname)
                elif token.dep == pobj and token.text == "triangle": # to check if main geometry is always pobj
                    mainobject = 't' # triangle
        elif token.dep_ == "nummod" or token.tag_ == "CD":
            if index == (len(doc) - 1) or (not any(t for t in ('area','hypotenuse','side','base','height','angles') if doc[index + 1].text in t) and doc[index + 1].dep != prep) :
                if token.head in populated_vars:
                    populated_vars[token.head] = token.text
                else: # take token.head.lefts here  iterate thru and find variable name? not reliable tho
                    populated_vars[known_vars[len(known_vars) - 1]]=token.text
        elif token.dep_ in ("advmod","amod","compound") or token.tag_ == "JJ": # maybe this should be and instead of or
            if token.head.text in 'angles':
                populated_vars['angle_attrib'] = token.text
            else:
                objecttype.add(token.text)

    objecttype = [x for x in objecttype if x in ['right','isosceles','equilateral']]
    populated_vars['t_type'] = '' if len(objecttype) == 0 else objecttype[0]
    populated_vars['geom_object'] = mainobject
    # At the end of this if any populated_vars has = -1 change it to -? as this will be the variable
    #if token.head.dep_ == "ROOT": this does not work as head of many guys is root
    return populated_vars


def calc_trigonom(populated_vars):
    populated_vars.pop('geom_object')
    t_type = populated_vars.pop('t_type')
    sol = angle = side = side2 = side1 = hypotenuse = base = height = answer = area = None
    if 'angle' in populated_vars and populated_vars['angle'] != '-?':
        angle = float(populated_vars['angle'])
    if 'side' in populated_vars and populated_vars['side'] != '-?':
        side = float(populated_vars['side'])
    if 'side2' in populated_vars and populated_vars['side2'] != '-?':
        side2 = float(populated_vars['side2'])
    if 'side1' in populated_vars and populated_vars['side1'] != '-?':
        side1 = float(populated_vars['side1'])
    if 'hypotenuse' in populated_vars and populated_vars['hypotenuse'] != '-?':
        hypotenuse = float(populated_vars['hypotenuse'])
    if 'base' in populated_vars and populated_vars['base'] != '-?':
        base = float(populated_vars['base'])
    if 'height' in populated_vars and populated_vars['height'] != '-?':
        height = float(populated_vars['height'])
    if 'area' in populated_vars and populated_vars['area'] != '-?':
        area = float(populated_vars['area'])
    variable = [t for t in populated_vars.keys() if populated_vars[t] == '-?']
    # add code heere to replace vars with root varoable name in caes where side = 20 and side1= -1
    # calc base and height here itself only ONCE!
    if base is not None and area is not None:
        height = 2 * area/ base
        answer = " with base " + str(base) + " and area " + str(area)
    elif height is not None and area is not None:
        base = 2 * area/ height
        answer = " with height " + str(height) + " and area " + str(area)
    elif height is not None and base is not None:
        area = 0.5 * base * height
        answer = " with height " + str(height) + " and base " + str(base)

    ques_code = ''
    vars = {}

    if 'right' in t_type:
        if angle is not None and 'angle_attrib' not in populated_vars:
            populated_vars['angle_attrib'] = 'opposite'
        # right angles triangle
        # all cases below work for sides opposite angles specified
        # make provisions for adjacent angles
        if 'side' in variable:
            if side1 is not None and side2 is None:
                side2 = side1
            if hypotenuse is not None and angle is not None:
                if populated_vars['angle_attrib'] == 'opposite':
                    if angle == 30:
                        sol = hypotenuse/2
                    elif angle == 60:
                        sol = sqrt(3) * hypotenuse/2
                    else:
                        sol = sin(radians(angle)) * hypotenuse
                elif populated_vars['angle_attrib'] == 'adjacent':
                    if angle == 30:
                        sol = sqrt(3) * hypotenuse/2
                    elif angle == 60:
                        sol = hypotenuse/2
                    else:
                        sol = cos(radians(angle)) * hypotenuse
                elif angle == 45:
                    sol = sqrt(3) * hypotenuse/sqrt(2)
                answer = "hypotenuse " + str(hypotenuse) + " and " + populated_vars['angle_attrib'] + " angle " + str(angle)
            elif side2 is not None and angle is not None:
                if populated_vars['angle_attrib'] == 'opposite':
                    if angle == 30:
                        sol = side2 * sqrt(3)
                    elif angle == 60:
                        sol = side2 / sqrt(3)
                    else:
                        sol = side2 / tan(radians(angle))
                elif populated_vars['angle_attrib'] == 'adjacent':
                    if angle == 30:
                        sol = side2 / sqrt(3)
                    elif angle == 60:
                        sol = side2 * sqrt(3)
                    else:
                        sol = side2 * tan(radians(angle))
                elif angle == 45:
                    sol = side2
                answer = "one side " + str(side2) + " and " + populated_vars['angle_attrib'] + " angle " + str(angle)
            elif hypotenuse is not None and (side is not None or side2 is not None):
                sol = sqrt(hypotenuse**2 - side**2) if side is not None else sqrt(hypotenuse**2 - side2**2)
                answer = " and one side " + str(side if side is not None else side2)
            else:
                err="hypotenusemissing"
            if sol is not None:
                answer = "side of right triangle with "  + answer + " is " + str(sol)
                ques_code = 'trig-side1'
                vars = {"angle_attrib": populated_vars['angle_attrib'], "hypotenuse": hypotenuse, "side": side, "side2": side2, "angle": angle}
            else:
                answer = err
        elif 'hypotenuse' in variable:
            if side is not None and angle is not None:
                if populated_vars['angle_attrib'] == 'opposite':
                    if angle == 30:
                        sol = side * 2
                    elif angle == 60:
                        sol = 2 * side / sqrt(3)
                    else:
                        sol = side / sin(radians(angle))
                elif populated_vars['angle_attrib'] == 'adjacent':
                    if angle == 30:
                        sol = 2 * side / sqrt(3)
                    elif angle == 60:
                        sol = side * 2
                    else:
                        sol = side / cos(radians(angle))
                elif angle == 45:
                    sol = sqrt(2) * side
                else:
                    err = "anglenot369"
                answer = " side " + str(side) + " and " + populated_vars['angle_attrib'] + " angle " + str(angle)
            elif side is not None and side2 is not None:
                sol = sqrt(side**2 + side**2)
                answer = " and sides " + str(side) + " " + str(side2)
            else:
                err="sidemissing"
            if sol is not None:
                answer = "hypotenuse of right triangle with " +  answer + " is " + str(sol)
                ques_code = 'trig-hyp1'
                vars = {"angle_attrib": populated_vars['angle_attrib'],  "side": side, "side2": side2, "angle": angle}
            else:
                answer = err
        elif 'angle' in variable:
            if side1 is not None and side2 is None:
                side2 = side1
            if hypotenuse is not None and side is not None:
                sol1 = degrees(asin(side/hypotenuse))
                sol2 = 90 - sol1
                answer = " side " + str(side) + " and hypotenuse " +   str(hypotenuse)
            elif side is not None and side2 is not None:
                sol1 = degrees(atan(side/side2))
                sol2 = 90 - sol1
                answer = " one side " + str(side) + " and another side " +   str(side2)
            if sol1 is not None:
                answer = "angles of right triangle with " +  answer + " are " + str(sol1) + "  and " + str(sol2)
                ques_code = 'trig-ang1'
                vars = {"angle_attrib": populated_vars['angle_attrib'], "hypotenuse": hypotenuse, "side": side, "side2": side2}
            else:
                answer = err
        if len(ques_code) > 0:
            subcontext = { "ques_code" : ques_code, "vars": vars }
            context_obj = {}
            context_obj['context'] = "trigonometry"
            context_obj['subcontext'] = subcontext
        return answer
    elif 'isosceles' in t_type:
        if base is not None and angle is not None:
            if angle == 30:
                side = 2 * (base/2) / sqrt(3)
                height = (base/2) / sqrt(3)
            elif angle == 60:
                side = 2 * (base/2) # / sqrt(3)
                height = (base/2) * sqrt(3)
            elif angle == 45:
                side = (base/2) * sqrt(2)
                height = (base/2)
            else:
                err = "anglenot369"
            answer = " with base " + str(base) + " and angle " + str(angle)
        if height is not None and angle is not None:
            if angle == 30:
                side = 2 * height
                base = 2 * height * sqrt(3)
            elif angle == 60:
                side = 2 * height / sqrt(3) # / sqrt(3)
                base = 2 * height / sqrt(3)
            elif angle == 45:
                side = (height) * sqrt(2)
                base = height
            else:
                err = "anglenot369"
            answer = " with height " + str(height) + " and angle " + str(angle)
        elif base is not None and height is not None:
            side = sqrt((base/2)**2 + height**2)
            answer = " with base " + str(base) + " and height " + str(height)
        else:
            err="isoscelesmissing"
        if 'side' in variable:
            answer = "side of Isosceles triangle " + answer + " is " + str(side)
        elif 'base' in variable:
            answer = "base of Isosceles triangle " + answer + " is " + str(base)
        elif 'height' in variable:
            answer = "height of Isosceles triangle " + answer + " is " + str(height)
        elif 'area' in variable:
            answer = "area of Isosceles triangle " + answer + " is " + str(0.5 * base * height)
        else:
            answer = err
        return answer

    elif 'equilateral' in t_type:
        if side is not None:
            height = (side/2) * sqrt(3)
            answer = " with side " + str(side)
        elif base is not None:
            height = (base/2) * sqrt(3)
            answer = " with base " + str(base)
        elif height is not None:
            side = 2 * height / sqrt(3)
            answer = " with height " + str(height)
        elif area is not None:
            side = sqrt(4 * area/ sqrt(3))
            answer = " with area " + str(area)
        else:
            err="equilateralmissing"
        if 'side' in variable:
            answer = "side of equilateral triangle " + answer + " is " + str(side)
        elif 'base' in variable:
            answer = "base of equilateral triangle " + answer + " is " + str(side)
        elif 'height' in variable:
            answer = "height of equilateral triangle " + answer + " is " + str(height)
        elif 'area' in variable:
            answer = "area of equilateral triangle " + answer + " is " + str(0.5 * side * height)
        else:
            answer = err
        return answer

    else:
        if 'side' in variable and base is not None:
            answer = "side of triangle " + answer + " is " + str(base)
        elif 'base' in variable and base is not None:
            answer = "base of triangle " + answer + " is " + str(base)
        elif 'height' in variable and height is not None:
            answer = "height of triangle " + answer + " is " + str(height)
        elif 'area' in variable and area is not None:
            answer = "area of triangle " + answer + " is " + str(area)
        else:
            answer = 'insufficienttriangle'
        return answer


def process_trigonom(question, nlp):
    populated_vars = prep_trigonom(question, nlp)
    return calc_trigonom(populated_vars)

'''
for ques in ["find area of triangle with base 10 and height 12"," what is the area of an equilateral triangle with length of side 20","find the side of a right triangle if length of one side is 20 and measure of the opposite angle is 30",
"find the hypotenuse of a right angled triangle with side 10 cms and one of its angle is 30 degrees",
"if area of an isosceles triangle is 300 what is length of its side if the base is 20",
"whats side of a right triangle if the length of other side is 55 feet and measure of an angle opposite that is 67.3 degrees",
"whats hypotenuse of a right triangle if the length of one side is 3 and measure of the angle adjacent to that side is 30",
"whats side of a right angled triangle if the length of one side is 3 and measure of the angle opposite the side is 30",
"whats angle of a right triangle if the length of one side is 23 feet and measure of the other side  is 55 ft"]:
    print(ques +' :\n ans: ', process_trigonom(ques, nlp))
'''
