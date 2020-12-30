"""
    SHEP v0.0.10
    Code By Dexter Shepherd, aged 19
    shepai.github.io

    Building on v0.0.9, this version learns by repetition. It looks at how the user responds to a message, and will learn to respond with
    the same or similar messages. This also prevents the machine learning irrelevent messages entered in.
    The code is to provide a smarter self learning chatbot which appears to learn naturaly and efficiently. 

    The code is split down into different classes. It also uses the language processor library I wrote.
    
    Short term
        This class stores the current log file of the coversation, the last 10 items of conversation, and the strength of different responses
        to messages. The strength is based on how often it is responded in this way.
    Long term
        This is the main memory which stores the topics and which log files they point to. It can also retrieve all the log files in relation to a topic. 
    Log
        This provides an interface to the json files holding a log of all the conversations
    AI
        This is the main class which binds all classes together. On initialization it creates a log, a short term memory and long term, as well as calls in the language
        analyser. 
"""
from languageProcessor import *
import json
import random
import os
import time
import difflib

class shortTerm:
    #short term memory class to store potential answers
    def __init__(self,size=10):
        try:
            file=open("PandA.json") #read file
            r=file.read()
            file.close()
            self.phrasesAndAnswers = json.loads(r) #convert to dictionary
        except:
            self.phrasesAndAnswers={}
        self.log=[]
        self.size=size #max amount of items it can store
        self.logFile=log()
    def add(self,item,answer):
        self.phrasesAndAnswers[item['speech']]=self.phrasesAndAnswers.get(item['speech'],{})
        self.phrasesAndAnswers[item['speech']][answer['speech']]=[1,"date"]
        self.save()
    def increase(self,item,answer):
        #increase the times it has been found
        if item['speech'] in self.phrasesAndAnswers and answer['speech'] in self.phrasesAndAnswers[item['speech']]:
            if self.phrasesAndAnswers[item['speech']][answer['speech']][0]<4:
                stats=self.phrasesAndAnswers[item['speech']][answer['speech']]
                stats[0]+=1 #increase
                self.phrasesAndAnswers[item['speech']][answer['speech']]=stats
        self.save()
    def addLog(self,items):
        #add information to the log to store what has been going on
        self.log.append(items)
        self.logFile.add(items)
        if len(self.log)>self.size:
            self.log.remove(self.log[0]) #remove oldest element
    def getConvo(self):
        #get conversation in paragraph form
        string=""
        for i in self.log:
            string+=i['speech']+". "
        return string[:-2]
    def save(self):
        with open("PandA.json", 'w', encoding='utf-8') as f:
            json.dump(self.phrasesAndAnswers, f)
    def getLast(self):
        if len(self.log)-2>0:
            return self.log[len(self.log)-2]
        return None
class log:
    #store the log file information of the current conversation
    def __init__(self,name=""):
        #create unique name
        self.convo={}
        if not os.path.isdir("logFiles"):
            os.mkdir("logFiles") #set aside area for logFiles
        if name!="": #allow user to set name
            self.name=name
            try:
                file=open(self.name) #read file
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
        with open(self.name, 'w', encoding='utf-8') as f:
            json.dump(self.convo, f)
    def add(self,items):
        self.convo[len(self.convo)]=items #add item to the conversation
        self.save() #save
    def findAnswer(self,items): #return the response to an item in the list
        Next=False
        for i in self.convo: #loop through each item
            if Next: #if flag activated
                return self.convo[i] #return current item
            if self.convo[i]['speech']==items:
                Next=True #flag to gather next variable
        return None
    def getLastItem(self):
        if len(self.convo)-1>0:
            return self.convo[str(len(self.convo)-1)]
        else:
            return None
