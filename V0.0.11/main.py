"""
SHEP chatbot V0.0.11

First version to use a neural network to pick answers

Code by D R C Shepherd, aged 20


"""

import json 
import numpy as np
from tensorflow import keras
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from languageProcessor import *
import colorama 
from colorama import Fore, Style, Back

import random
import pickle


def toString(arr): #utility function to convert to string
    #@param arr with array
    s=""
    for i in arr:
        s+=i+" "
    return s[:-1]


class AI:
    def __init__(self,filePath="./",datasets=["conv_questions"],filename='data.json',name='SHEP'):
        """
        initialization
        @param filePath default current path
        @param dataset default questions and answers from hugging face
        @param filename default data.json
        """
        self.lp=LanguageProcessor()
        self.path=filePath
        self.dtst=datasets
        self.data=filename
        self.model=None
        self.built_questions=["what is your name"]
        self.build_responses=[["my name is "+name,name,name+" is my name"]]
        try:
            #attempt to open the dataset if it exists
            model = keras.models.load_model('chat_model')
            self.model=model
        except OSError:
            pass
        self.tokenizer=None
        try: #attempt to open the dataset if it exists
            with open(self.path+'tokenizer.pickle', 'rb') as handle:
                self.tokenizer = pickle.load(handle)
        except OSError:
            pass
        try: #attempt to open the dataset if it exists
            with open(self.path+'label_encoder.pickle', 'rb') as enc:
                self.lbl_encoder = pickle.load(enc)
        except OSError:
            pass
    def addDataSet(self,datasetName):
        """
        @param datasetName taking the name of the dataset to download
        """
        if datasetName not in self.dtst: #check its not in there
            try: #check is valid
                dataset = load_dataset(datasetName) #contains 11,200 conversations
                self.dtst.append(datasetName)
            except:
                raise NameError("This dataset is not found, the dataset has not been added")
            
    def generateData(self,trainQ,trainA):
        """
        Method to generate an intents file for use of training the network
        @param trainQ list of training items
        @param trainA list of corresponding repsonses
        """
        fileData={"intents":[]}
        indexer={}
        for i in range(len(trainA)):
            tag=LP.get_individual_topic(trainQ[i])
            if len(tag)>0:
                name=toString(tag)
                if indexer.get(name,None)!=None: #if exists append
                    fileData["intents"][indexer.get(name)]["patterns"].append(trainQ[i])
                    fileData["intents"][indexer.get(name)]["responses"].append(trainA)
                else: #if not add
                    fileData["intents"].append({"tag":name,"patterns":[trainQ[i]],"responses":[trainA]})
        with open(self.path+self.data, 'w') as f:
            json.dump(fileData, f)
    def train(self,embedding_dim = 16,max_len = 20,vocab_size = 1000,epochs=1000):
        """
        train the network weights and biases
        """
        data=None
        oov_token = "<OOV>"
        try:
            with open(self.path+self.data) as file: #load in training data
                data = json.load(file)
        except:
            raise OSError("No such file")
        training_sentences = []
        training_labels = []
        labels = []
        responses = []
        for intent in data['intents']: #get each phrase
            for pattern in intent['patterns']: #look at patterns of phrase
                training_sentences.append(self.lp.retokenize(pattern.replace("?","").replace(".",""))) #add to training sentences
                training_labels.append(intent['tag']) #add to labels what sort of exchange it is eg greeting
            responses.append(intent['responses'])
        
            if intent['tag'] not in labels: 
                labels.append(intent['tag']) #add unique labels
        
        num_classes = len(labels) #count class numbers
        
        self.lbl_encoder = LabelEncoder() #encode object
        self.lbl_encoder.fit(training_labels) #object use labels
        training_labels = self.lbl_encoder.transform(training_labels)
        self.tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
        self.tokenizer.fit_on_texts(training_sentences)
        word_index = self.tokenizer.word_index
        sequences = self.tokenizer.texts_to_sequences(training_sentences)
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
        history = model.fit(padded_sequences, np.array(training_labels), epochs=epochs)
        # to save the trained model
        model.save(self.path+"chat_model")
        self.model=model
        # to save the fitted tokenizer
        with open(self.path+'tokenizer.pickle', 'wb') as handle:
            pickle.dump(self.tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # to save the fitted label encoder
        with open(self.path+'label_encoder.pickle', 'wb') as ecn_file:
            pickle.dump(self.lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)
    def chat(self,message,max_len = 20):
        """
        @param message of the user message
        @param max_len must be the same as the max_len in the training
        """
        message= self.lp.retokenize(message)
        print(message)
        data=None
        try:
            with open(self.path+self.data) as file: #load in training data
                data = json.load(file)
        except:
            raise OSError("No such file")
        
        if self.tokenizer==None:
            raise SystemError("Train dataset first...")
        max_len = 20
        result = self.model.predict(keras.preprocessing.sequence.pad_sequences(self.tokenizer.texts_to_sequences([message]),
                                             truncating='post', maxlen=max_len)) #predict tag
        tag = self.lbl_encoder.inverse_transform([np.argmax(result)]) #get which tag is predicted
        for i in data['intents']:
            if i['tag'] == tag:
                return np.random.choice(i['responses']) #return a potential answer
        return "I am not sure how to respond to that one"


ai = AI()
#ai.train(epochs=1000)

while True:
    x=input(">")
    print(ai.chat(x))
    
