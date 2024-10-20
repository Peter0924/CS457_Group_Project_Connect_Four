# Sprint 1 Overview

This is a simple implementation of a server-client application using Python. The server can handle multiple client connections simultaneously, and both the server and clients can exchange messages.

## How to run

1. **Start the Server** 
   - Run `python server.py`

2. **Start the Client** 
   - Run `python client.py`

3. **Message exchange** 
   - Type any message in client terminal and press enter, the server should print out the message and echo it back to the client.

4. **Shutdonw the Server** 
   - Type `shutdown` or `CTRL + C` to shut down the server

5. **Shutdown the Client** 
   - Type `exit` to shut down the client

## Test Instructions

1. **Create a virtual environment to isolate our project's dependencies** 
   - `python -m venv venv`

2. **Activate Virtual Environment** 
   - Run the `venv/Scripts/activate`

3. **Start the Server** 
   - Start the another new terminal and run `python server.py`

4. **Run the Test** 
   - Go back to the terminal where we activate the virtual environment
   - Run the test by using `pytest test.py`
   

# Connect Four Game with Chat Feature

This is a **Connect Four** game implemented using Python, enhanced with a built-in chat feature. Players can enjoy the classic game while chatting with each other in real time during gameplay.

## How to play:
1. **Start the game:** Run the `connect_four_server.py` script to start the server, then run the `connect_four_client.py` script on two different machines or terminals to connect as players.

2. **Game setup:** The game starts with an empty 6x7 grid. Two players alternate turns to drop their discs.

3. **Play the game:**
   - Players select a column to drop their disc into. The disc will fall to the lowest available row in that column.
   - The first player to connect four discs vertically, horizontally, or diagonally wins!

4. **Chat while playing:** Players can send messages to each other during the game using the built-in chat interface.

5. **Message Commands:** Players can utilize four different message commands during the game:
   - join
   - move
   - chat
   - quit

6. **Restart the game:** Once a game is finished, players can reset and play again.

## Features:
- Real-time chat functionality during the game
- Graphical interface for the grid and player interaction
- Two-player local game mode
- Automatic victory detection
- Reset and restart functionality

## Technologies used:
- Python
- Sockets for real-time communication

## Game Rules:
- Players take turns selecting a column to drop their disc.
- A player wins by connecting four discs in a row (vertically, horizontally, or diagonally).
- If all grid spaces are filled and no player has connected four, the game results in a draw.
- Players can chat with each other at any time during the game.
