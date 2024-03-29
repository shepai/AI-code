"""
    Language Processor Class
    Code By Dexter Shepherd, aged 19
    shepai.github.io
    
    * Provides the abilities of semmantic analyses and breaking down of language into understanding
    * Provides sentence similarity scores both on semmantics and stucture
    * Stores data in a structured by topic way

    Documentation
    * split_meaning(text, Type="all", tags=False)
        #will return an array of words that show the meaning down to key features of a sentence
        #optional whether it returns tags or words with tags=False for words
        #Type can be either "subjects", "structure" or "all" to return words relating to the type

    * break_down(sentence)
        #Break sentence down into components such as [what is,the capital,of england]

    * retokenize(sentence)
        #Break sentence down into tagged frequent words and subjects
        
    * get_dominant_topic(text)
        #returns the most dominant topics in a piece of text entered as parameter
        
    * get_all_topics(text)
        #returns all topics in a piece of text entered as parameter
        
    * get_frequent_topics(text)
        #get the most frequent topics in a piece of text
        
    * get_all_topic_frequencies(text)
        #returns the topics of a piece of text broken down to frequency of apperance
        
    * distance_to_root(node1)
        #returns an array of topic ancestors of a word
        
    * train(text)
        #trains text into the system in a topic based heirachy
        
    * subject_similarity_score(phrase1,phrase2)
        #returns how similar two sentences are based on subject
        
    * structural_similarity_score(phrase1,phrase2)
        #returns how similar two sentences are based on structure
        #"what is your name" and "what is the weather like" have similar structures
        
    * get individual topic(text)
        #get the topics relating to each subject in the text
        
    * get_linked(text)
        #returns the current text saved in the system which is linked
        #adds text to the heirarchy if not in there

    * get_similarity
        #get words which mean the same
        
    * get_same(word)
        #get words that mean the same 

    * is_question(sentence)
        #checks if a sentence is a question or not
        #returns boolean

    * extract_information(words)
        #extracts information about the user or system
"""

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer 

import nltk
import difflib

