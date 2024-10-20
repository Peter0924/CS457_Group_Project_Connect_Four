import socket
import threading
import logging
import json

# Setup to log connection and disconnection events
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

clients = {} 

def broadcast_message(message):
    """Send a message to all connected clients."""
    for client_socket in clients:
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error broadcasting to {clients[client_socket]}: {e}")

def client_connection(client_socket, client_address):
    logging.info(f"Connection established with {client_address}")
    clients[client_socket] = {"address": client_address, "username": None, "position": (0,0)}

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            logging.info(f"Message received from {client_address}: {message}")
            handle_message(client_socket, message)
        except ConnectionResetError:
            logging.error(f"Connection lost with {client_address}")
            break
        except Exception as e:
            logging.error(f"Unexpected error with client {client_address}: {e}")
            break

    logging.info(f"Client {client_address} disconnected.")
    if client_socket in clients:
        del clients[client_socket]
    client_socket.close()

def handle_message(client_socket, message):
    """Handle different types of messages from clients."""
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
    clients[client_socket]["position"] = (0, 0) # initialize at (0,0)
    response = {"type": "join", "message": f"Player {username} has joined the game."}
    broadcast_message(json.dumps(response))

def handle_move(client_socket, data):
    x, y = data.get('x'), data.get('y')
    username = clients[client_socket]["username"]
    clients[client_socket]["position"] = (x, y)
    response = {"type": "move", "message": f"{username} moved to ({x}, {y})"}
    broadcast_message(json.dumps(response))

def handle_chat(client_socket, data):
    username = clients[client_socket]["username"]
    chat_message = data.get('message')
    response = {"type": "chat", "message": f"{username}: {chat_message}"}
    broadcast_message(json.dumps(response))

def handle_quit(client_socket):
    username = clients[client_socket]["username"]
    response = {"type": "quit", "message": f"{username} has left the game."}
    broadcast_message(json.dumps(response))
    client_socket.close()
    if client_socket in clients:
        del clients[client_socket]  # Remove client from list

def server_startup(server_address='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_address, port))
    server.listen(5)  # Set the max number of simultaneous connections
    logging.info(f"Server started on {server_address}:{port}")

    # Start a thread to accept client connections
    accept_thread = threading.Thread(target=accept_connections, args=(server,))
    accept_thread.start()

    # Wait for shutdown command
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
            logging.info(f"Connection from {client_address} established.")

            client_handler = threading.Thread(target=client_connection, args=(client_socket, client_address))
            client_handler.daemon = True 
            client_handler.start()
        except OSError:
            break

if __name__ == "__main__":
    server_startup()
