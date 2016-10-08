# AI Bot for playing Connect 4

Connect Four is a two-player connection game in which the players first choose a color and then take turns dropping colored discs from the top into a seven-column, six-row vertically-suspended grid. The pieces fall straight down, occupying the next available space within the column. The objective of the game is to connect four of one's own discs of the same color next to each other vertically, horizontally, or diagonally before your opponent. Connect Four is a strongly solved game. The first player can always win by playing the right moves.

## Getting Started

The project is hosted on Github, there are a number of ways to download it:
* Clone the git repository via https, ssh or with the Github Windows or Mac clients.
* Download as zip or tar.gz

### Prerequisities

The project requires the following things before you can play the game:
* FireFox web browser version < 48
* Python version > 3
* Selenium for python
* A working internet connection, as the game is hosted online

### Installing

You can download FireFox from the official website at [Download FireFox](https://www.mozilla.org/en-US/firefox/new/)

If you are using Linux or Mac OS then you don't need to do anything to install python, you can simply use the interpreter by opening the terminal and typing the command.

```
python3 main.py
```

For windows systems, the steps are a bit more complex. You can use this guide in order to properly setup python on you windows desktop [How to Install Python on Windows](http://www.howtogeek.com/197947/how-to-install-python-on-windows/). Remember that you need to install a version > 3 for this project.

Before you can actually start playing against the bot you first need to install Selenium which is a browser automation tool for python. You may consider creating a virtual environment first to isolate the installation.

```
pip3 install -U selenium
```

Before you move on to the next step I recommend that you test if selenium has been properly installed on your system. To do that open the python interpreter and run the following code.

```
$python3
>>from selenium import webdriver

>>browser = webdriver.Firefox()
>>browser.get('http://google.com/')
```

If the code successfully opens a new FireFox window and navigates to the requested link, then you are all set and ready for starting your match against the bot!

## Running the game

In order to simplify the coding process and devote more time to actually learning and implementing the AI for the bot, I decided that I won't be making the interface for the game myself. Instead, I have used an open, freely available version of connect 4 hosted online at [Play Connect 4](https://www.playc4.com/). In order to have a 2 player game, you need to copy the link given at the right side and paste in another browser tab. This allows you to send the link to another friend sitting in another corner of the world and have them lose against the bot :).

To run the game navigate to the directory where the code is present and type the command:
```
python3 main.py
```

This will open a new Firefox window and the link mentioned above will automatically open as one of the tabs.

You will notice in the terminal the bot says:
```
Press Enter to Start the Bot
```
Before you do that you need to copy the link to the second player and open it in a new tab. Wait for the page to load and then press start game. Doing so will initialize the second player allowing the bot to make its move. Go to the terminal and press Enter.

The bot is designed to only play as the first player (sorry about that). Once it has made its move you can go to the tab of the second player and make your move. The bot is smart enough to detect the move that you have made and once it does that it will make its move, you don't need to switch tabs or even look at the terminal (it does show some useful info).


## How does the bot work

Keeping aside the automation done by Selenium, The bot primarily works on the MiniMax algorithm. 

From Wikipedia: "Minimax (sometimes MinMax or MM) is a decision rule used in decision theory, game theory, statistics and philosophy for minimizing the possible loss for a worst case (maximum loss) scenario. Alternatively, it can be thought of as maximizing the minimum gain (maximin or MaxMin). Originally formulated for two-player zero-sum game theory, covering both the cases where players take alternate moves and those where they make simultaneous moves, it has also been extended to more complex games and to general decision making in the presence of uncertainty."

I am not going to go into how I have implemented it as it is a simple and straightforward algorithm and would be better explained by a course directed towards AI. Instead, I will discuss how I optimized it for my implementation and the design of the Utility function used to evaluate board states.

### Search optimizations
To give you a little background, using just pure minimax the bot is only able to go only unto a depth of 2 moves (7^4 nodes at leaves since 1 move is equal to 2 levels in the tree). Going above that slows heavily slows down the bot and response that take several minutes.

#### Alpha Beta pruning
A simple optimization technique used with minimax that cuts off further evaluation of a node once it has determined that its relative magnitude will not change. Pruning with Alpha Beta depends a lot on the ordering of the nodes, as of now I have not implemented any form of ordering but I do plan on doing that in the near future.

#### Transposition Table
If you were to draw the tree constructed while minimax search you will find that there is a very small portion (less than 5%) of board states are actually unique. This means that if store the value of an evaluated board state then we will effectively be pruning a massive portion of the tree. 
This is implemented by converting the board state into a 42 character long string and using that as a unique key value in a python dictionary with the board's utility as the value. After the minimax has done its calculation the current transposition table is dropped.

By implementing these to optimizations together the algorithm is able to easily reach up to a depth of 4 (evaluating and pruning over 500 million nodes). It's possible to go up to a depth 5 and get a response in reasonable time but doing that results in an abnormally large transposition table, effectively slowing down the bot since the system will be low in memory.

### Evaluating Board states

A major part of Minimax is how well you evaluate board states. For this project, the evaluation function at the moment depends on how many threats are present on that board state. To be specific the utility of each board is simple
```
Linear function of player 1's threat - Linear function of player 2's threat
```
now the linear function means that for each threat a constant value is multiples with it to distinguish it from other threats.
For instance, an odd threat of player 1 is a lot better than an odd threat of player 2, so we will multiply a higher constant to the threat count of player 1.

The way threats are counted is quite simple. Its is based on the logic that if you treat a blank spot (no player has a coin there) as a player and check if he has performed a connect 4 relatives to that spot than the player has a threat at that spot.
Now we know that threats can only occur at the boundary formed by the occupied slots, so the algorithm first finds this boundary and then calculates the threats that each user has relative to these points.

For example, if the board looks like this
```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0 
0 0 2 0 0 0 0
0 0 1 2 0 0 0
0 1 1 1 2 0 0
```

Then the boundry will be
```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 X X X 0 0 0 
0 X 2 X 0 0 0
X X 1 2 X X 0
X 1 1 1 2 X X
```
Now the algorithm will iterate over each of these boundry points and perform a directed recursive search to count how many coins of the player are connected across all diagonals.

So if we were to count the threats for player 2 at point [0, 2] (consider it to a 2D matrix) the the search would go something like this:

First find all the coins of the player in points 8 neighborhood.
```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 X 0 0 0 0 0 
0 0 2 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
```
Now iterate over each of these neighbors and then recursively procede in the same direction as it took to reach to the neighbor
```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 X 0 0 0 0 0 
0 0 2 0 0 0 0
0 0 0 2 0 0 0
0 0 0 0 0 0 0

0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 X 0 0 0 0 0 
0 0 2 0 0 0 0
0 0 0 2 0 0 0
0 0 0 0 2 0 0
```

This will happen across all half diagonal, so we can just add the result of 2 half diagonals in order to get the total connected discs across the entire diagonal, and a connect 4 is a threat in that case. So This way a simple algorithm for checking for connect 4 works amazing well for finding open threats on the board as well.

## Built With

* Python
* Selenium 

## Contributing

The code is open for anyone to copy and modify. Feel free to use it as a base for you own projects. I have tried to make the code as modular as possible so that adding new features is easy.
 

## Authors

* [**Saurabh Kumar**](https://github.com/saurabh-kumar-vit)

