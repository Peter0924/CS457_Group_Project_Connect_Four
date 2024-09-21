# Connect Four Game with Chat Feature

This is a **Connect Four** game implemented using Python, enhanced with a built-in chat feature. Players can enjoy the classic game while chatting with each other in real time during gameplay.

## How to play:
1. **Start the game:** Run the `connect_four_server.py` script to start the server, then run the `connect_four_client.py` script on two different machines or terminals to connect as players.

2. **Game setup:** The game starts with an empty 6x7 grid. Two players alternate turns to drop their discs.

3. **Play the game:**
   - Players select a column to drop their disc into. The disc will fall to the lowest available row in that column.
   - The first player to connect four discs vertically, horizontally, or diagonally wins!

4. **Chat while playing:** Players can send messages to each other during the game using the built-in chat interface.

5. **Restart the game:** Once a game is finished, players can reset and play again.

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
