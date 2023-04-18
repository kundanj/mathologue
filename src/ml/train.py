import os
import sys
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import layers
from tensorflow import keras
from keras.models import Sequential
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from sklearn.preprocessing import LabelEncoder
from keras.preprocessing.text import Tokenizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.feature_extraction.text import CountVectorizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.preprocess import sanitize_text

training_sentences = []
training_labels = []
labels = []
responses = []
FILE_PATH = os.path.dirname(os.path.realpath(__file__))


with open(FILE_PATH + '/../data/intents.json') as f:
    data = json.load(f)
df = pd.DataFrame(data)

for intent in df['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses.append(intent['responses'])

    if intent['tag'] not in labels:
        labels.append(intent['tag'])

num_classes = len(labels)

sentences_train, sentences_test, y_train, y_test = train_test_split(
        sanitize_text(training_sentences), training_labels, test_size=0.15, random_state=1000)

vocab_size = 2000
oov_token = "<OOV>"
maxlen = 200
tokenizer = Tokenizer(num_words=10000, filters='"#():;?@[\\]_`|~\'\t\n')
tokenizer.fit_on_texts(sentences_train)
X_train = tokenizer.texts_to_sequences(sentences_train)
X_test = tokenizer.texts_to_sequences(sentences_test)
vocab_size = len(tokenizer.word_index) + 1

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

label_tokenizer = Tokenizer()
label_tokenizer.fit_on_texts(training_labels)

training_label_seq = np.array(label_tokenizer.texts_to_sequences(y_train))
validation_label_seq = np.array(label_tokenizer.texts_to_sequences(y_test))

print("label_tokenize-----------------------",label_tokenizer.word_index)
print("numclasses-----------------------",num_classes)
print("word embeddings-----------------------",vocab_size)

# finally make the model...sequential suits NLP use cases
embedding_dim = 50
model = Sequential()
model.add(layers.Embedding(input_dim=vocab_size,
                           output_dim=embedding_dim,
                           input_length=maxlen))
model.add(layers.GlobalMaxPool1D())
model.add(layers.Dense(50, activation='relu'))
model.add(layers.Dense(num_classes + 1, activation='softmax'))
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',metrics=['accuracy'])

history = model.fit(X_train, training_label_seq, epochs=50, validation_data=(X_test, validation_label_seq), verbose=True)
loss, accuracy = model.evaluate(X_train, training_label_seq, verbose=False)
print("Training Accuracy: {:.4f}".format(accuracy))

loss, accuracy = model.evaluate(X_test,validation_label_seq , verbose=False)
print("Testing Accuracy:  {:.4f}".format(accuracy))

# save the model for use by chatbot!
model.save(FILE_PATH + "/../../models/chat_model")
import pickle
with open(FILE_PATH +'/../../models/tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(FILE_PATH + '/../../models/label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(label_tokenizer, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)
