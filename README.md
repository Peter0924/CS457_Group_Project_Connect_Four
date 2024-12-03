
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

### 5. Play the Game

