"""
    SHEP v0.0.10
    Code By Dexter Shepherd, aged 19
    shepai.github.io

    Building on v0.0.9, this version learns by repetition. It looks at how the user responds to a message, and will learn to respond with
    the same or similar messages. This also prevents the machine learning irrelevent messages entered in.
    The code is to provide a smarter self learning chatbot which appears to learn naturaly and efficiently. 
    This code is a re-write of the origional V0.0.10, which was improved upon for speed and information
    efficiency.
    The code is split down into different classes. It also uses the language processor library I wrote.
    
    Short term
        This class stores the current log file of the coversation, the last 10 items of conversation, and the strength of different responses
        to messages. The strength is based on how often it is responded in this way.
    Log
        This provides an interface to the json files holding a log of all the conversations
    InformationLog
        Thils holds a log of all information relating to this topic
    AI
        This is the main class which binds all classes together. On initialization it creates a log, a short term memory and long term, as well as calls in the language
        analyser. 
"""

from languageProcessor import LanguageProcessor as LP
LP=LP() #form on initialization
SYSTEM_PATHWAY=""
import json
import random
import os
import time
import difflib
from datetime import datetime, timedelta

class Log:
    #store the log file information of the current conversation
    def __init__(self,name=""):
        #create unique name
        self.convo={}
        if not os.path.isdir("logFiles"):
            os.mkdir("logFiles") #set aside area for logFiles
        if name!="": #allow user to set name
            self.name=name
            try:
                file=open(SYSTEM_PATHWAY+self.name) #read file
                r=file.read()
                file.close()
                self.convo = json.loads(r) #convert to dictionary
            except: #if file deleted
                self.convo={}
        else:
            num=len([name for name in os.listdir("logFiles/")])+1
            self.name="logFiles/"+str(num)+".json"
    def getName(self):
        return self.name
    def save(self):
        with open(SYSTEM_PATHWAY+self.name, 'w', encoding='utf-8') as f:
            json.dump(self.convo, f)
    def add(self,items):
        key=len(self.convo)
        self.convo[str(key)]=items #add item to the conversation
        self.save() #save
        return key #return the key it is added at
    def getLastItem(self):
        #return the last item in the conversation
        if len(self.convo)-1>0:
            return self.convo[str(len(self.convo)-1)]
        else:
            return None
    def findTopics(self,num):
        start=num-10#find item at line
        if start<0: start=0
        text=""
        for i in range(num):
            text+=self.convo[str(i)]['text']+". "
        return LP.get_frequent_topics(text) #return topics of conversation
class shortTerm:
    #short term memory simply binds the log files and current conversation
    #into one class
    def  __init__(self,size=10): #give size as 10
        self.convo=[] #store the current conversation
        self.current=Log() #initialize log file
        self.size=size
    def add(self,item):
        self.current.add(item) #add to log
        self.current.save() #save log
        self.convo.append(item['text'])
        if len(self.convo)>self.size: #do not let it sopass memory size
            self.convo.remove(self.convo[0]) #remove first item
    def commitLog(self):
        #self.current.save() #save log file
        self.current=Log() #create new log file
        self.convo=[]
    def getLastItem(self):
        return self.convo[-1]
    def getText(self):
        text=""
        for i in self.convo:
            text+=i+". "
        if len(text)>2: return text[:-2]
        else: return ""
