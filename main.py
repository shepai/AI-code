"""
Checkers code by Dexter Shepherd, aged 20

"""


import pygame
from tkinter import *
from tkinter import messagebox
import copy
import time
import random

class AI:
    """
    AI player which uses a mini max algorithm to find the best option through a game

    @param difficulty that the AI will play the game
    @param player holds integer value for player. Default set to 1, only here if we want an AI vs AI game
    """
    def __init__(self,difficulty,player=1):
        self.difficulty=difficulty
        self.player=player
    def successorFunction(self,board):
        #get the possible moves off of the current
        moves=[]
        #loop through board values and find piece objects owned by user
        if board.checkForceTake(self.player):
            #enforce force take
            for node in board.node:
                m=board.getMoves(node)
                for mov in m:
                            moves.append([node,mov])
        else: #gather all nodes
            for i in range(8):
                for j in range(8):
                    if board.grid[i][j]!=None and board.grid[i][j].getPlayer()==self.player:
                        m=board.getMoves([i,j])
                        for mov in m:
                            moves.append([[i,j],mov])
        return moves
            
class Piece:
    """
    Piece code will store the piece information
    player owning it
    whether it is crowned

    These conditions will specify what moves a piece can do

    @param player that the piece belongs to (int)
    """
    def __init__(self,player):
        self.crowned=False
        self.player=player
        self.pos=[]
        self.toggle=False
    #setters and getters defined below
    def setPosition(self,arr):
        self.pos=arr
    def getPlayer(self):
        return self.player
    def getCoord(self):
        return self.pos[0],self.pos[1]
    def getCrowned(self):
        return self.crowned
    def crown(self):
        self.crowned=True
    def toggleSelected(self): #toggle the selected value on and off
        self.toggle= not self.toggle
    def getSelected(self):
        return self.toggle
    def returnVectors(self):
        #return the possible vectors that the piece can take
        vectors=[]
        if self.player==1:
            if self.crowned: #can go both directions
                vectors+=[[-1,-1],[-1,1]]
            vectors+=[[1,1],[1,-1]]
        else:
            if self.crowned: #can go both directions
                vectors+=[[1,1],[1,-1]]
            vectors+=[[-1,-1],[-1,1]]
        return vectors
        
    
