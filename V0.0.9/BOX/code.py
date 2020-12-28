from AI import CB
import speech_recognition as sr
import os
import sys
import serial
import time
#The following line is for serial over GPIO
port = 'COM3'
ard = serial.Serial(port,9600,timeout=5)
time.sleep(2)
systemPath=sys.path[0]+"/" #gather the pathway to the file
m=sr.Microphone()
r=sr.Recognizer()
eye="""
-RR--RR-
RWBRRBWR
RBBRRBBR
-RR--RR-
--------
--------
--------
--------""".replace("\n","")
blink="""
--------
RRRRRRRR
RRRRRRRR
--------
--------
--------
--------
--------""".replace("\n","")
def INPUT(): #input method
    with m as source: #gather audio
        r.adjust_for_ambient_noise(source)
        showEye(eye)
        print(">")
        audio=r.listen(source)
    showEye(blink)
    try:
        return r.recognize_google(audio)
    except:
        return ""
def OUTPUT(string): #output to user
    print(string)
    os.system('espeak "'+string+'" 2>/dev/null')
def showEye(eye):
    a=[]
    for i in eye:
        a.append(ord(i))
    ard.write(a)
    print("-----")


bot=CB(systemPath+"testCB/")
while True:
    UI=INPUT()
    if UI!="":
        print(UI)
        OUTPUT(bot.chat(UI))
