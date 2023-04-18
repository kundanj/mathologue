import re
import string
from spellchecker import SpellChecker
stop_words = ['what','is','does','tell','give'] # add your own here
spell = SpellChecker()


def sanitize_text(docs):
    documents = []
    for sentence in docs:
        # IMPORTANT step - replace alll numbers in text by a single stndard numer! This is beoz the model trains ONLY on specific numbers
        # that are in the training set. This is a bug when training for equations
        sentence = re.sub(r'\d+', '99', sentence)
        sent_tok = sentence.lower().split()
        document = [word for word in sent_tok if word not in set(stop_words)]
        documents.append(' '.join(document))
    return documents


def spell_check(sentence):
    corrected_spells = []
    for word in sentence.split():
        if word.isalpha():
            tmp = spell.correction(word)
            if tmp is not None :
                corrected_spells.append(tmp)
            else:
                corrected_spells.append(word)
        else:
            corrected_spells.append(word)
    return ' '.join(corrected_spells)
