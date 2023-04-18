# this piece is directly derived from ElIZA chatbot
# this is a temp and primitive implementation - needs to ve changed to a proper rules chatbot
# for normal chitchat
import re
import random

reflections = {
    "i am": "you are",
    "i was": "you were",
    "i": "you",
    "i'm": "you are",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "you are": "I am",
    "you were": "I was",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you",
}

topic_list_reg = "(trigo?nome?try?|arithmetic|percentages?|permutations?|linear\sequations?|inte?rest|statistics|polynomials?)"

pairs = [
    [
        r"((can\s*y?o?u)?\s*(teach|explain|show)\s*(me)?\s*(how)?[\D]{0,12}(((the)?\ssolution|answer|solved?)|done|do|did)(\D){0,10})|(how\s*did\s*y?o?u\s*(get|do)\s*(the)?\s*(it|answer|solution))",
        "explain",
        "explain",
        ["I am equipped to teach only interest and trigonometry solutions for now...will need to learn others yet!"]
    ],
    [
        r"what(s|'s|\s*is) your name",
        "greet",
        "",
        ["It's not my name but what I do that matters....","Call me Jarvis ...for now."]
    ],
    [
        r"(Solve|i would like to solve|help me with|)\s*" + topic_list_reg,
        "topic",
        "inner",
        ["OK, we will solve %2. Please type the %2 problem.", "Great, please type the %2 question for me to give a shot at."]
    ],
    [
        r"what (type|kind|maths)? (of)? (problems|questions|topics)? (can|do)? you solve|what (can|do) you (do|solve)|what do you (know|solve)|how can you help|what can you help me with",
        "topic",
        "",
        ["I can do $MATH_TOPICS$.... for now.", "I understand $MATH_TOPICS$ at this time. Go ahead and ask me something",
        "$MATH_TOPICS$", "I can solve $MATH_TOPICS$ right now."]
    ],
    [
        r"I would like to solve something|Please help me with a solution|I have a maths problem|Solve something",
        "topic",
        "",
        ["Please tell me what topic you would like help on. I can do $MATH_TOPICS$.... for now.", "Great, what would you like help on? I understand $MATH_TOPICS$ at this time."]
    ],
    [
        r"(Can you)? teach (me)?\s*" + topic_list_reg + "|what else (can you)? (.)*|what other (.)* solve",
        "chitchat",
        "chitchat",
        ["I'm sorry I can only solve a limited set of maths questions for now.", "I only solve maths questions in a small range for now...stay tuned for more","I'm still in my infancy..I only know how to solve maths problems as of now."]
    ],
    [
        r"how are you|what'?s up|wass?sup|how (are)? you doing?",
        "chitchat",
        "chitchat",
        [ "I'm doing good\nHow about You ?" , "All good, how about you" ]
    ],
    [
        r"(Solve|i would like to solve|help me with|can you do|do you know) [a-zA-Z]+",
        "chitchat",
        "",
        ["I'm sorry, I can only do $MATH_TOPICS$ now. Am still learning...please wait..there's a lot more to come! "]
    ],
    [
        r"sorry (.*)",
        "chitchat",
        "chitchat",
        ["Its alright","Its OK, never mind",]
    ],
    [
        r"(wha?t[']?\s*i?s|define|teach|explain)\s*[A-Za-z]{0,5}" + topic_list_reg + "\s*.$",
        "chitchat",
        "chitchat",
        ["I can only solve maths problems for now. please ask the %2 problem not the definition (google's there for that).", "please ask me the %2 problem not a textual definition."]
    ],
    [
        r"(wha?t[']?\s*i?s|define|teach|explain)\s*[A-Z a-z]{0,15}.$",
        "chitchat",
        "chitchat",
        ["I can only solve maths problems for now. please ask a maths problem not the definition", "please ask me a math problem not a textual definition."]
    ],
    [
        r"i('m|\s*am) (.*) doing (.*) (good|ok|fine|great)",
        "chitchat",
        "chitchat",
        ["Nice to hear that","Alright :)","cool"]
    ],
    [
        r"i?('m|\s*am)? (.*) (me)? (bored|angry|irritated|frustrated|sad|upset|depressed)",
        "chitchat",
        "chitchat",
        ["My database does not encompass the dynamics of human behavioral mechanics","Based on your pupil dilation, skin temperature, and motor functions, I calculate an 83 percent probability that you will be just fine. :-)) "]
    ],
    [
        r"hi|hey|hello",
        "greet",
        "",
        ["Hello", "Hey there",]
    ],
    [
        r"(quit|exit|ciao|bye|am\sdone)",
        "quit",
        "",
        ["Bye. See you soon :) ","It was nice talking to you. See you soon :)", "Hope I was of help."]
    ],
    [
        r"(great\s*$|ok\s*$|fine\s*$|good\s*$)",
        "chitchat",
        "",
        ["ok"]
    ],
    [
        r"(you are|that was) (great|amazing|awesome|good|excellent|fantastic)",
        "chitchat",
        "",
        ["Thank you!", "I'm glad you think so"]
    ],
    [
        r"(My name is|I'm|I am) (.*)",
        "greet",
        "",
        ["Hello %2, How are you today ?",]
    ]
]

class RulesChat(object):
    def __init__(self, reflections={}):

        self._pairs = [(re.compile(x.replace(" ","\s*"), re.IGNORECASE),t,c,y) for (x,t,c,y) in pairs]
        self._reflections = reflections
        self._regex = self._compile_reflections()

    def _compile_reflections(self):
        sorted_refl = sorted(self._reflections, key=len, reverse=True)
        return re.compile(
            r"\b({0})\b".format("|".join(map(re.escape, sorted_refl))), re.IGNORECASE
        )

    def _substitute(self, str):

        return self._regex.sub(
            lambda mo: self._reflections[mo.string[mo.start() : mo.end()]], str
        )

    def _wildcards(self, response, match):
        pos = response.find("%")
        while pos >= 0:
            num = int(response[pos + 1 : pos + 2])
            response = (
                response[:pos]
                + self._substitute(match.group(num))
                + response[pos + 2 :]
            )
            pos = response.find("%")
        return response

    def respond(self, str, ctx):

        for (pattern, tag, context, response) in self._pairs:
            match = pattern.match(str)
            if match:
                resp = random.choice(response)
                if len(context) == 0:
                    context = None
                elif context == "inner":
                    pos = resp.find("%")
                    num = int(resp[pos + 1 : pos + 2])
                    # change below to inteligently parse topics and decipher proper tags
                    context = match.group(num).lower().replace(' ','')

                resp = self._wildcards(resp, match)  # process wildcards

                if resp[-2:] == "?.":
                    resp = resp[:-2] + "."
                if resp[-2:] == "??":
                    resp = resp[:-2] + "?"

                return resp, context, tag

        return (None, None, None)