class informationLog:
    #Information logs contain all the messages and responses saved based under the topic (subject of conversation)
    #It is organized to save the reliability of each answer and only return reliable answers which have been strengthened
    #Log files relating to each are saved so answers which are different can be checked to find topic dependent info
    def __init__(self,name,freq_topics,log):
        #if name exists open
        #otherwise create
        self.FT=freq_topics #set the current topics
        self.log=log
        if not os.path.isdir("infoFiles"):
            os.mkdir("infoFiles") #set aside area for logFiles
        self.name=name+".json"
        #open file
        try:
                file=open(SYSTEM_PATHWAY+"infoFiles/"+self.name) #read file
                r=file.read()
                file.close()
                self.data = json.loads(r) #convert to dictionary
        except: #if file not existant
                self.data={}
    def add(self,message,items):
        #add to the data
        date=datetime.today().strftime("%d/%m/%Y") #gather the date
        if self.data.get(message,False):
            responses=list(self.data[message].keys())
            for candidate in items: #loop through data items
                    ###############Future make it so it increases response if very similar
                    if type(candidate)==type([]): candidate=candidate[0] #only add strings
                    if candidate in responses: #if found
                        if self.data[message][candidate]['times']<4: #stop adding after time
                            self.data[message][candidate]['times']+=1 #increase
                            self.data[message][candidate]['date']=date #refresh
                            self.data[message][candidate]['log'][self.log.getName()]=len(self.log.convo)
                        items.remove(candidate) #remove if added
        else:
                self.data[message]={}
        if len(items)>0: #if more to add or none was every added
                    for response in items:
                        if type(response)==type([]): response=response[0]
                        self.data[message][response]={'times':1,'date':date,'log':{self.log.getName():len(self.log.convo)}}
        self.save()
    def save(self):
        with open(SYSTEM_PATHWAY+"infoFiles/"+self.name, 'w', encoding='utf-8') as f:
            json.dump(self.data, f)
    def deleteItem(self,message,response):
        #delete a response
        try:
            self.data[message].pop(response)
            self.save()
        except: #was not in file
            pass
    def findOutput(self,message):
        #search these areas for a best match
        responses={}
        dateOfRemove=datetime.today()#use to clean up unused
        for msg in self.data:
            if LP.get_similarity(msg,message)>0.8: #gather responses of good probability
                for response in self.data[msg]: #gather responses
                    times=self.data[msg][response]['times']
                    if times==4:
                        responses[response]=self.data[msg][response]['log'] #save responses and logs
                    if datetime.strptime(self.data[msg][response]['date'],"%d/%m/%Y") < dateOfRemove-timedelta(days=times*2): #forget after so many days
                        self.data[msg].pop(response) #delete and keep files clean
                        self.save()
        response=""
        probability=0
        for candidate in responses: #Select response with log file conversation most similar to freq_topics of convo
            for logName in responses[candidate]: #look through log files of these items outputs.
                ######NEEDS IMPROVING
                log=Log(name=logName)
                freq=log.findTopics(responses[candidate][logName]) #get topics of recent convo in log
                res=0
                if float(len(set(freq) | set(self.FT)))>0:
                    res = len(set(freq) & set(self.FT)) / float(len(set(freq) | set(self.FT))) * 100
                if res>=probability: #set highest ranking
                    response=candidate
                    probability=res
        probability=0.5 ######DEBUG
        return response, probability #return response and match probibility
    def findRelated(self):
        #loop through items and find first message with no responses or lowest response
        responseNum=5
        messageS=""
        i=0
        keys2=list(self.data.keys())
        while j<len(self.data) and responseNum>1:
                message=keys2[j] #get each message
                z=0
                keys3=list(self.data[message].keys())
                localMax=1
                while z<len(self.data[message]) and responseNum>1: #find each response
                    response=keys3[z]
                    data=self.data[message][response]
                    if data['times']>localMax: #find the largest
                        localMax=data['times']
                    z+=1
                if localMax<responseNum: #store the lowest overal response to find un answered
                    messageS=message
                    responseNum=localMax
                j+=1
        return messageS, responseNum
