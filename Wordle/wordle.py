# Wordle Game

import random
import pygame
import math
from sys import exit
import os

# Game Mode
file = open(os.path.join(os.path.dirname(__file__), "..\gameMode.txt"), 'r')
fileline = file.readline()

playerInput = True
if fileline[0] == "1":
    playerInput = False

file.close()

# Solver Input
if not playerInput:
    # Wordle Listener + Client
    from multiprocessing.connection import Listener
    from multiprocessing.connection import Client

    # Listener
    addressListener = ('localhost', 6000)  # family is deduced to be 'AF_INET'
    listener = Listener(addressListener, authkey=b'secret password')
    connListener = listener.accept()
    print('connection accepted from', listener.last_accepted)

    # Client
    addressClient = ('localhost', 6001)
    connClient = Client(addressClient, authkey=b'secret password')

# Window Configuration
SCR_WIDTH = 600
SCR_HEIGHT = 800

# PYGAME Configuration
pygame.init()
screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
pygame.display.set_caption("Wordle")
pygameIcon = pygame.image.load(os.path.join(os.path.dirname(__file__), "WordleIcon.png"))
pygame.display.set_icon(pygameIcon)

clock = pygame.time.Clock()

# Background color
backgroundColor = (18, 18, 19)
screen.fill(backgroundColor)

# Text
titleFont = pygame.font.Font(None, 50)
charFont = pygame.font.Font(None, 64)
textWordle = titleFont.render("Wordle", True, "White")

# Grid Configuration
squareSpace = 8
gridSpace = 3
gridSquareSize = 70
startSquareHeight = 150

# Words
words = [
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0']
]

# N = negru
# V = verde
# G = galben
# X = neutru
# R = rosu (cuvantul nu se afla in baza de date)

feedback = [
    ['X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X'],
    ['X', 'X', 'X', 'X', 'X']
]

currentRow = 0
currentColumn = 0

wrongWord = False
endGame = False
wordsCounter = 0
letterIndexBestWord = 0

enableAnimation = False
deltaAnimation = 0
startAnimation = False
direction = 1


# classes + functions
class Square:
    def __init__(self, gridSquareWidth, gridSquareHeight, row, column):
        self.gridSquareWidth = gridSquareWidth
        self.gridSquareHeight = gridSquareHeight
        self.row = row
        self.column = column

        self.fillSquareSize = gridSquareSize - gridSpace * 2
        self.fillSquareWidth = gridSquareWidth + gridSpace
        self.fillSquareHeight = gridSquareHeight + gridSpace

        self.gridColor = (129, 131, 132)
        self.squareColor = (18, 18, 19)
        self.redColor = (155, 21, 14)
        self.blackColor = (58, 58, 60)
        self.greenColor = (83, 141, 78)
        self.yellowColor = (183, 161, 72)


    def draw(self):
        color = self.gridColor
        if feedback[self.row][self.column] == 'N':
            color = self.blackColor
        elif feedback[self.row][self.column] == 'V':
            color = self.greenColor
        elif feedback[self.row][self.column] == 'G':
            color = self.yellowColor
        elif feedback[self.row][self.column] == 'R':
            color = self.redColor

        pygame.draw.rect(screen, color, (self.gridSquareWidth, self.gridSquareHeight, gridSquareSize, gridSquareSize))

        if feedback[self.row][self.column] == 'X':
            pygame.draw.rect(screen, self.squareColor, (self.fillSquareWidth, self.fillSquareHeight, self.fillSquareSize, self.fillSquareSize))

        if words[self.row][self.column] != '0':
            textChar = charFont.render(words[self.row][self.column], True, "White")

            textWidth = self.fillSquareWidth + self.fillSquareSize // 2 - textChar.get_width() // 2
            textHeight = self.fillSquareHeight + self.fillSquareSize // 2 - textChar.get_height() // 2

            screen.blit(textChar, (textWidth, textHeight))


class Grid:
    def draw(self):
        for row in range(6):
            # mid square
            midSquareWidth = SCR_WIDTH // 2 - gridSquareSize // 2
            midSquareHeight = startSquareHeight + row * squareSpace + row * gridSquareSize

            for i in range(-2, 3):
                squareWidth = midSquareWidth + i * squareSpace + i * gridSquareSize
                squareHeight = midSquareHeight
                column = i + 2
                if row == currentRow:
                    squareWidth -= animationFunction(deltaAnimation)
                square = Square(squareWidth, squareHeight, row, column)
                square.draw()


def animationFunction(time):
    global direction

    if time != 0:
        return direction * 3 / math.sqrt(time)
    else:
        return 0

def wordFeedback():
    global endGame
    global hiddenWord
    
    for i in range(5):
        if hiddenWord[i] == words[currentRow][i]:
            feedback[currentRow][i] = 'V'
        else:
            for j in range(5):
                if hiddenWord[j] == words[currentRow][i]:
                    feedback[currentRow][i] = 'G'
                    break
            else:
                feedback[currentRow][i] = 'N'
    if hiddenWord == "".join(words[currentRow]):
        endGame = True


