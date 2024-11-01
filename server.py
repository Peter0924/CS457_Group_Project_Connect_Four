import socket
import threading
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

clients = {}  # Stores client socket with details
game_state = {
    "board": [["" for _ in range(7)] for _ in range(6)],  # Empty 6x7 board
    "turn": None,
    "players": []
}

def broadcast_game_state():
    """Send the current game state to all clients."""
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
            except Exception as e:
                logging.error(f"Error broadcasting to {clients[client_socket]['username']}: {e}")
                disconnected_clients.append(client_socket)

    # Remove disconnected clients from the list
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
        else:
            logging.error(f"Unknown message type: {message_type}")
    except json.JSONDecodeError:
        logging.error(f"Failed to decode message: {message}")

def handle_join(client_socket, data):
    username = data.get('username')
    clients[client_socket]["username"] = username
    game_state["players"].append(username)
    
    if len(game_state["players"]) == 1:
        game_state["turn"] = username  # First player to join gets the first turn
    
    response = {"type": "join", "message": f"{username} has joined the game."}
    broadcast_message(json.dumps(response))
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
                game_state["board"][row][column] = username[0]  # Place player's initial as a marker
                break
        else:
            logging.warning("Column is full!")
            return

        # Toggle turn to the next player
        next_index = (game_state["players"].index(username) + 1) % len(game_state["players"])
        game_state["turn"] = game_state["players"][next_index]

        response = {"type": "move", "message": f"{username} made a move in column {column}."}
        broadcast_message(json.dumps(response))
        broadcast_game_state()
    else:
        logging.error("Invalid move data")

def handle_chat(client_socket, data):
    username = clients[client_socket]["username"]
    chat_message = data.get('message')
    response = {"type": "chat", "message": f"{username}: {chat_message}"}
    broadcast_message(json.dumps(response), exclude_client=client_socket)

def handle_quit(client_socket):
    username = clients[client_socket].get("username") if client_socket in clients else None
    if username:
        response = {"type": "quit", "message": f"{username} has left the game."}
        broadcast_message(json.dumps(response), exclude_client=client_socket)
        game_state["players"].remove(username)
        logging.info(f"Client {username} has been removed from the game.")
    if client_socket in clients:
        del clients[client_socket]
    broadcast_game_state()

def server_startup(server_address='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_address, port))
    server.listen(5)
    logging.info(f"Server started on {server_address}:{port}")

    accept_thread = threading.Thread(target=accept_connections, args=(server,))
    accept_thread.start()

    try:
        while True:
            command = input("Type 'shutdown' to stop the server: ").strip().lower()
            if command == 'shutdown':
                logging.info("Shutdown command received. Shutting down server...")
                break
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Shutting down server...")
    finally:
        server.close()
        logging.info("Server socket closed.")

def accept_connections(server):
    while True:
        try:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=client_connection, args=(client_socket, client_address))
            client_handler.daemon = True
            client_handler.start()
        except OSError:
            break

if __name__ == "__main__":
    server_startup()