class longTerm:
    #long term memory to store routes of conversation logs based on topic
    def __init__(self,log):
        self.log=log
        try:
            file=open("convo.json") #read file
            r=file.read()
            file.close()
            self.topics = json.loads(r) #convert to dictionary
            file=open("sentence.json") #read file
            r=file.read()
            file.close()
            self.sentenceTopics = json.loads(r) #convert to dictionary
        except:
            self.topics={"":[]} #store each topic and the log file related
            self.sentenceTopics={"":[]}
    def find(self,topics,convoTopics):
        #search through file system to find best match
        if topics==[]:
            topics=["other"]
        if convoTopics==[]:
            convoTopics=["other"]
        topicLog=[]
        name=self.log.getName()
        for i in topics:
            if i in self.sentenceTopics:
                topicLog+=self.sentenceTopics[i] #get the log files with these topics
                if name not in self.sentenceTopics[i]:
                    arr=self.sentenceTopics[i]
                    arr.append(name) #add new name
                    self.sentenceTopics[i]=arr
            else:
                self.sentenceTopics[i]=[name] #get log name
        #of these find the most similar log files
        self.save()
        return topicLog
    def linkToTopic(self,topics):
        name=self.log.getName()
        if topics==[]:
            topics=["other"]
        for i in topics:
            if i in self.sentenceTopics:
                arr=self.sentenceTopics[i]
                arr.append(name) #add new name
                self.sentenceTopics[i]=arr
            else:
                self.sentenceTopics[i]=[name] #get log name
        self.save()
    def save(self):
        with open("convo.json", 'w', encoding='utf-8') as f:
            json.dump(self.sentenceTopics, f)
        with open("sentence.json", 'w', encoding='utf-8') as f:
            json.dump(self.topics, f)