class GameBoard:
    """
    GameBoard creates a board and stores the positions of all the pieces.
    When making moves it validates moves by checking which piece has been selected
    It also checks whether the player has won or not
    """
    def __init__(self):
        self.grid=[[None for j in range(8)] for i in range(8)] #populate empty board
        #populate player pieces within the set pattern
        for j in range(8):
            if j%2!=0: self.grid[0][j]=Piece(1)
        for j in range(8):
            if j%2==0: self.grid[1][j]=Piece(1)
        for j in range(8):
            if j%2!=0: self.grid[2][j]=Piece(1)
        for j in range(8):
            if j%2==0: self.grid[7][j]=Piece(2)
        for j in range(8):
            if j%2!=0: self.grid[6][j]=Piece(2)
        for j in range(8):
            if j%2==0: self.grid[5][j]=Piece(2)
    def getWinDrawLose(self): #return whether the player [player 1 wins,draws,player 2 wins]
        count={'1':0,'2':0}
        for i in range(8):
            for j in range(8):
                if self.grid[i][j]!=None:
                    count[str(self.grid[i][j].getPlayer())]+=1 #count how many of each player exist
        if count['1']>0 and count['2']==0: #if player 1 is the only one left
             return [1,0,0]
        elif count['1']==1 and count['2']==1: #if only two pieces left it must be a draw
            return [0,1,0]
        elif count['1']==0 and count['2']>0: #if player 2 is the only one left
            return [0,0,1]
        return [0,0,0] #return default with no winners or losers or draw
    def getMoves(self,position):
        #get the possible moves from the current player
        #return grid positions
        current=self.grid[position[0]][position[1]].returnVectors()
        currentPlayer=self.grid[position[0]][position[1]].getPlayer()
        currentpos=[position.copy()]
        coords=[]
        virgin=False
        searched=[]
        self.routes={}
        while len(currentpos)>0: #while there are positions to explore
            pos=currentpos.pop(0) #get top of queue#
            searched.append(pos)
            for i,constraint in enumerate(current): #loop through immediate possible vectors
                if (pos[0]+constraint[0]>=0 and pos[0]+constraint[0]<8
                       and pos[1]+constraint[1]>=0 and pos[1]+constraint[1]<8): #check constraint
                    #constraint within bounds
                    #check whether it is obstructed
                    if not virgin and self.grid[pos[0]+constraint[0]][pos[1]+constraint[1]]==None:
                        #the position is allowed
                        coords.append([pos[0]+constraint[0],pos[1]+constraint[1]])
                    if (self.grid[pos[0]+constraint[0]][pos[1]+constraint[1]]!=None
                        and self.grid[pos[0]+constraint[0]][pos[1]+constraint[1]].getPlayer()!=currentPlayer):
                        #the piece in front is the enemy
                        if (pos[0]+(constraint[0]*2)>=0  and pos[0]+(constraint[0]*2)<8
                            and pos[1]+(constraint[1]*2)>=0 and pos[1]+(constraint[1]*2)<8
                            and self.grid[pos[0]+constraint[0]*2][pos[1]+constraint[1]*2]==None):
                            #add potential take and search the take position to see if it can double take or more
                            coords.append([pos[0]+constraint[0]*2,pos[1]+constraint[1]*2]) 
                            if [pos[0]+constraint[0]*2,pos[1]+constraint[1]*2] not in searched: #don't get stuck in circles
                                currentpos.append([pos[0]+constraint[0]*2,pos[1]+constraint[1]*2]) #check next position
                            arr=self.routes.get(str([pos[0]+constraint[0]*2,pos[1]+constraint[1]*2]),[])
                            arr.append({str(pos):[pos[0]+constraint[0],pos[1]+constraint[1]]})
                            self.routes[str([pos[0]+constraint[0]*2,pos[1]+constraint[1]*2])]=arr #trace route 

            virgin=True #set once gone through
        canTake=[]
        for pos in coords:
            #remove all non takable to force take
            if ( (pos[0]>=position[0]+2 or pos[1]>=position[1]+2) or
                (pos[0]>=position[0]+2 or pos[1]<=position[1]-2) or
                (pos[0]<=position[0]-2 or pos[1]>=position[1]+2) or
                (pos[0]<=position[0]-2 or pos[1]<=position[1]-2)):
                        canTake.append(pos)
                        
        if len(canTake)>0:
            return canTake
        return coords #return the collected coords
    def movePlayer(self,pos,end,gui):
        if self.grid[pos[0]][pos[1]]==None: #assertion
            raise TypeError("Cannot move what is not there")
        x=pos[0]
        y=pos[1]
        #pos=copy.deepcopy(self.grid[x][y])
        #col=self.grid[pos[0]][pos[1]].getPlayer()
        animate=[]
        intermediates=[]
        hide=[]
        if (abs(end[0])-abs(pos[0])>=2 or abs(end[0])-abs(pos[0])<=-2 or
            abs(end[1])-abs(pos[1])>=2 or abs(end[1])-abs(pos[1])<=-2): #players have been taken
            #print("taken",end,self.routes)
            q=[str(end)]
            checked=[]
            while len(q)>0: #work backwards
                item=q.pop(0)
                for dic in self.routes.get(item,[]): #if key get last node
                    for key in dic:
                        if key not in checked: #do not recheck positions
                            checked.append(key)
                            ind=dic[key]
                            if self.grid[ind[0]][ind[1]].getCrowned(): #regicide enforcement
                                self.grid[pos[0]][pos[1]].crown() #become monarch
                            #self.grid[ind[0]][ind[1]]=None
                            animate.append(copy.deepcopy(ind))
                            intermediate=item.replace("[","").replace("]","")
                            intermediate=intermediate.split(",")
                            hide.append(copy.deepcopy([pos]))
                            intermediates.append([int(intermediate[0]),int(intermediate[1])])
                            
                            q.append(key)
                        if key==str(pos): #if start pos found exit
                            q=[]
                            break
                    if key==str(pos): #inefficent but it works
                            q=[]
                            break
        if gui!=None and len(animate)>=1: #perform the animation if gui included
            gui.selected=[]
            for i in range(1,len(animate)+1):
                currentPiece=animate[len(animate)-i]
                self.grid[currentPiece[0]][currentPiece[1]]=None #set grid
                toHide=hide[len(animate)-i]
                inter=intermediates[len(animate)-i]
                gui.displayBoard(hide=toHide,place=inter) #display on gui
                pygame.display.flip()
                time.sleep(0.5) #pause to show
        elif len(animate)>0: #if no gui is provided
            for i in range(len(animate)):
                currentPiece=animate[i]
                self.grid[currentPiece[0]][currentPiece[1]]=None
        #switch the positions of new and old
        pos=copy.deepcopy(self.grid[x][y])
        self.grid[x][y]=None #rewrite
        self.grid[end[0]][end[1]]=copy.deepcopy(pos) 
        if end[0]==0 and self.grid[end[0]][end[1]].getPlayer()==2: #made it to end
            self.grid[end[0]][end[1]].crown()
        if end[0]==7 and self.grid[end[0]][end[1]].getPlayer()==1: #made it to end
            self.grid[end[0]][end[1]].crown()
    def checkForceTake(self,player):
        #take in the player as an integer and return whether
        #or not there is a force take move to be applied
        canTake=[]
        self.node=[]
        for i in range(8):
            for j in range(8):
                position=[i,j]
                if self.grid[i][j]!=None and self.grid[i][j].getPlayer()==player: #check player
                    coords=self.getMoves([i,j])
                    for pos in coords:
                        #remove all non takable to force take
                        if ( (pos[0]>=position[0]+2 or pos[1]>=position[1]+2) or
                            (pos[0]>=position[0]+2 or pos[1]<=position[1]-2) or
                            (pos[0]<=position[0]-2 or pos[1]>=position[1]+2) or
                            (pos[0]<=position[0]-2 or pos[1]<=position[1]-2)):
                            canTake.append(pos)
                            self.node.append([i,j])
                            #self.grid[i][j].toggle=True
        if len(canTake)>0:return True
        return False
