import os
import json
import spacy
import random
import pickle
import numpy as np
import pandas as pd
import sys, traceback
from logic import stats
from logic import interest
from logic import lineareq
from logic import arithmetic
from logic import trigonom
from logic import polynomial
from tensorflow import keras
from tools import redis_adapter
from tools.RulesChat import RulesChat
from nltk.chat.util import reflections
from logic.percent import process_percent
from logic.permute import process_permute
from logic.combine import process_combine
from tools.response_utils import process_explain
from tools.preprocess import sanitize_text, spell_check
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CHECK FOR THREAD SAFETTY of this entire code as well as called code!
# specifcically Spacy nlp etc that is passed to every component
context = {} # change to distributed redis later
training_sentences = []
training_labels = []
labels = {}
responses = {}
model = None
tokenizer = None
nlp = None
tag_to_intent = {}
Chat = RulesChat(reflections)
doc_explain=None
FILE_PATH = os.path.dirname(os.path.realpath(__file__))

with open(FILE_PATH + '/../data/intents.json') as f:
    data = json.load(f)
df = pd.DataFrame(data)

for intent in df['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses[intent['tag']] = intent['responses']
    tag_to_intent[intent['tag']] = intent


def load_model():
    # load trained model
    global nlp
    global labels
    global model
    global tokenizer
    global doc_explain
    model = keras.models.load_model(FILE_PATH + '/../../models/chat_model')
    with open(FILE_PATH + '/../../models/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    with open(FILE_PATH + '/../../models/label_encoder.pickle', 'rb') as enc:
        lbl_tokenizer = pickle.load(enc)
    for (k,v) in lbl_tokenizer.word_index.items():
        labels[v] = k
    nlp = spacy.load('en_core_web_sm')


def process_tag(tag, input_text, chat_id):
    response = None
    try:
        if (tag in 'percentages'):
            response = process_percent(input_text, nlp)
        elif (tag in 'permutations'):
            response = process_permute(input_text, nlp)
            if response is None:
                response = process_combine(input_text, nlp)
        elif (tag in 'combinations'):
            response = process_combine(input_text, nlp)
        elif (tag == 'arithmetic'):
            response = arithmetic.process_arith(input_text, nlp)
        elif (tag == 'interest'):
            response = interest.process_interest(input_text, nlp)
        elif (tag == 'statistics'):
            response = stats.process_statistics(input_text, nlp)
        elif (tag == 'trigonometry'):
            response = trigonom.process_trigonom(input_text, nlp)
        elif (tag in 'linearequations'):
            response = lineareq.process_lineareq(input_text)
            if response is None:
                response = polynomial.process_polynomial(input_text)
        elif (tag in 'polynomials'):
            response = polynomial.process_polynomial(input_text)
            if response is None:
                response = lineareq.process_lineareq(input_text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_tb(exc_tb, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_tb,limit=2, file=sys.stdout)
        traceback.print_exc(limit=2, file=sys.stdout)
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        response = None
    finally:
        return response


def predict_response(chat_id, unspelt_chat_stmt, test_mode=False):
    max_len = 200
    # call a general model/rules chat here to separate maths content from all other chit chat etc
    # Most common case - context is set to a maths topic then we avoid rules and model prediction and go str8 to Spacy
    chat_statement = spell_check(unspelt_chat_stmt)
    if (chat_id in context):
        tag_resp = process_tag(context[chat_id], chat_statement, chat_id)
        if tag_resp is not None:
            return tag_resp

    # Usual case -is context is not set let either first process rules-textual input
    # as a rule am processing rules first always if context is not set - avoid/opttimize this?
    (res, cont, tg) = (None, None , None)
    if (not chat_id in context):
        (res, cont, tg) = Chat.respond(chat_statement, None)
    else:
        (res, cont, tg) = Chat.respond(chat_statement, context[chat_id])
    if cont is not None:
        context[chat_id] = cont

    if res is not None:
        return res

    tag = None
    # if we reach here without a response we need model.predict anyway!
    model_resp = None
    # classify text using trained models

    result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences(sanitize_text([chat_statement])),
                                         truncating='post', maxlen=max_len))
    tag = labels[np.argmax(result)]
    intent = tag_to_intent[tag]
    if 'context_set' in intent:
        context[chat_id] = intent['context_set']

    print("category of your query is....!!!! |-", tag,"-|", len(tag))

    model_resp = process_tag(tag, chat_statement, chat_id)
    if model_resp is None:
        model_resp = '$INCOHERENT$' + (tag or '')  #'Could not understand your query, please rephrase'
    print('Jarvis: ', model_resp)
    if test_mode: # used only for testing model accuracy after build
        return (model_resp, tag)
    else:
        return model_resp

load_model()
