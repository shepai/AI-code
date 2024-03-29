import json 
import numpy as np 
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder


with open('data.json') as file: #load in training data
    data = json.load(file)
    
training_sentences = []
training_labels = []
labels = []
responses = []


for intent in data['intents']: #get each phrase
    for pattern in intent['patterns']: #look at patterns of phrase
        training_sentences.append(pattern) #add to training sentences
        training_labels.append(intent['tag']) #add to labels what sort of exchange it is eg greeting
    responses.append(intent['responses'])
    
    if intent['tag'] not in labels: 
        labels.append(intent['tag']) #add unique labels
        
num_classes = len(labels) #count class numbers

lbl_encoder = LabelEncoder() #encode object
lbl_encoder.fit(training_labels) #object use labels
training_labels = lbl_encoder.transform(training_labels)


#vectorize tokens of our data
vocab_size = 1000
embedding_dim = 16
max_len = 20
oov_token = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)


model = Sequential() #create model
model.add(Embedding(vocab_size, embedding_dim, input_length=max_len))
model.add(GlobalAveragePooling1D())
model.add(Dense(16, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(num_classes, activation='softmax')) #softmax activation

model.compile(loss='sparse_categorical_crossentropy', 
              optimizer='adam', metrics=['accuracy'])

model.summary()


epochs = 1000
history = model.fit(padded_sequences, np.array(training_labels), epochs=epochs)

# to save the trained model
model.save("chat_model")

import pickle

# to save the fitted tokenizer
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
# to save the fitted label encoder
with open('label_encoder.pickle', 'wb') as ecn_file:
    pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