class LanguageProcessor:
    def __init__(self):
        self.rules={}
        self.lemmatizer = WordNetLemmatizer() 
        self.stopWords=stopwords.words('english')
        self.questionTerms={"what":"","when":"time","who":"person","where":"place","how":""}
        self.topics={} #stores the topic and a key based on size of phrases
        self.phrases={} #a dictionary of dictonaries storing text input and broken up sentences into phrases
    def split_meaning(self,text,Type="all",tags=False):
        #get the key words determining the sentence meaning
        if Type not in ["all","subjects","structure"]:
            raise TypeError("Incorrect Type '"+Type+"' entered")
        tokens = nltk.word_tokenize(text) #tokenize sentence
        tagged = nltk.pos_tag(tokens) #get tags
        words=[]
        for i in tagged:
            if ((("W" == i[1][0] or "V" == i[1][0]) and (Type=="all" or Type=="structure")) #question-determiners and verbs
            or (("NN" in i[1]  and (Type=="all" or Type=="subjects") or (("IN" in i[1] or "JJ" in i[1] or "VBG" in i[1] or "VB"==i[1]) and Type=="all"))) #subjects
            or ("P" in i[1][:-1] and Type=="all")): #pronouns (who is it directed at)
                if not tags: #if tokens are false
                    words.append(i[0]) #return words
                else:
                    words.append(i[1]) #return tags
        return words
    def retokenize(self,text):
        #retokenize a sentence by tagging any words which can be subsituted
        text=text.replace("'s","")
        words=text.split()
        tokens = nltk.word_tokenize(text) #tokenize sentence
        t=[]
        for i in tokens:
            t.append(self.lemmatizer.lemmatize(i))
        tokens=t.copy()
        tagged = nltk.pos_tag(tokens) #get tags
        newSent=""
        for word,tag in tagged:
                if "W" == tag[0]:
                    newSent+=tag+" "
                elif "V" == tag[0] and tag!="VBG" : #remove
                    pass
                else:
                    newSent+=word+" "
        return newSent[:-1]
    def break_down(self,sentence):
        sentence=sentence.lower() #convert to lower case
        tokens=nltk.word_tokenize(sentence)
        tags=nltk.pos_tag(tokens)
        sub=[]
        phrase=""
        for word,tag in tags:
            if tag=="VBZ": #add and then split
                phrase+=word+" "
                if phrase!="": sub.append(phrase)
                phrase=""
            elif tag[0]=="W" or tag=="ADJ" or tag=="IN" or tag=="CC" or tag=="TO" or tag=="VBG" or tag=="PRP$":
                #split then add
                if phrase!="": sub.append(phrase)
                phrase=""
                phrase+=word+" "
            else:
                phrase+=word+" "
        if phrase!="": sub.append(phrase)
        return sub
    def get_dominant_topic(self,text): #return the most dominant topics in the text
        frequent=self.get_all_topic_frequencies(text)
        best_score=0
        previousPos=0
        previousFreq=0
        lowest_most_frequent=[]
        for i in frequent: #find the lowest most common ancestor (essentially find the subjects)
            val=frequent[i]
            score=int(val[1]-(val[0]*2)) #freq-position
            if nltk.pos_tag([val[2]])[0][1][0] == "N": score+=3 #nouns are more significant
            if score>best_score or (score==best_score and val[0]<previousPos and val[1]>previousFreq) :
                best_score=score
                lowest_most_frequent=i
                previousPos=val[0]
                previousFreq=val[1]
                lowest_most_frequent=[i]
            elif score==best_score and val[0]==previousPos and val[1]==previousFreq: #if it is equal to
                lowest_most_frequent.append(i)
        return lowest_most_frequent
    def get_all_topics(self,text): #return all topics in a piece of text
        frequent=self.get_all_topic_frequencies(text)
        array=[]
        for i in frequent: #convert to list
            if i not in array: #remove duplicates
                array.append(i)
        return array
    def get_frequent_topics(self,text): #return all topics in a piece of text
        frequent=self.get_all_topic_frequencies(text)
        top=0
        av=0
        arr=[]
        for i in frequent: #convert to list
            val=frequent[i]
            av+=val[1]
        if len(frequent)>0:
            av=av/len(frequent)
        else:
            av=0
        for i in frequent:
            val=frequent[i]
            if nltk.pos_tag([val[2]])[0][1][0] == "N": val[1]+=1 #nouns are more significant
            if val[1] >av:
                if i not in arr:
                    arr.append(i)
        return arr
    def get_all_topic_frequencies(self,text):
        words=[word for word in text.split() if word not in self.stopWords]
        ancestors={}
        for word in words: #gather ancestors for all words
            ancestors[word]=self.distance_to_root(word)
        frequent={}
        for ancestor in ancestors: #sort into frequency of word
            wordT=ancestors[ancestor]
            for j,i in enumerate(wordT): #get every word in list [position in ancestors,frequency,ancestor]
                frequent[i]=frequent.get(i,[j,0,ancestor])
                frequent[i][1]+=1
        if "entity" in frequent: frequent.pop("entity")
        return frequent
    def distance_to_root(self,node1):
        #gather every ancestor node from wordnet
        if type(node1)==str:
            node1=wn.synsets(node1)
        if len(node1)>0:
            value=0
            hypernyms=node1[0].hypernyms()
            if hypernyms != []:
                value = self.distance_to_root(hypernyms)
                return [str(hypernyms[0].lemmas()[0].name())]+value
        return []
    def train(self,text):
        topics=self.get_dominant_topic(text)
        all_topics=self.get_frequent_topics(text)
        sentences=[x for x in text.split(".") if x!='']
        count=0
        PKey=-1
        #Firstly add phrases to the phrase data structure
        for key in self.phrases:
             count=0
             for k in self.phrases[key]:
                 for i,sentence in enumerate(sentences): #enumerate through sentences
                     if self.phrases[key][k].lower()==sentence.lower():
                         count+=1 #increase amount of sentences found
             if count==len(sentences):
                     PKey=key #if found set key
        if PKey==-1: #create PK if none exists
            PKey=len(self.phrases) 
            self.phrases[PKey]={}
            for i,sentence in enumerate(sentences):
                self.phrases[PKey][i]=sentence
        #loop through topic structure to assign correct keys
        LinkedText=[]
        for topic in topics: #get and add Keys
             self.topics[topic]=self.topics.get(topic,{}) #set new if not there
             self.topics[topic][PKey]=1
    def subject_similarity_score(self,phrase1,phrase2):
        #get the similarity between two token arrays
        subjects1=self.split_meaning(phrase1,Type="subjects")
        subjects2=self.split_meaning(phrase2,Type="subjects")
        similarity_matrix=[]
        for i,word1 in enumerate(subjects1): #loop through items to make matrix of all path scores
            similarity_matrix.append([])
            for word2 in subjects2:
                try:
                    word1S=wn.synsets(word1)[0] #gather both synset first sense
                    word2S=wn.synsets(word2)[0]
                    similarity_matrix[i].append(word1S.path_similarity(word2S)) #add to matrix
                except IndexError:
                    similarity_matrix[i].append(None) #add none if cannot be compared
        count=0
        for i,rows in  enumerate(similarity_matrix): #find the amount of similar words
            for j,columns in  enumerate(rows):
                if columns != None and columns>0.3: #counted as similar if 30%
                    count+=1 #increase count
        if max(len(subjects1),len(subjects2))>0:
            return count/max(len(subjects1),len(subjects2)) #return score
        else:
            return 0
    def structural_similarity_score(self,phrase1,phrase2):
        s1=self.split_meaning(phrase1,Type="structure",tags=True) #get tokens of structre
        s2=self.split_meaning(phrase2,Type="structure",tags=True) #get tokens of structure
        sm=difflib.SequenceMatcher(None,s1,s2)
        return sm.ratio() #return score
    def get_similarity(self,phrase1,phrase2):
        try:
            s1=self.split_meaning(phrase1,Type="structure")+self.split_meaning(phrase1,Type="subjects")#get tokens of structre
            s2=self.split_meaning(phrase2,Type="structure")+self.split_meaning(phrase2,Type="subjects")#get tokens of structure
            if s1==[] and s2==[]:
                s1=phrase1.split()
                s2=phrase2.split()
            sm=difflib.SequenceMatcher(None,s1,s2)
            return sm.ratio() #return score
        except:
            print(phrase1,phrase2)
            raise TypeError("problem")
    def get_Similar_Tokens(self,phrase1,tokensToMatch):
        #does the same as get similar but only find tokens for one sentence
        s1=self.split_meaning(phrase1,Type="structure")+self.split_meaning(phrase1,Type="subjects")#get tokens of structre
        sm=difflib.SequenceMatcher(None,s1,tokensToMatch)
        return sm.ratio() #return score
    def get_linked(self,text):
        #get sentences which are closely linked
        topics=self.get_dominant_topic(text)
        keysToTry=[]
        for item in topics:
            keysToTry+=self.topics.get(item,{}) #gather all keys
        sentences=[]
        for key in keysToTry: #loop through 
            sentence=self.phrases[key] #get each sentence linked
            for i in sentence:
                if sentence[i] not in sentences: sentences.append(sentence[i])
        self.train(text) #add it to data
        return sentences
    def get_individual_topic(self,text):
        #get all topic headers
        subs=self.split_meaning(text,Type="subjects")
        topics=[]
        for word in subs:
            tmp=subs.copy()
            tmp.remove(word)
            word=self.lemmatizer.lemmatize(word)
            sense=""
            try:
                sense=self.get_sense(word,tmp)
                if len(sense.hyponyms())>0:
                    sense=sense.hyponyms()[0]
                    if len(sense.hyponyms())>0:
                        sense=sense.hyponyms()[0].lemmas()[0].name() #two up
                    else:
                        sense=sense.lemmas()[0].name() #one up
                else:
                    sense=sense.name().split(".")[0]
            except nltk.corpus.reader.wordnet.WordNetError:
                sense=word
            topics.append(sense)
        return topics
    def get_same(self,word):
        #get words which mean the same
        synonyms = []
        for syn in wordnet.synsets("active"):
            for l in syn.lemmas():
                synonyms.append(l.name())
        return synonyms
    def get_sense(self,word,otherSubjects):
        #get the senses
        top=wn.synset(word+".n.01") #default
        high=0
        for syn in wn.synsets(word): #loop through synsets
            d=syn.definition()
            d=d.split()
            count=0
            for sub in otherSubjects: #coount occurance of other subjects 
                if sub in d:
                    count+=1
            if count>high: #store best
                high=count
                top=syn
        return top
    def is_question(self,words):
        #return true or false if sentence thinks is question
        if type(words)!=type([]): #get correct format
            words=self.break_down(words)
        if "do" in words[0] or "can" in words[0] or "have you" in words[0] or "have i" in words[0] or "have they" in words[0]: #only sentence if in begnining phrase
            #may need reconsidering with tags
            return True
        for i in self.questionTerms:
            for j in words:
                if i in j:
                    return True
        return False
    def extract_information(self,words):
        #extract information regarding the user or system
        if type(words)!=type([]): #get correct format
            words=self.break_down(words)
        system={}
        user={}
        nextNoun=""
        store=0
        for phrase in words:
            tokens = nltk.word_tokenize(phrase) #tokenize sentence
            tagged = nltk.pos_tag(tokens) #get tags
            ignore=-1
            #print(tagged)
            for i,val in enumerate(tagged):
                word,tag=val
                if (tag=="PRP$" and i+1<len(tagged) and tagged[i+1][1]=="NN") or (
                    (tag=="VB" or tag=="JJ" or tag=="NN") and i+1<len(tagged) and tagged[i+1][1]=="VBP"):
                    nextNoun=word+" "+tagged[i+1][0]
                    user[word+" "+tagged[i+1][0]]=""
                    store=i
                    ignore=i+1
                elif ignore!=i and nextNoun!="" and (tag=="NN" or tag=='CD'  or tag=='JJ' or tag=="NNS"):
                    user[nextNoun]+=word+" "
                elif user.get(nextNoun,False)!=False and nextNoun!=nextNoun.split(" ")[0]+" "+word: #disruptive word to gathering
                    if user[nextNoun]!="":
                        nextNoun=user[nextNoun] #break down further
                        user[nextNoun]=""
        return user


