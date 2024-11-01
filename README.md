
# Connect Four Game with Real-Time Chat

This project is a **Connect Four** game implemented in Python, with an added real-time chat feature. Players can compete in the classic game of Connect Four while communicating with each other during gameplay.

## Features

- **Real-Time Chat**: Players can send messages to each other during the game.
- **Turn-Based Gameplay**: Alternating turns ensure only the current player can make a move.
- **Game State Synchronization**: The server maintains a consistent game state across all connected clients.
- **Player Identification**: Each player has a unique username, making it easy to track moves and chat messages.
- **Automatic Victory Detection**: The server detects when a player connects four discs and announces the winner.
- **Reset and Restart Functionality**: Players can restart the game after a round is completed.

## Technologies Used

- **Python**
- **Sockets**: For real-time communication between the server and clients.

## How to Set Up and Run

### 1. Create a Virtual Environment (Optional but Recommended)

To isolate the project’s dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 2. Start the Server

In a terminal, start the server:

```bash
python server.py
```

### 3. Start the Client

In separate terminals, start the client for each player:

```bash
python client.py
```

You can run multiple clients to connect multiple players.

### 4. Play the Game

- **Join the Game**: Each player enters a username upon connecting.
- **Take Turns**: Players take turns selecting a column (0-6) to drop their disc.
- **Win the Game**: The first player to connect four discs in a row (vertically, horizontally, or diagonally) wins!
- **Chat with Players**: Players can use the chat feature at any time during the game.
- **Restart**: Once a game finishes, players can reset and play again.

## In-Game Commands

Players can enter the following commands during the game:

- **join**: Join the game with a username.
- **move**: Make a move by selecting a column.
- **chat**: Send a message to all players.
- **quit**: Leave the game.

## Game Rules

1. **Connect Four**: Players take turns dropping discs into columns. The disc falls to the lowest available row in that column.
2. **Victory Condition**: A player wins by connecting four discs in a row vertically, horizontally, or diagonally.
3. **Draw Condition**: If all grid spaces are filled and no player has connected four, the game ends in a draw.
4. **Chat Feature**: Players can communicate with each other in real-time using the chat feature.

## Shutting Down

- **Server Shutdown**: Type `shutdown` in the server terminal or press `CTRL + C` to terminate the server.
- **Client Exit**: Type `quit` in the client terminal to exit the game.

## Testing Instructions

1. **Activate the Virtual Environment** (if set up earlier):

    ```bash
    # Windows
    venv\Scripts\activate

    # Mac/Linux
    source venv/bin/activate
    ```

2. **Start the Server**: In a new terminal, run `python server.py`.

3. **Run Tests** (if test files are available):

    ```bash
    pytest test.py
    ```
