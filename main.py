'''
    Created by Saurabh Kumar

    The main game logic
    This file implements the Minimax logic

    The game is automated for a specific online version of the game 
    hosted a https://playc4.com/.
    The game uses selenium webdriver for autmomation and automatically 
    opens a browser with the above link. from that point on the user needs
    the copy the given link and open it in a new tab.

    Due the deisgn of this code, the bot works only as first player.

    TODO: Make the bot quit once the game is over
'''

import Game
from selenium import webdriver
import random
import time

gameStateManager = Game.Game()   
states = {}


'''
    Automated procedure for checking if the opponent has made a move
    and finding out the position of that move.  
'''
def GetBoardConfiguration (browser):
    move = 0
    for i in range(1, 8):
        if gameStateManager.GetHeight(i) > 0:
            path = '//body/div[2]/div[{}]/div[{}]'.format(gameStateManager.GetHeight(i), i)
            b = browser.find_element_by_xpath(path)
            st = b.get_attribute('class').split()[-1]
            if st == 'blue':
                move = i
                gameStateManager.ModifyBoard(move, 2)
                break
    return move

'''
    main driver function for Minimax, 
    In order to speed up the search the following methods are used
    1. alpha beta pruning
    2. transpositon table

    TODO: improve performance further
'''
def min_max (depth):
    global states
    v = float('-inf')

    a = float('-inf')
    b = float('inf')

    action = -1

    for move in gameStateManager.GetMoves():
        if gameStateManager.ModifyBoard(move, 1):
            tmp = min_value(a, b, move, depth)
            gameStateManager.UndoBoard(move)
            if tmp > v:
                v = tmp
                action = move
            if v >= b:   
                print (test)
                return action
            a = max(a, v)
    states = {}
    return action 

def max_value(a, b, oponentMove, depth = 0):
    global states

    hashValue = gameStateManager.GenerateHash()
    if hashValue in states:
        return states[hashValue]

    hasWon = gameStateManager.CheckForC4(2, oponentMove)

    if hasWon == True or depth == 0:
        u = gameStateManager.Utility(2, hasWon)
        states[hashValue] = u
        return u

    v = float('-inf')
    for move in gameStateManager.GetMoves():
        if gameStateManager.ModifyBoard(move, 1):
            v = max(v, min_value(a, b, move, depth))
            gameStateManager.UndoBoard(move)
            if v >= b:   
                states[hashValue] = v
                return v
            a = max(a, v)
    states[hashValue] = v
    return v

def min_value(a, b, oponentMove, depth = 0):
    global states

    hashValue = gameStateManager.GenerateHash()
    if hashValue in states:
        return states[hashValue]

    hasWon = gameStateManager.CheckForC4(1, oponentMove)
    if hasWon == True or depth == 0:
        u = gameStateManager.Utility(1, hasWon)
        states[hashValue] = u
        return u

    v = float('inf')
    for move in gameStateManager.GetMoves():
        if gameStateManager.ModifyBoard(move, 2):
            v = min(v, max_value(a, b, move, depth - 1))
            gameStateManager.UndoBoard(move)
            if v <= a:   
                states[hashValue] = v
                return v
            b = min(b, v)
    states[hashValue] = v
    return v


def main():
    browser = webdriver.Firefox()
    browser.get('https://playc4.com/')

    _ = input('Press Enter to Start the Bot')
    waitingSign = ['/', '\\']
    x = 0
    firstMove = True
    while True:
        '''
            unless its the first move, will wait until the opponent makes a move 
            and check if the the state of the board as changed or not. If the opponent
            has made a move then reflect it in the board.  
        '''
        oponentMove = 0
        if not firstMove:
            while oponentMove == 0:
                x = 1 - x
                print('waiting for enemy to move {}'.format(waitingSign[x]), end='\r')
                oponentMove = GetBoardConfiguration (browser)
                time.sleep(2)
        firstMove = False

        print('Applying Min Max to find next move')
        move = min_max(4)

        '''
            There can be cases when the game has lead to situation 
            in which no matter what move the bot takes, it will end up 
            in him losing the game. In such a state the bot will just play randomly
            until it losses.
        '''
        if move == -1:
            print ('There is no way the bot can win')
            possibleMoves = gameStateManager.GetMoves()
            move = random.choice(possibleMoves)

        print ('Move to take: ', move)
        b = browser.find_element_by_xpath('//body/div[2]/div[1]/div[{}]'.format(move))
        b.click()
        gameStateManager.ModifyBoard(move, 1)
        print (gameStateManager.height)

        print ('-' * 10)
        board = gameStateManager.GetBoard()
        print ('Board Configuration')
        for i in board:
            print (i)
        print ('-' * 10)

if __name__ == '__main__':
    main()