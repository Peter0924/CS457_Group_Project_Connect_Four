import socket
import threading
import logging
import json
import argparse
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Stores connected clients' information
clients = {}
# Represents the state of the game, including the board, the current turn, and the players
game_state = {
    "board": [["" for _ in range(7)] for _ in range(5)],
    "turn": None,
    "players": []
}

def check_winner():
    """
    Checks if there is a winner or a tie on the 5x7 game board.
    Returns:
        - Winner's token if there is a winner.
        - "tie" if the game ends in a tie.
        - None if the game is still ongoing.
    """
    board = game_state["board"]

    def check_line(start_row, start_col, delta_row, delta_col):
        """Helper function to check if there are 4 tokens in a row."""
        player = board[start_row][start_col]
        if not player:
            return False
        for i in range(1, 4):
            row, col = start_row + i * delta_row, start_col + i * delta_col
            if row < 0 or row >= 5 or col < 0 or col >= 7 or board[row][col] != player:
                return False
        return True

    # Check all possible winning lines
    for row in range(5):
        for col in range(7):
            if (col <= 3 and check_line(row, col, 0, 1)) or \
               (row <= 1 and check_line(row, col, 1, 0)) or \
               (row <= 1 and col <= 3 and check_line(row, col, 1, 1)) or \
               (row >= 3 and col <= 3 and check_line(row, col, -1, 1)):
                return board[row][col]

    # Check for a tie if the board is full
    if all(board[row][col] != "" for row in range(5) for col in range(7)):
        return "tie"

    return None

def reset_game_state():
    """Resets the game state, clearing the board and setting the turn to the first player."""
    global game_state
    game_state["board"] = [["" for _ in range(7)] for _ in range(5)]
    game_state["turn"] = game_state["players"][0] if game_state["players"] else None

def broadcast_game_state():
    """Sends the current game state to all connected clients."""
    game_state_message = json.dumps({
        "type": "update",
        "board": game_state["board"],
        "turn": game_state["turn"],
        "players": game_state["players"]
    })
    broadcast_message(game_state_message)

def broadcast_message(message, exclude_client=None):
    """Sends a message to all connected clients.Removes any disconnected clients."""
    disconnected_clients = []
    for client_socket in clients:
        if client_socket != exclude_client:
            try:
                client_socket.send((message + '\n').encode('utf-8'))
            except Exception:
                disconnected_clients.append(client_socket)

    for client_socket in disconnected_clients:
        if client_socket in clients:
            del clients[client_socket]

def client_connection(client_socket, client_address):
    """Handles communication with a single client, including receiving and processing messages."""
    logging.info(f"Connection established with {client_address}")
    clients[client_socket] = {"address": client_address, "username": None, "id": len(clients)}

    try:
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    logging.warning(f"Empty message received from {client_address}")
                    break
                handle_message(client_socket, message)
            except json.JSONDecodeError:
                logging.error(f"Malformed message from {client_address}: {message}")
                client_socket.send(json.dumps({"type": "error", "message": "Invalid message format"}).encode('utf-8'))
            except Exception as e:
                logging.error(f"Unexpected error with {client_address}: {e}")
                break
    except (ConnectionResetError, OSError):
        logging.error(f"Connection lost with {client_address}")
    finally:
        handle_quit(client_socket)
        client_socket.close()

def handle_message(client_socket, message):
    """Handles message from a client by identifying its type and taking appropriate action."""
    try:
        data = json.loads(message)
        message_type = data.get('type')

        if message_type == "join":
            handle_join(client_socket, data)
        elif message_type == "move":
            handle_move(client_socket, data)
        elif message_type == "chat":
            handle_chat(client_socket, data)
        elif message_type == "quit":
            handle_quit(client_socket)
        elif message_type == "new_game":
            handle_new_game()
        else:
            logging.error(f"Unknown message type: {message_type}")
    except json.JSONDecodeError:
        logging.error(f"Failed to decode message: {message}")

def handle_join(client_socket, data):
    """Handles a client joining the game by adding their username and player ID to the game state and broadcast to others."""
    username = data.get('username')
    playerID = str(uuid.uuid4())

    if len(game_state["players"]) >= 2:
        client_socket.send(json.dumps({
            "type": "error",
            "message": "The game is full. Please try again later."
        }).encode('utf-8'))
        logging.info(f"Rejected connection from {clients[client_socket]['address']}: Game is full")
        client_socket.close()
        if client_socket in clients:
            del clients[client_socket]
        return

    clients[client_socket]["username"] = username
    clients[client_socket]["id"] = playerID
    game_state["players"].append({"id": playerID, "username": username})

    if len(game_state["players"]) == 1:
        game_state["turn"] = playerID

    broadcast_message(json.dumps({"type": "join", "message": f"{username} has joined the game."}))
    broadcast_game_state()

def handle_move(client_socket, data):
    """Handles a player's move, updating the board, checking for a winner or tie, and updating the turn."""
    username = clients[client_socket]["username"]
    playerID = clients[client_socket]["id"]
    if len(game_state["players"]) < 2:
        client_socket.send(json.dumps({
            "type": "error",
            "message": "Wait for another player to join before making a move."
        }).encode('utf-8'))
        return

    if game_state["turn"] != username:
        logging.warning(f"It's not {username}'s turn.")
        return

    column = data.get('column')
    if column is not None and 0 <= column < 7:  
        player_index = game_state["players"].index(username)  
        for row in reversed(range(5)):
            if game_state["board"][row][column] == "":
                game_state["board"][row][column] = str(player_index) 
                break
        else:
            logging.warning("Column is full!")
            return

        winner = check_winner()
        if winner == "tie":
            broadcast_message(json.dumps({"type": "game_tie", "message": "The game is a tie!"}))
            game_state["turn"] = None
        elif winner:
            broadcast_message(json.dumps({"type": "game_over", "message": f"{game_state['players'][int(winner)]} wins!"}))
            game_state["turn"] = None
        else:
            next_index = (game_state["players"].index(username) + 1) % len(game_state["players"])
            game_state["turn"] = game_state["players"][next_index]

        broadcast_game_state()
    else:
        logging.error("Invalid move data")

def handle_chat(client_socket, data):
    """Handles a chat message from a client and broadcasts it to all connected clients."""
    username = clients[client_socket]["username"]
    chat_message = data.get('message')
    if chat_message:
        broadcast_message(json.dumps({"type": "chat", "message": f"{username}: {chat_message}"}))

def handle_quit(client_socket):
    """Handles a client leaving the game by removing them from the game state and notifying others."""
    username = clients[client_socket].get("username")
    if username:
        game_state["players"].remove(username)
        broadcast_message(json.dumps({"type": "quit", "message": f"{username} has left the game."}))
    if client_socket in clients:
        del clients[client_socket]
    broadcast_game_state()

def handle_new_game():
    """Resets the game state and notifies all clients about the start of a new game."""
    reset_game_state()
    broadcast_message(json.dumps({"type": "new_game"}))
    broadcast_message(json.dumps({"type": "chat", "message": "A new game has started!"}))
    broadcast_game_state()

def server_startup():
    """Starts the server, listens for incoming connections, and spawns threads to handle clients."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to run the server on")
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', args.port))
    server.listen(5)
    logging.info(f"Server started on 0.0.0.0:{args.port}")

    while True:
        try:
            client_socket, client_address = server.accept()
            threading.Thread(target=client_connection, args=(client_socket, client_address)).start()
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
            break

    server.close()

if __name__ == "__main__":
    server_startup()