"""
test=LanguageProcessor()
print(test.extract_information(test.break_down("my name is dexter")))
print(test.extract_information(test.break_down("what is your name")))
print(test.extract_information(test.break_down("I need to get my car")))
print(test.extract_information(test.break_down("how old are you")))
print(test.extract_information(test.break_down("how many turtles can i have")))
print(test.extract_information(test.break_down("i am 3 years old")))
print(test.extract_information(test.break_down("my car is blue and green")))
print(test.get_sense("bank",["financial"]))
demoText1="I am going to the store to buy some bannanas. I will then go to clothes shop"
demoText2="how do i compute the sum of a large array. This is for the program analyses coursework. I am also struggling with writing pseudocode for algorithms."
demoText3="i need to find a good car mechanic. My front tyre fell off and the engine is damaged"
demoText4="i need to go to the toilet. Let's stop at the next gas station"
demoText5="I cannot wait till we go skiing next febuary. It will be nice to visit the mountains and play some sports."
demoText6="Back in elementary school you learnt the difference between nouns, verbs, adjectives, and adverbs. These 'word classes' are not just the idle invention of grammarians, but are useful categories for many language processing tasks. As we will see, they arise from simple analysis of the distribution of words in text."
demoText7="British soldiers have joined multinational units from across Europe and North America at Duke of Gloucester Barracks in South Cerney, RAF Fairford and Imjin Barracks, Gloucestershire, for Exercise LOYAL LEDA 2020, a key NATO exercise to validate the Allied Rapid Reaction Corps (ARRC), based in Gloucester."
demoText8="I am going to the shop to get some christmas bits and bobs. Then will buy a turkey for dinner"
demoText9="Let's go to the shop to buy a dog"


print("    Text: "+demoText1)
print("Topics of sentence:",test.get_dominant_topic(demoText1))
print("    Text: "+demoText2)
print("Topics of sentence:",test.get_dominant_topic(demoText2))
print("    Text: "+demoText3)
print("Topics of sentence:",test.get_dominant_topic(demoText3))
print("    Text: "+demoText4)
print("Topics of sentence:",test.get_dominant_topic(demoText4))
print("    Text: "+demoText5)
print("Topics of sentence:",test.get_dominant_topic(demoText5))
print("    Text: "+demoText6)
print("Topics of sentence:",test.get_dominant_topic(demoText6))
print("    Text: "+demoText7)
print(test.get_dominant_topic(demoText7))

def getText():
    TEXT=input("Enter your sentenc:")
    print("Topics of sentence:",test.get_dominant_topic(TEXT))
test.train(demoText1)
test.train(demoText2)
test.train(demoText3)
test.train(demoText4)
test.train(demoText5)
test.train(demoText6)
test.train(demoText7)
test.train(demoText9)
#print(test.topics)
#print(test.phrases)

#print(test.get_linked(demoText8))

(test.get_linked(demoText8))

#print(test.get_linked(demoText8))

#print(test.topics)
#print(test.phrases)
"""