class AI:
    #The AI class binds all the features of memory management and data interfacing
    #it provides options on whether the AI will learn or not with the user interaction
    def __init__(self,clean=False,pathway=""): #clean parameter decides whether to purge rude items
        #define language processor
        SYSTEM_PATHWAY=pathway #global variable
        if len(SYSTEM_PATHWAY)>0 and SYSTEM_PATHWAY[-1]!="/": SYSTEM_PATHWAY=SYSTEM_PATHWAY+"/" #validate
        self.lang=LP
        self.ST=shortTerm()
        self.time=0
        self.user="default"
    def validate(self,message):
        #prevent user creating errors
        for i in message:
            message[i]=message[i].replace(":","").replace("{","(").replace("}",")")
        return message
    def chat(self,message,user="default"):
        #if a considerable amount of time has gone since last interaction restart log file
        #if user has changed then restart log file
        #reset time
        message=self.validate(message)
        freq=LP.get_frequent_topics(self.ST.getText()) #get the frequent topics
        if len(self.ST.convo)>0:
            output=self.ST.getLastItem() #get the previous output from short term
            outputN=LP.split_meaning(output, Type="subjects") #gather the nouns within the output
            string=""
            for i in outputN: string+=i+" "
            outputN=LP.get_dominant_topic(string)
            if len(outputN)==0: outputN=['entity']
            #get all information logs
            for logName in outputN:
                IL=informationLog(logName,freq,self.ST.current) #create each file
                IL.add(output,list(message.values())) #add previous output to this message
            
        msg=message['text'] #split message to get text
        msgN=LP.split_meaning(msg, Type="subjects")#gather the nouns within the text
        string=""
        for i in msgN: string+=i+" "
        msgN=LP.get_frequent_topics(string)
        if len(msgN)==0: msgN=['entity']
        #get all information logs
        response=""
        p=0
        for logName in msgN:
            IL=informationLog(logName,freq,self.ST.current) #create each file
            responseT,pT=IL.findOutput(msg) #find outputs of each log file and probability
            if pT>p: #pick highest probability
                p=pT
                response=responseT
        if p<0.5: #if probability still low
            #get item with low or little responses
            relatedS=""
            numS=5
            for logName in msgN:
                IL=informationLog(logName,freq,self.ST.current) #create each file
                related,num=IL.findRelated()
                if num<numS: #GET LOWEST OUT OF BATCH
                    numS=num
                    relatedS=related
            response=relatedS #set the response
        if response=="": response=msg
        self.ST.add(message) #add message to conversation
        self.ST.add({"text":response})
        return response#return something from most similar topic which exists #otherwise return best chance
    def changeUser(self):
        #change the user
        pass
    def setPersonalInfo(self,log):
        #given a log set this as personal information to not be changed or altered
        pass
    def checkPersonal(self,message):
        #given a message, check if there is personal information to give
        pass
    def chatWithoutAdd(self,message):
        #find an output to a message
        #or find a near outout to a message
        #do not add or alter the system when doing so
        message=self.validate(message)
        msg=message['text'] #split message to get text
        msgN=LP.split_meaning(msg, Type="subjects")#gather the nouns within the text
        string=""
        for i in msgN: string+=i+" "
        msgN=LP.get_frequent_topics(string)
        if len(msgN)==0: msgN=['entity']
        #get all information logs
        response=""
        p=0
        for logName in msgN:
            IL=informationLog(logName,freq,self.ST.current) #create each file
            responseT,pT=IL.findOutput(msg) #find outputs of each log file and probability
            if pT>p: #pick highest probability
                p=pT
                response=responseT
        self.ST.add(message) #add message to conversation
        self.ST.add({"text":response})
        return response
    def setAnswer(self,message,response):
        pass
    def train(self,conversation):
        self.ST.commitLog() #create new log file each time
        for message,response in conversation:
            message=message.replace(":","").replace("}",")")
            response=response.replace(":","").replace("{","(")
            freq=LP.get_frequent_topics(self.ST.getText()) #get the frequent topics
            messageN=LP.split_meaning(message, Type="subjects") #gather the nouns within the output
            string=""
            for i in messageN: string+=i+" "
            messageN=LP.get_dominant_topic(string)
            if len(messageN)==0: messageN=['entity']
            #get all information logs
            for logName in messageN:
                IL=informationLog(logName,freq,self.ST.current) #create each file
                IL.add(message,[response]) #add previous output to this message
            self.ST.add({'text':message}) #add message to conversation
            self.ST.add({'text':response}) #add message to conversation
ai=AI()


file=open("train_full.json") #read file
r=file.read()
file.close()
data = json.loads(r) #convert to dictionary
training=[]
count=0
for i in data:
    train=[]
    for j in i['thread']:
        text=j['text']
        train.append(text.replace("?","").replace("!","").replace(".",""))
    training.append(train)
for train in training: #train each in
    flow=[]
    for i in range(len(train)-1):
        phrase1= train[i]
        phrase2=train[i+1]
        flow.append([phrase1,phrase2])
    print(str(count/len(data) *100),"%")
    if len(flow)>0:
        ai.train(flow)
    count+=1
        
while True:
    x=input(">")
    print(">",ai.chat({"text":x}))
