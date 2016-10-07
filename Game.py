'''
    Created By Saurabh Kumar

    This is the Game manager class of the bot.
    Its supposed to manage the various operations that the 
    MiniMax algo may make, like modifying the board or calculating
    the utility of the given state. 
'''

class Game:
    def __init__ (self):
        self.height = [6 for _ in range(9)] # The array is padding on both ends to ease utility calculation
        self.board = [[0 for _ in range(7)]  for _ in range(6)]

        # we need these in order to know in which direction should we traverse during CheckForC4
        self.positon = {
            (-1, -1): 0,
            (-1, 0): 1,
            (-1, 1): 2,
            (0, -1): 3,
            (0, 1): 4,
            (1, -1): 5,
            (1, 0): 6,
            (1, 1): 7
        }

        self.inv_position = {
            0: (-1, -1),
            1: (-1, 0),
            2: (-1, 1),
            3: (0, -1),
            4: (0, 1),
            5: (1, -1),
            6: (1, 0),
            7: (1, 1) 
        }

    def GetMoves (self):
        moves = []
        for j, i in enumerate(self.height):
            if i > 0 and (j != 0 and j != 8):
                moves.append(j)
        return moves

    def GetHeight (self, index):
        return self.height[index]

    def GetBoard (self):
        return self.board

    '''
        TODO: Need to test these 3 functions for consistency
                1. ModifyHeight
                2. ModifyBoard
                3. UndoBoard

        funcitons used to improve robustness of program,
        deny invalid modifying of height or board
    '''
    def ModifyHeight (self, index, delta):
        if (self.height[index] + delta) >= 0 and (self.height[index] + delta) <= 6:
            self.height[index] += delta
            return True
        return False

    ''' 
        They way we are traversing in the MiniMax tree is first commiting 
        a move in the board, and after it has been evaluated we undo the 
        board. Doing this saves a lot of memeory allowing us to deepen the 
        search further.
    '''
    def ModifyBoard (self, move, item):
        if self.ModifyHeight(move, -1):
            self.board[self.height[move]][move - 1] = item
            return True
        return False

    def UndoBoard (self, move):
        if self.ModifyHeight(move, 1):
            self.board[self.height[move] - 1][move - 1] = 0
            return True
        return False

    '''
        In case ModifyBoard and UndoBoard are not functioning properly 
        then use these functions instead. They are less robust but are correct
    '''
    # def SimpleModifyBoard (self, move, item):
    #     if self.height[move] - 1 >= 0:
    #         self.board[self.height[move] - 1][move - 1] = item
    #         self.height[move] -= 1
    #         return True
    #     return False
    # def SimpleUndoBoard (self, move):
    #     self.height[move] += 1
    #     self.board[self.height[move] - 1][move - 1] = 0

    '''
        in order to store the utility of calculated board states in transpostion table 
        we use this to generate a unique hash value for each board state
    '''
    def GenerateHash (self):
        hashValue = ''
        for row in self.board:
            for ele in row:
                hashValue += str(ele)
        return hashValue

    '''
        Checks if the player has won given his latest move
        if the current position corresponds to an empty slot (0), 
        this this function will act as if it is counting threats
        associated with that slot for the player.
    '''
    def CheckForC4 (self, player, move, countthreats = False):
        connection = [1 for _ in range(8)]

        m, n = self.height[move], move - 1
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0) and (m + i >= 0 and m + i < 6) and (n + j >= 0 and n + j < 7):
                    self.Search(m + i, n + j, self.positon[(i, j)], connection, player)
        
        '''
            find the total number connections across each diagonal
            a value greater than 4 means that there are atleast 4 discs
            of same color across that diagonal         
        '''
        pos_diagnol = connection[0] + connection[7]
        neg_diagnol = connection[2] + connection[5]
        horzontal = connection[3] + connection[4]
        vertical = connection[1] + connection[6]

        connectionValue = [pos_diagnol, neg_diagnol, horzontal, vertical]

        threats = 0
        hasWon = False

        for value in connectionValue:
            if value > 4:
                threats += 1
                hasWon = True

        if countthreats:    return threats
        return hasWon

    '''
        Support function for CheckForC4, It recursively traverses 
        across a diagonal until it can no longer move forward, used to
        find total no of player's discs in that diagonal
    ''' 
    def Search(self, i, j, pos, connection, player):
        if self.board[i][j] == player:
            connection[pos] += 1
            m, n = self.inv_position[pos]
            if (i + m >= 0 and i + m < 6) and (j + n >= 0 and j + n < 7):
                self.Search(i + m, j + n, pos, connection, player)

    '''
        Calculate the utility of the current board positon.

        TODO: improve utility as the bot has a hard time evaluating early board states
    '''
    def Utility(self, player, hasWon):
        if hasWon:
            return float('-inf') if (player == 2) else float('inf')
 
        playerOneUtil = 0
        playerTwoUtil = 0
        '''
            in the CheckForC4 function, if the move passed in the parameter
            actually corresponds to a blank (0) then the function acts as if 
            it counting threats corresponding to that blank space.

            the code bellow traces the boundry of blank slots around the occupied slots,
            and Calculates the threats for both players at that slot.

            The utility is computed  
        '''
        for i in range(1, 8):
            balanceHeight = min(self.height[i-1], self.height[i+1])
            if self.height[i] >= balanceHeight:
                k = self.height[i] - balanceHeight + 1                  
                for j in range(1, k+1):
                    if self.ModifyHeight(i, -j):
                        util1 = self.CheckForC4(1, i, countthreats = True)
                        util2 = self.CheckForC4(2, i, countthreats = True)
                        playerOneUtil += (5 * util1 if self.height[i] % 2 != 0 else 3 * util1)
                        playerTwoUtil += (3 * util2 if self.height[i] % 2 == 0 else 2 * util2)
                        self.ModifyHeight(i, j)

            else:
                if self.ModifyHeight(i, -1):
                    util1 = self.CheckForC4(1, i, countthreats = True)
                    util2 = self.CheckForC4(2, i, countthreats = True)
                    playerOneUtil += (5 * util1 if self.height[i] % 2 != 0 else 3 * util1)
                    playerTwoUtil += (3 * util2 if self.height[i] % 2 == 0 else 2 * util2)
                    self.ModifyHeight(i, 1)

        return playerOneUtil - playerTwoUtil

