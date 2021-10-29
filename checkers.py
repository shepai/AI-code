"""
Checkers code by Dexter Shepherd, aged 20

"""


import pygame
import copy
import time

class AI_agent:
    """
    AI player which uses a mini max algorithm to find the best option through a game

    @param difficulty that the AI will play at
    """
    def __init__(self,difficulty):
        self.difficulty=difficulty
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

        print("end")
        return coords #return the collected coords
    def movePlayer(self,pos,end):
        if self.grid[pos[0]][pos[1]]==None: #assertion
            raise TypeError("Cannot move what is not there")
        x=pos[0]
        y=pos[1]
        #pos=copy.deepcopy(self.grid[x][y])
        #print(pos,end)
        if (abs(end[0])-abs(pos[0])>=2 or abs(end[0])-abs(pos[0])<=-2 or
            abs(end[1])-abs(pos[1])>=2 or abs(end[1])-abs(pos[1])<=-2): #players have been taken
            #print("taken",end,self.routes)
            key=str(end)
            things=[]
            while things!=None: #follow the route of taking players
                things=self.routes.get(key,None)
                if things!=None:
                    for thing in things: #loop through each piece and delete
                        for k in thing:
                            #print("remove",thing[k])
                            self.grid[thing[k][0]][thing[k][1]]=None
                            key=k
        #switch the positions of new and old
        pos=copy.deepcopy(self.grid[x][y])
        self.grid[x][y]=None #rewrite
        self.grid[end[0]][end[1]]=copy.deepcopy(pos) 
        if end[0]==0 and self.grid[end[0]][end[1]].getPlayer()==2: #made it to end
            self.grid[end[0]][end[1]].crown()
        if end[0]==7 and self.grid[end[0]][end[1]].getPlayer()==1: #made it to end
            self.grid[end[0]][end[1]].crown()
        

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
        self.greyBackground =(203, 206, 203)
        self.blue=(0,0,255)
        #define window size
        self.windowSize=[960, 640]
        self.xDistanceFromEdge=220
    def display(self):
        pygame.font.init() #initialize font
        self.myfont = pygame.font.SysFont('Comic Sans MS', 15)
        self.screen = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("Checkers for Knowledge and Reasoning")
    def displayBoard(self): #display board positions
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
                pygame.draw.rect(self.screen,currentColour,[xCoordinate,yCoordinate, self.width, self.height])
                if self.board.grid[boardRow][boardColumn] != None: #if checker piece there update position
                    self.board.grid[boardRow][boardColumn].setPosition([xCoordinate,yCoordinate, self.width, self.height])
                    cx,cy=(xCoordinate+self.mid,yCoordinate+self.mid)
                    colour=self.blue #define default colour
                    if self.board.grid[boardRow][boardColumn].getCrowned(): colour=(0,0,100)
                    if self.board.grid[boardRow][boardColumn].getPlayer()==1:
                        colour=self.red #set colour if other player
                        if self.board.grid[boardRow][boardColumn].getCrowned(): colour=(100,0,0)
                    pygame.draw.circle(self.screen,colour,(cx,cy),self.radius) #draw checker
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
    def mainLoop(self):
        #main game loop called upon
        self.__init__() #reset game board
        self.display()
        self.displayBoard() #display the empty board
        pygame.display.flip()
        done=False
        currentPlayer=2
        toggled=None
        scoresT=[]
        while not done: #loop through all the items
            for event in pygame.event.get(): #get each event
                if event.type == pygame.QUIT: #quit if quit button pressed
                    done = True
                elif event.type == pygame.MOUSEBUTTONDOWN: #if mouse is clicked
                    pos = pygame.mouse.get_pos()
                    grid=self.getGrid(pos) #evaluate the grid position
                    if -1 not in grid: #the selection is on the grid
                        #initiate game mechanics
                        #print(grid)
                        if (self.board.grid[grid[0]][grid[1]]!=None and self.board.grid[grid[0]][grid[1]].getPlayer()==currentPlayer
                            and (toggled==None or grid==toggled)):
                            self.board.grid[grid[0]][grid[1]].toggleSelected()
                            x,y=self.board.grid[grid[0]][grid[1]].getCoord()
                            cx,cy=(x+self.mid,y+self.mid)
                            if self.board.grid[grid[0]][grid[1]].getSelected():
                                colour=(0,255,0) #green for possible
                                pygame.draw.circle(self.screen,colour,(cx,cy),self.radius) #colour toggled
                                toggled=grid
                                moves=self.board.getMoves(grid) #get the moves that the player can take
                                scoresT=moves
                                t=self.getSquare(moves) #get the coordinates in pixels
                                for move in t:
                                    xCoordinate=move[0]
                                    yCoordinate=move[1]
                                    pygame.draw.rect(self.screen,colour,[xCoordinate,yCoordinate, self.width, self.height])
                            else: #click again to turn off
                                self.displayBoard() #wipe board and show positions
                                scoresT=[] #reset scores
                                toggled=None #reset toggeled
                        elif grid in scoresT: #selected an item within possible moves
                            #move piece to position
                            self.board.grid[toggled[0]][toggled[1]].toggleSelected()
                            
                            self.board.movePlayer(toggled,grid)
                            self.displayBoard() #display new board
                            scoresT=[] #wipe the stored values
                            toggled=None
                            if currentPlayer==2: currentPlayer=1#set new player
                            else: currentPlayer=2
                        else:
                            self.displayBoard() #display new board
                            textsurface = self.myfont.render("HAL: I'm sorry, Dave. I'm afraid I can't do that.", False, (255, 255, 255))
                            self.screen.blit(textsurface,(343,573))
                    else: #incorrect move
                        self.displayBoard() #display new board
                        textsurface = self.myfont.render("HAL: Just what do you think you're doing, Dave?", False, (255, 255, 255))
                        self.screen.blit(textsurface,(343,573))
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
        time.sleep(5) #leave 5 seconds to
        self.exit()
    def exit(self):
        textsurface = self.myfont.render("HAL: Goodbye", False, (255, 255, 255))
        print("Goodbye!")
        pygame.quit()


#HAL quotes
#I'm sorry, Frank, I think you missed it.
#Thank you for a very enjoyable game.
#Just what do you think you're doing, Dave?

game=main()
game.mainLoop()