class AI:
    #main class to provide interface with AI
    def __init__(self):
        #define language processor
        self.lang=LanguageProcessor()
        #define memories
        self.ST=shortTerm()
        self.memory=longTerm(self.ST.logFile)
        
    def chat(self,message):
        self.ST.addLog(message)
        #get answers of previous
        #if the message is not one of the answers add it to the short term
        convoTopics=self.lang.get_dominant_topic(self.ST.getConvo())#get topic of conversation
        topics=self.lang.get_dominant_topic(message['speech'])#get topics of message
        logs=self.memory.find(topics,convoTopics)#check long term memory for response
        answers=self.check(message,logs)
        lastItem=self.ST.getLast() #get the last item
        if lastItem!=None: #there is a value
            #set the response as linked to the last item
            if lastItem['speech'] not in self.ST.phrasesAndAnswers:
                self.ST.add(lastItem,message)
            self.ST.increase(lastItem,message) #increase statistics
        refined=[]
        random.shuffle(answers)
        for answer in answers :
            if self.isReliable(message,answer): #check reliability
                refined.append(answer)
                if len(refined)>5:
                    break
        if len(refined)>0:
            answer=random.choice(refined)
            self.ST.addLog(answer) #add to log of conversation
            return answer['speech'] #if reliable return
        #otherwise try return something topic related but un answered
        self.ST.logFile=log() #new log for change in subject
        self.memory.log=self.ST.logFile
        response=self.getLinked(message,logs)
        response={'speech':response}
        self.ST.addLog(response) #add to log of conversation
        self.memory.linkToTopic(topics) #link to where it begins
        return response['speech'] #for now return
    def getLinked(self,message,logFiles):
        #get a reponse slightly linked to respond with
        message=message['speech']
        top=0
        answer=""
        backup=message #default respond with same message
        topics2=self.lang.get_all_topics(message)
        if len(logFiles)==0: #if no log files
            convoTopics=self.lang.get_all_topics(self.ST.getConvo())#get topic of conversation
            topics=self.lang.get_all_topics(message)#get topics of message
            logFiles=self.memory.find(topics,convoTopics)#check long term memory for response
        for file in logFiles:
            current=log(name=file) #create log objects with conversation
            temp=current.getLastItem()
            if temp!=None: #only allow strings
                temp=temp['speech']
                topics1=self.lang.get_all_topics(temp)
                sm=difflib.SequenceMatcher(None,topics2,topics1)
                num=sm.ratio() #return score
                if num>top and temp not in self.ST.getConvo(): #get most related but not the same
                    top=num
                    answer=temp
                elif num>top and temp!=current.getLastItem()['speech'] and current.getLastItem()['speech']!=None: #get backp incase nothing meets high recquirement
                    backup=temp
        if answer=="":
            return backup
        return answer
    def check(self,message,logFiles):
        #check for the message and potential answer
        answers=[]
        for file in logFiles:
            current=log(name=file) #create log objects with conversation
            top=0
            sent=""
            keys =list(current.convo.keys()) #randomize order to prevent repetition
            random.shuffle(keys) #randomize order
            d={}
            for i in keys:
                d[i]=current.convo[i] #transfer content
            for data in d: #attempt to find similar phrase
                sentence=d[data]['speech']
                if sentence!=None:
                    temp=self.lang.get_similarity(sentence,message['speech'])
                    if temp>top and temp>0.7: #gather most likely
                        sent=sentence
                        top=temp
                counter=0
                #for Object in data.get('vision',[]): #check objects present
                #        if Object in message.get('vision',[]):
                #            counter+=1
                #if counter>0:
                #    answer=current.findAnswer(sentence)
                #    if answer!=None: answers.append(answer) #if found gather the answers
            answer=current.findAnswer(sent)
            if answer!=None: answers.append(answer) #if found gather the answers
            if len(answers)>5: #no need to loop when found sample
                break
        return answers
    def isLinked(self,data,answers):
        #check whether and which objects are connected
        pass
    def isReliable(self,data,answers):
        #check how reliable an answer is
        phrase=data['speech'] #speech
        answer=answers['speech']
        tokens=self.lang.split_meaning(phrase,Type="structure")+self.lang.split_meaning(phrase,Type="subjects")#get tokens of structre
        for i in self.ST.phrasesAndAnswers:
                if difflib.SequenceMatcher(None,i.split(),phrase.split()).ratio() > 0.6: #only check if similar to word
                    if self.lang.get_Similar_Tokens(i,tokens)>0.7 and self.ST.phrasesAndAnswers[i].get(answer,None)!=None: #check is same (use similarity of language instead)
                        for ans in self.ST.phrasesAndAnswers[i]:
                            if self.lang.subject_similarity_score(answer,ans)>0.7 or self.lang.structural_similarity_score(answer,ans) >0.7: #if the jist of whats being said is similar
                                stats=self.ST.phrasesAndAnswers[i][ans] #gather stats
                                if stats[0]==4:
                                    return True #found
        return False
    def train(self,data):
        #train the bot on data
        for i, message in enumerate(data[:-1]):
            message={'speech':message}
            self.ST.addLog(message)
            #get answers of previous
            #if the message is not one of the answers add it to the short term
            convoTopics=self.lang.get_dominant_topic(self.ST.getConvo())#get topic of conversation
            topics=self.lang.get_dominant_topic(message['speech'])#get topics of message
            logs=self.memory.find(topics,convoTopics)#check long term memory for response
            answer={'speech':data[i+1]}
            self.isReliable(message,answer)
        self.ST.logFile=log() #new log for change in subject
        self.memory.log=self.ST.logFile
        print("Training complete")


a=AI()

while True:
    q={"speech":input(">")}
    print("Answer:",a.chat(q))

"""
file=open("train_full.json") #read file
r=file.read()
file.close()
data = json.loads(r) #convert to dictionary
training=[]
for i in data:
    train=[]
    for j in i['thread']:
        text=j['text']
        train.append(text.replace("?","").replace("!","").replace(".",""))
    training.append(train)
for i,convo in enumerate(training):
    a.train(convo)
    print(str((i/len(training))*100)+"%")
#NEED TO ADD:

#Manipulation of information with similar structure
#"""
