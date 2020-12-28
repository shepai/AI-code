#hardware library
from adafruit_servokit import ServoKit
class Servo:
    def __init__(self,pin,startPos,max):
        #initialize the servo
        self.pos=startPos
        self.pin=pin
        self.max=max
        self.kit = ServoKit(channels=16)
        if pin<0 or pin>16: #check the pin is valid
            raise ValueError("pin not valid")
        kit.servo[self.pin].actuation_range = max
        kit.servo[self.pin].angle = startPos
    def setPos(self,pos):
        self.pos=pos
        kit.servo[self.pin].angle = pos
    def turnRight(self):
        if self.pos+5<self.max: #validate the turn
            kit.servo[self.pin].angle = self.max
        kit.servo[self.pin].angle = self.pos+5
    def turnLeft(self):
        if self.pos-5>=0: #validate the turn
            kit.servo[self.pin].angle = 0
        kit.servo[self.pin].angle = self.pos-5
class Action:
    def __init__(self,array):
        self.array=array
    def getAction(self):
        return self.array
class Spider:
    #class for the spider robot
    #must use 9 servos of 0 to 180
    def __init__(self):
        #define servo
        LF1=Servo(0,10,180)
        LF2=Servo(1,10,180)
        RF1=Servo(2,10,180)
        RF2=Servo(3,10,180)
        LB1=Servo(4,10,180)
        LB2=Servo(5,10,180)
        RB1=Servo(6,10,180)
        RB2=Servo(7,10,180)
        Rotate=Servo(8,0,180)
        self.dictionary={"LF1":LF1,"LF2":LF2,"RF1":RF1,
                         "RF2":RF2,"LB1":LB1,"LB2":LB2,"RB1":RB1,"RB2":RB2,"Rotate":Rotate}
        #set each leg action
        legA=Action(["LF1:l","LF2:l","LF1:l"])
        legB=Action(["RF1:r","RF2:r","RF1:r"])
        legC=Action(["LB1:r","LB2:l","LB1:r"])
        legD=Action(["RB1:l","RB2:r","RB1:l"])
        self.walk=Action([legA,legB,legC,legD])
    def perform_action(self,action):
        #perform the action given
        for i in action:
            leg=i.split(":")
            if leg[1]=="r":
                self.dictionary[leg[0]].turnRight()
            else:
                self.dictionary[leg[0]].turnLeft()
    def forward(self,direction):
        #move foward in the given direction
        if direction=="N":
            #perform forward in north direction
            walk=self.walk.getAction()
            toWalk=[walk[1],walk[2],walk[3],walk[0]]
            self.perform_action(toWalk)
        elif direction=="E":
            #perform forward in north direction
            walk=self.walk.getAction()
            toWalk=[walk[2],walk[3],walk[0],walk[1]]
            self.perform_action(toWalk)
        elif direction=="S":
            #perform forward in north direction
            walk=self.walk.getAction()
            toWalk=[walk[3],walk[0],walk[1],walk[2]]
            self.perform_action(toWalk)
        elif direction=="W":
            #perform forward in north direction
            walk=self.walk.getAction()
            toWalk=[walk[0],walk[1],walk[2],walk[3]]
            self.perform_action(toWalk)
            
        
