from datasets import load_dataset
from languageProcessor import *

dataset = load_dataset("conv_questions") #contains 11,200 conversations

LP=LanguageProcessor()

questions=dataset['train']['questions']

answers=dataset['train']['answer_texts']

dictionary={}

questionsR=[]
answersR=[]
for i,q in enumerate(questions[0:200]):
    for tmp in range(len(q)): #linearlize the array
        questionsR.append(q[tmp])
        answersR.append(answers[i][tmp])
        
fileData={"intents":[]}
indexer={}

def toString(arr):
    s=""
    for i in arr:
        s+=i+" "
    return s[:-1]
for i in range(len(answersR)):
    
    tag=LP.get_individual_topic(questionsR[i])
    if len(tag)>0:
        name=toString(tag)
        if indexer.get(name,None)!=None: #if exists append
            fileData["intents"][indexer.get(name)]["patterns"].append(questionsR[i])
            fileData["intents"][indexer.get(name)]["responses"].append(answersR[i])
        else: #if not add
            fileData["intents"].append({"tag":name,"patterns":[questionsR[i]],"responses":[answersR[i]]})

import json
with open('./data.json', 'w') as f:
    json.dump(fileData, f)