class main:
    def __init__(self):
        self.board=GameBoard()
        pygame.init()
        #conditions of each grid square
        self.width=65
        self.mid=int(self.width/2)
        self.height=65
        self.radius=30
        #define colours
        self.black=(0,0,0)
        self.white=(255,255,255)
        self.red=(255,0,0)
        self.yellow=(230, 209, 23)
        self.greyBackground =(203, 206, 203)
        self.blue=(0,0,255)
        self.green=(0,255,0)
        #define window size
        self.windowSize=[960, 640]
        self.xDistanceFromEdge=220
        self.selected=[]
        Tk().wm_withdraw() #to hide the main window

    def display(self):
        pygame.font.init() #initialize font
        self.myfont = pygame.font.SysFont('calibri', 20)
        self.screen = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("Checkers for Knowledge and Reasoning")
    def displayBoard(self,hide=[],place=None): #display board positions
        self.screen.fill(pygame.Color("black")) # erases the entire screen surface
        for boardRow in range(8):
            for boardColumn in range(8):
                xCoordinate=((0+self.width) * boardColumn + 0)+self.xDistanceFromEdge #calculate x coord
                yCoordinate=(0+self.height) * boardRow + 0 #calculate y coord
                if boardRow%2==0 and boardColumn%2==0: 
                    currentColour = self.white
                if boardRow%2!=0 and boardColumn%2==0:
                    currentColour = self.black
                if boardRow%2==0 and boardColumn%2!=0:
                    currentColour = self.black
                if boardRow%2!=0 and boardColumn%2!=0:
                    currentColour = self.white
                #draw rectangles based on colour in checkerboard shape
                if [boardRow,boardColumn] not in hide: #used for animation
                    pygame.draw.rect(self.screen,currentColour,[xCoordinate,yCoordinate, self.width, self.height])
                    cx,cy=(xCoordinate+self.mid,yCoordinate+self.mid)
                    if self.board.grid[boardRow][boardColumn] != None: #if checker piece there update position
                        self.board.grid[boardRow][boardColumn].setPosition([xCoordinate,yCoordinate, self.width, self.height])
                        colour=self.blue #define default colour
                        if self.board.grid[boardRow][boardColumn].getCrowned(): colour=(0,0,100)
                        if self.board.grid[boardRow][boardColumn].getPlayer()==1:
                            colour=self.red #set colour if other player
                            if self.board.grid[boardRow][boardColumn].getCrowned(): colour=(100,0,0)
                        if self.board.grid[boardRow][boardColumn].getSelected():
                            colour=self.green
                        pygame.draw.circle(self.screen,colour,(cx,cy),self.radius) #draw checker
                    if [boardRow,boardColumn]==place:
                        colour=self.green
                        pygame.draw.circle(self.screen,colour,(cx,cy),self.radius) #draw checker
        if len(self.selected)>0:
            for cord in self.selected:
                xCoordinate=cord[0]
                yCoordinate=cord[1]
                pygame.draw.rect(self.screen,self.green,[xCoordinate,yCoordinate, self.width, self.height])
        textsurface = self.myfont.render("HELP", False, (255, 255, 255))
        self.screen.blit(textsurface,[self.windowSize[0]-self.width,self.windowSize[1]-self.height])
    def getGrid(self,pos):
        #get the index of the grid based off of coordinates the user has clicked
        #@param pos containing the coordinates of the pixels pressed
        foundIndex=[-1,-1]
        for boardRow in range(8):
            for boardColumn in range(8):
                xCoordinate=((0+self.width) * boardColumn + 0)+self.xDistanceFromEdge
                yCoordinate=(0+self.height) * boardRow + 0
                if yCoordinate<pos[1] and pos[1]<yCoordinate+self.width:
                    foundIndex[0]=boardRow
                if xCoordinate<pos[0] and pos[0]<xCoordinate+self.height:
                    foundIndex[1]=boardColumn
        return foundIndex #return the grid index
    def getSquare(self,poses):
        #use the position to get the corner coordinates
        #@param poses which contains the grid coordinates
        coords=[] #get coord of each position 
        for pos in poses: #get each position and check it works
            xCoordinate=((0+self.width) * pos[1] + 0)+self.xDistanceFromEdge
            yCoordinate=(0+self.height) * pos[0] + 0 #calculate y coord
            coords.append([xCoordinate,yCoordinate])
        return coords
    def mainLoop(self,difficulty=2):
        #main game loop called upon
        AI_player=AI(difficulty)
        self.__init__() #reset game board
        self.display()
        self.displayBoard() #display the empty board
        pygame.display.flip()
        done=False
        currentPlayer=2
        toggled=None
        scoresT=[]
        focusToggle=[]
        helpButton=[self.windowSize[0]-self.width,self.windowSize[1]-self.height]
        while not done: #loop through all the items
            if currentPlayer==1: #AI decision
                 if difficulty==1: #low difficulty
                    move=random.choice(AI_player.successorFunction(self.board)) #get random successors
                    self.board.getMoves(move[0])
                    self.board.movePlayer(move[0],move[1],self) #make move
                    currentPlayer=2 #switch back player
                    self.displayBoard() #display new board
            if self.board.checkForceTake(currentPlayer):
                toggled=self.board.node
                self.displayBoard() #display new board
            
            for event in pygame.event.get(): #get each event
                if event.type == pygame.QUIT: #quit if quit button pressed
                    done = True
                    textsurface = self.myfont.render("HAL: Stop Dave. Stop Dave. I am afraid. I am afraid Dave.", False, (255, 255, 255))
                    self.screen.blit(textsurface,(343,573))
                elif event.type == pygame.MOUSEBUTTONDOWN: #if mouse is clicked
                    pos = pygame.mouse.get_pos()
                    grid=self.getGrid(pos) #evaluate the grid position
                    if -1 not in grid: #the selection is on the grid
                        #initiate game mechanics
                        #print(grid)
                        if (self.board.grid[grid[0]][grid[1]]!=None and self.board.grid[grid[0]][grid[1]].getPlayer()==currentPlayer
                            and (toggled==None or grid==toggled or  (type(toggled)==type([]) and grid in toggled))):
                            self.board.grid[grid[0]][grid[1]].toggleSelected()
                            x,y=self.board.grid[grid[0]][grid[1]].getCoord()
                            cx,cy=(x+self.mid,y+self.mid)
                            moves=self.board.getMoves(grid) #get the moves that the player can take
                            scoresT=moves
                            self.selected=self.getSquare(moves) #get the coordinates in pixels
                            toggled=grid
                            focusToggle=grid
                            if not(self.board.grid[grid[0]][grid[1]].getSelected()): #click again to turn off
                                self.displayBoard() #wipe board and show positions
                                scoresT=[] #reset scores
                                toggled=None #reset toggeled
                                focusToggle=None
                                self.selected=[]
                            self.displayBoard() #display new board
                        elif grid in scoresT: #selected an item within possible moves
                            #move piece to position
                            deselect=copy.deepcopy(toggled)
                            deselect.remove(focusToggle)
                            for tog in deselect:
                                self.board.grid[tog[0]][tog[1]].toggle=False #set toggle off
                            toggled=focusToggle
                            self.board.grid[toggled[0]][toggled[1]].toggleSelected()
                            
                            scoresT=self.board.getMoves(toggled)
                            self.board.movePlayer(toggled,grid,self)
                            scoresT=[] #wipe the stored values
                            toggled=None
                            focusToggle=None
                            self.selected=[]
                            if currentPlayer==2: currentPlayer=1#set new player
                            else: currentPlayer=2
                            self.displayBoard() #display new board
                        else:
                            self.displayBoard() #display new board
                            textsurface = self.myfont.render("HAL: I'm sorry, Dave. I'm afraid I can't do that.", False, (255, 255, 255))
                            self.screen.blit(textsurface,(343,573))
                            textsurface = self.myfont.render("You pressed a piece/position that cannot move", False, (255, 255, 255))
                            self.screen.blit(textsurface,(343,593))
                    elif pos[0]>=helpButton[0] and pos[0]<self.windowSize[0] and pos[1]>=helpButton[1] and pos[1]<self.windowSize[1]:
                        #help button activated in cornor
                        messagebox.showinfo('Help','OK',parent=self.screen)
                    else: #incorrect move
                        self.displayBoard() #display new board
                        textsurface = self.myfont.render("HAL: Just what do you think you're doing, Dave?", False, (255, 255, 255))
                        self.screen.blit(textsurface,(343,573))
                        textsurface = self.myfont.render("You pressed outside the board", False, (255, 255, 255))
                        self.screen.blit(textsurface,(343,593))
                if toggled != None: #keep toggled up
                    colour=(0,255,0) #green for possible
                    if type(toggled[0])!=type([]): toggled=[toggled]
                    tt=self.getSquare(toggled)
                    for t in tt:
                        pygame.draw.circle(self.screen,colour,(t[0]+self.mid,t[1]+self.mid),self.radius) #colour toggled

                #check whether or not there is a win
                gamestate=self.board.getWinDrawLose()
                if gamestate!=[0,0,0]: #check whether the game needs to end
                    done=True
                    pygame.display.flip()
                    if gamestate==[1,0,0]: #player loses
                        textsurface = self.myfont.render("HAL: You lose. I'm sorry, Frank, I think you missed it.", False, (255, 255, 255))
                    elif gamestate==[0,0,1]: #player wins
                        textsurface = self.myfont.render("HAL: You win. Thank you for a very enjoyable game.", False, (255, 255, 255))
                    else: #draw
                        textsurface = self.myfont.render("HAL: Its a draw!", False, (255, 255, 255))

                    self.screen.blit(textsurface,(343,573))
                pygame.display.flip()
        time.sleep(2) #leave 2 seconds to
        self.exit()
    def menu(self):
        self.display()
        done=False
        currentDifficulty="easy"
        start = int(self.windowSize[1]/3)
        x=start
        y=100
        x1=start*2
        x2=start*3
        
        while not done: #loop through all the items
            textsurface = self.myfont.render("Select a difficulty:", False, (255, 255, 255))
            self.screen.blit(textsurface,(int(self.windowSize[1]/2)+80,50))
            textsurface = self.myfont.render("The harder the difficulty, the more intelligent the AI is ", False, (255, 255, 255))
            self.screen.blit(textsurface,(int(self.windowSize[1]/2)-60,200))
            pygame.draw.rect(self.screen,self.green,[x,y, self.width, self.height])
            pygame.draw.rect(self.screen,self.yellow,[x1,y, self.width, self.height])
            pygame.draw.rect(self.screen,self.red,[x2,y, self.width, self.height])
            pygame.display.flip()
            for event in pygame.event.get(): #get each event
                if event.type == pygame.QUIT: #quit if quit button pressed
                    done = True
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN: #if mouse is clicked
                    pos = pygame.mouse.get_pos()
                    if pos[1]>=y and pos[1]<=y+self.height:
                        if pos[0]>=x and pos[0]<=x+self.width:
                            self.mainLoop(difficulty=1) #start game on easy
                            done = True
                        elif pos[0]>=x1 and pos[0]<=x1+self.width:
                            self.mainLoop(difficulty=2) #start game on medium
                            done = True
                        elif pos[0]>=x2 and pos[0]<=x2+self.width:
                            self.mainLoop(difficulty=3) #start game on hard
                            done = True

    def exit(self):
        textsurface = self.myfont.render("HAL: Goodbye", False, (255, 255, 255))
        print("Goodbye!")
        pygame.quit()


game=main()
game.menu()


#TODO
"""
display rules
"""


