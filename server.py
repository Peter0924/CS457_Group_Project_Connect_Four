import socket
import threading
import logging
import json
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

clients = {}
game_state = {
    "board": [["" for _ in range(7)] for _ in range(6)],
    "turn": None,
    "players": []
}

def check_winner():
    """Check for a winning condition on the board."""
    board = game_state["board"]

    def check_line(start_row, start_col, delta_row, delta_col):
        player = board[start_row][start_col]
        if not player:
            return False
        for i in range(1, 4):
            row, col = start_row + i * delta_row, start_col + i * delta_col
            if board[row][col] != player:
                return False
        return True

    for row in range(6):
        for col in range(7):
            if (col <= 3 and check_line(row, col, 0, 1)) or \
               (row <= 2 and check_line(row, col, 1, 0)) or \
               (row <= 2 and col <= 3 and check_line(row, col, 1, 1)) or \
               (row >= 3 and col <= 3 and check_line(row, col, -1, 1)):
                return board[row][col]
    return None

def reset_game_state():
    """Reset the game state for a new round."""
    global game_state
    game_state = {
        "board": [["" for _ in range(7)] for _ in range(6)],
        "turn": None,
        "players": game_state["players"]  # Keep the same players
    }

def broadcast_game_state():
    game_state_message = json.dumps({
        "type": "update",
        "board": game_state["board"],
        "turn": game_state["turn"],
        "players": game_state["players"]
    })
    broadcast_message(game_state_message)

def broadcast_message(message, exclude_client=None):
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
    logging.info(f"Connection established with {client_address}")
    clients[client_socket] = {"address": client_address, "username": None, "id": len(clients)}

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            handle_message(client_socket, message)
    except (ConnectionResetError, OSError):
        logging.error(f"Connection lost with {client_address}")
    finally:
        handle_quit(client_socket)
        client_socket.close()

def handle_message(client_socket, message):
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
    username = data.get('username')
    clients[client_socket]["username"] = username
    game_state["players"].append(username)

    if len(game_state["players"]) == 1:
        game_state["turn"] = username

    broadcast_message(json.dumps({"type": "join", "message": f"{username} has joined the game."}))
    broadcast_game_state()

def handle_move(client_socket, data):
    username = clients[client_socket]["username"]
    if game_state["turn"] != username:
        logging.warning(f"It's not {username}'s turn.")
        return

    column = data.get('column')
    if column is not None and 0 <= column < 7:
        for row in reversed(range(6)):
            if game_state["board"][row][column] == "":
                game_state["board"][row][column] = username[0]
                break
        else:
            logging.warning("Column is full!")
            return

        winner = check_winner()
        if winner:
            broadcast_message(json.dumps({"type": "game_over", "message": f"{winner} wins!"}))
            game_state["board"] = [["" for _ in range(7)] for _ in range(6)]
            game_state["turn"] = None
        else:
            next_index = (game_state["players"].index(username) + 1) % len(game_state["players"])
            game_state["turn"] = game_state["players"][next_index]

        broadcast_game_state()
    else:
        logging.error("Invalid move data")

def handle_chat(client_socket, data):
    username = clients[client_socket]["username"]
    chat_message = data.get('message')
    broadcast_message(json.dumps({"type": "chat", "message": f"{username}: {chat_message}"}), exclude_client=client_socket)

def handle_quit(client_socket):
    username = clients[client_socket].get("username")
    if username:
        game_state["players"].remove(username)
        broadcast_message(json.dumps({"type": "quit", "message": f"{username} has left the game."}))
    if client_socket in clients:
        del clients[client_socket]
    broadcast_game_state()

def handle_new_game():
    """Handle resetting the game for a new round."""
    reset_game_state()
    broadcast_message(json.dumps({"type": "chat", "message": "A new game has started!"}))
    broadcast_game_state()

def server_startup():
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
