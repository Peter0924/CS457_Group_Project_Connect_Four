
# Connect Four Game with Real-Time Chat

This project is a **Connect Four** game implemented in Python, with an added real-time chat feature. Players can compete in the classic game of Connect Four while communicating with each other during gameplay.

## Features

- **Real-Time Chat**: Players can send messages to each other during the game.
- **Turn-Based Gameplay**: Alternating turns ensure only the current player can make a move.
- **Game State Synchronization**: The server maintains a consistent game state across all connected clients.
- **Player Identification**: Each player has a unique username, making it easy to track moves and chat messages.
- **Automatic Victory Detection**: The server detects when a player connects four discs and announces the winner.
- **Reset and Restart Functionality**: Players can restart the game after a round is completed.
- **Intuitive UI with Pygame**: A simple and interactive game board and chat interface, built using Pygame.

## Technologies Used

- **Python**
- **Sockets**: For real-time communication between the server and clients.
- **Pygame**: For the game board and user interface.

## How to Set Up and Run

### 1. Create a Virtual Environment (Optional but Recommended)

To isolate the project’s dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 2. Install Dependencies
Ensure you have Python (3.6 or later) installed:

```bash
module load python/bundle-3.6

```

Ensure you have Pygame installed:

```bash
pip install pygame

```

### 3. Start the Server

In a terminal, start the server:

```bash
python server.py -p <PORT>

```
Replace <PORT> with the desired port number, e.g., 12345.
Server IP defaults to 127.0.0.1.

### 4. Start the Client

In separate terminals, start the client for each player:

```bash
python client.py -i <SERVER_IP> -p <PORT>

```

Replace <SERVER_IP> with the server's IP address and <PORT> with the port number you used for the server.

### 5. Play the Game

- **Join the Game**: Each player enters a username upon connecting.
- **Take Turns**: Players take turns selecting a column (0-6) to drop their disc.
- **Win the Game**: The first player to connect four discs in a row (vertically, horizontally, or diagonally) wins!
- **Chat with Players**: Players can use the chat feature at any time during the game.
- **Restart**: After a round ends, players can click the "New Game" button to reset the board and start over.

## Game Rules

1. **Connect Four**: Players take turns dropping discs into columns. The disc falls to the lowest available row in that column.
2. **Victory Condition**: A player wins by connecting four discs in a row vertically, horizontally, or diagonally.
3. **Draw Condition**: If all grid spaces are filled and no player has connected four, the game ends in a draw.
4. **Chat Feature**: Players can communicate with each other in real-time using the chat feature.

## Shutting Down

- **Server Shutdown**: Type `shutdown` in the server terminal or press `CTRL + C` to terminate the server.
- **Client Exit**: Type `quit` in the client terminal to exit the game or click quit button to exit the game.

## Brief roadmap of where you would take the project

1. **Advanced UI with Web Integration**: Replace the Pygame interface with a web-based UI using modern frameworks like React. This would enable more flexibility and a better user experience.
2. **Matchmaking and Player Lobby**: Introduce a feature for creating and joining game lobbies, enabling players to find and compete with others online.
3. **AI Opponent**: Add a single-player mode where users can play against a AI with adjustable difficulty levels.
4. **Leaderboards and Statistics**: Track and display player stats, including wins, losses, and ties, in a persistent leaderboard.
5. **Enhanced Chat Features**: Add emojis, message notifications, and group chat capabilities for a richer communication experience.

## Retrospective on Overall Project

### What Went Right

- Successfully implemented core gameplay mechanics and synchronized game state across clients.
- Real-time communication and chat functionality worked as intended.
- The Pygame-based interface provides a functional and intuitive experience for players.

### What Could Be Improved On

- The current UI can be improved to make it more visually appealing and user-friendly, potentially by transitioning to a web-based interface.
- The game lacks scalability for hosting multiple games or players simultaneously.
- Error handling could be further refined for better resilience to unexpected scenarios.