def checkInput(eventToHandle):
    global currentRow
    global currentColumn
    global endGame
    global wrongWord
    global enableAnimation
    global startAnimation

    if eventToHandle.type == pygame.KEYDOWN:
        if pygame.K_a <= eventToHandle.key <= pygame.K_z:
            if currentColumn < 5:
                words[currentRow][currentColumn] = pygame.key.name(eventToHandle.key).upper()
                currentColumn += 1
        elif eventToHandle.key == pygame.K_BACKSPACE:
            currentColumn = max(currentColumn - 1, 0)
            words[currentRow][currentColumn] = '0'
            if wrongWord == True:
                wrongWord = False
                for i in range(5):
                    feedback[currentRow][i] = 'X'
        elif eventToHandle.key == pygame.K_RETURN or eventToHandle.key == pygame.K_KP_ENTER:
            if currentColumn == 5:
                checkWord()
                if startAnimation:
                    # the animation will start again from the beginning
                    startAnimation = False
                enableAnimation = True
            else:
                print("Word is not valid")

def checkWord():
    global currentRow
    global currentColumn
    global endGame
    global wordsCounter
    global wrongWord
    global playerInput

    if playerInput:
        currentWord = ""
        for i in range(5):
            currentWord += words[currentRow][i]

        if checkDataBase(currentWord):
            wordFeedback()

            wordsCounter += 1
            currentRow += 1
            currentColumn = 0

        else:
            print("Word isn't in database")
            wrongWord = True
            for i in range(5):
                feedback[currentRow][i] = 'R'
    else:
        wordFeedback()
        wordsCounter += 1
        currentRow += 1
        currentColumn = 0

    if currentRow == 6:
        # Move words[][] + feedback[][]
        for r in range(5):
            words[r] = words[r + 1].copy()
            feedback[r] = feedback[r + 1].copy()

        currentRow = 5
        currentColumn = 0
        for c in range(5):
            words[5][c] = '0'
            feedback[5][c] = 'X'


def checkDataBase(word): 
    global database

    for w in database:
        if w == word:
            return True
    return False


def sendFeedback(clientMsg):
    print("Send to solver : " + clientMsg)
    connClient.send(clientMsg)


listenerMsg = ''
def receiveBestWord():
    global listenerMsg

    if listenerMsg != "exit":
        listenerMsg = connListener.recv()
        print("From solver : ", listenerMsg)

    return listenerMsg


def closeConnection():
    connClient.close()
    connListener.close()
    listener.close()

def newWord():
    global endGame
    global hiddenWord
    global currentColumn
    global currentRow
    global letterIndexBestWord
    global wordsCounter

    endGame = False

    # Choose a random word
    hiddenWord = random.choice(database)

    for row in range(6):
        for column in range(5):
            feedback[row][column] = 'X'
            words[row][column] = '0'
    currentColumn = currentRow = 0
    indexSolver = 0
    wordsCounter = 0
    print("New hidden word : ", hiddenWord)


if __name__ == '__main__':

    # Database
    database = []
    file = open(os.path.join(os.path.dirname(__file__), "../database.txt"), 'r')
    fileline = file.readline()
    while fileline:
        fileline = fileline[:-1]
        database.append(fileline)
        fileline = file.readline()
    file.close()

    # Choose a random word
    hiddenWord = random.choice(database)
    print("Hidden word : ", hiddenWord)

    # Timer
    getTicksLastFrame = 0
    checkForInputTimer = 0.7 
    timer = 0

    # Animation
    animationTime = 2.0
    startAnimation = False

    while True:
        # deltaTime in seconds
        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t

        canReadWrite = False
        if timer > checkForInputTimer:
            timer = 0
            canReadWrite = True
        else:
            timer += deltaTime

        # Check Input
        for event in pygame.event.get():
            # check exit
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # check keyboard input
            if playerInput and (not endGame):
                checkInput(event)

            if endGame and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    newWord()

        # Solver Input
        if (not endGame) and (not playerInput) and canReadWrite:
            if letterIndexBestWord == 0:
                #Listener first
                bestWord = receiveBestWord()

            words[currentRow][letterIndexBestWord] = bestWord[letterIndexBestWord]
            if letterIndexBestWord == 4: # all the letters have been displayed
                checkWord()
                letterIndexBestWord = 0

                #Client second

                fb = ""
                for i in range(5):
                    fb += feedback[currentRow - 1][i]
                sendFeedback(fb)
            else:
                letterIndexBestWord += 1

        # Animation settings
        if startAnimation == False and wrongWord and enableAnimation:
            start_t = pygame.time.get_ticks() # time when the animation starts
            startAnimation = True
            deltaAnimation = 0

        if startAnimation == True:
            if wrongWord == False or deltaAnimation > animationTime:
                # stop the animation
                startAnimation = False
                enableAnimation = False
                deltaAnimation = 0
            else:
                # continue the animation
                deltaAnimation = (pygame.time.get_ticks() - start_t) / 1000
                direction *= -1
        
        # draw interface
        textWidth = SCR_WIDTH // 2 - textWordle.get_width() // 2
        screen.blit(textWordle, (textWidth, 50))

        # draw grid + characters
        grid = Grid()
        grid.draw()

        # draw winner
        if endGame:
            textResult = titleFont.render("WINNER", True, "Green")
            textWidth = SCR_WIDTH // 2 - textResult.get_width() // 2
            screen.blit(textResult, (textWidth, 100))

        # draw words counter
        textCounter = titleFont.render("Counter : " + str(wordsCounter), True, "White")
        textWidth = SCR_WIDTH // 2 - textCounter.get_width() // 2
        screen.blit(textCounter, (textWidth, 660))
        
        # refresh
        pygame.display.update()
        clock.tick(60)
        screen.fill(backgroundColor)

if not playerInput:
    closeConnection()

