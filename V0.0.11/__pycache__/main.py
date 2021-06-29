"""
    SHEP v0.0.10
    Code By Dexter Shepherd, aged 19
    shepai.github.io

    
   
"""
import torch.nn as nn
import torch.nn.functional as F
import torch
import torch.optim as optim
from torchvision import datasets, models, transforms

import numpy as np
import pandas as pd

import nltk
from nltk.data import load
from nltk.tokenize import RegexpTokenizer

class Net(nn.Module):
    #neural network class
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(80, 84)
        self.fc2 = nn.Linear(84, 120)
        self.fc3 = nn.Linear(120, 84)
        self.fc4 = nn.Linear(84, 80)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
    
class AI:
    def __init__(self,path="./"):
        self.SentClassifier=Net()
        self.dataPath=path
        self.dictionary={}
        self.keys={}
        tagdict = load('help/tagsets/upenn_tagset.pickle') #load all possible tags
        keys=list(tagdict.keys())
        for i,tag in enumerate(keys): #sort into dictionary
            self.dictionary[tag]=(i+1) #for input /len(keys)
            self.keys[(i+1)]=tag #for output
    def getID(self,words): #convert a batch of words into a batch of token ids
        Words=[]
        for sent in words:
            if type(sent)!=type([]): sent = nltk.word_tokenize(sent) #tokenize sentence
            tagged = nltk.pos_tag(sent) #get tags
            s=[]
            for word,tok in tagged: #loop through tokens
                s.append(self.dictionary[tok]) #get token id
            Words.append(s)
        return Words
    def removePunc(self,words): #remove punctuation of batch of words
        w=[]
        for inp in words: #loop through each sentence
            if type(inp)!=type(""):
                inp=inp[0]
            tokenizer = RegexpTokenizer(r'\w+')
            w.append(tokenizer.tokenize(inp)) #remove and tokenize
        return w
    def train_batch(self,inputs,responses,epochNum=200): #train the model on
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.SentClassifier.parameters(), lr=0.0001)
        loss_fn = torch.nn.MSELoss(reduction='sum')
        inputs=self.removePunc(inputs) #remove punctuation
        responses=self.removePunc(responses) #remove punctuation
        X = self.getID(inputs) #get ID array
        x=[]
        for item in X: #replace blanks
            z=item.copy()
            if len(item)<80:
                for j in range(len(item),80):
                    z.append(0)
            elif len(item)>80: #raise error if dataset has sentence of more than 80 words
                raise ValueError("error of sentence sizing in question set at "+item)
            x.append(z)
        X=x
        y = self.getID(responses) #get ID array
        Y=[]
        for item in y: #replace blanks
            z=item.copy()
            if len(item)<80:
                for j in range(len(item),80):
                    z.append(0)
            elif len(item)>80: #raise error if dataset has sentence of more than 80 words
                raise ValueError("error of sentence sizing in answer set at "+item)
            Y.append(z)
        y=Y
        X=np.array(X)#/len(self.dictionary) #convert to numpy
        y=np.array(y) #convert to numpy
        X=torch.tensor(X).float()
        y=torch.tensor(y).float()
        for step in range(epochNum): #train
            y_pred = self.SentClassifier(X)
            #clear all the gradients before calculating them
            loss = loss_fn(y_pred, y)
            if step % 100 == 99:
                print(step, loss.item())
            optimizer.zero_grad()
            loss.backward()

            optimizer.step()
        
    def predict_tags(self,question): #predict tags related to question
        q=[question]
        inputs=self.removePunc(q) #remove punctuation
        X = self.getID(inputs) #get ID array
        x=[]
        for item in X: #replace blanks
            z=item.copy()
            if len(item)<80:
                for j in range(len(item),80):
                    z.append(0)
            elif len(item)>80: #raise error if dataset has sentence of more than 80 words
                raise ValueError("error of sentence sizing in question set at "+item)
            x.append(z)
        X=x
        X=np.array(X)#/len(self.dictionary) #convert to numpy
        X=torch.tensor(X).float()
        predictions=self.SentClassifier.forward(X)
        print(predictions)

ai=AI()

from datasets import load_dataset
dataset = load_dataset("web_questions")

train=dataset['train']
test=dataset['test']


X=train['question']
y=train['answers']

ai.train_batch(X,y)

#input("Enter to end")

while True:
    x=input("Question:")
    ai.predict_tags(x)
    
