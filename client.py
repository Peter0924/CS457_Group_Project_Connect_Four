import socket
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '127.0.0.1'  # Server address
PORT = 12345        # Server port

game_state = {
    "player_position": None,
    "turn": None,
    "players": [],
}

def update_game_state(response):
    """Update the game state based on server response."""
    response_data = json.loads(response)
    
    if response_data['type'] == 'join':
        logging.info(response_data['message'])
        game_state["players"].append(response_data['message'])  # Add new player to the state

    elif response_data['type'] == 'move':
        logging.info(response_data['message'])
        # Update the player's position (this is a basic example, adjust as needed)
        game_state["player_position"] = response_data['message']

    elif response_data['type'] == 'chat':
        logging.info(f"Chat message: {response_data['message']}")

    elif response_data['type'] == 'quit':
        logging.info(response_data['message'])
        # You could also remove the player from the game state here
        game_state["players"].remove(response_data['message'])

    elif response_data['type'] == 'error':
        logging.error(f"Error from server: {response_data['message']}")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        logging.info(f"Connected to server at {HOST}:{PORT}")

        # Send a join message to the server
        username = input("Enter your username: ")
        join_message = json.dumps({"type": "join", "username": username})
        client.send(join_message.encode('utf-8'))

        while True:
            message = input("Enter message (type 'move', 'chat', or 'exit' to disconnect): ")

            if message.lower() == 'move':
                x = int(input("Enter x coordinate: "))
                y = int(input("Enter y coordinate: "))
                move_message = json.dumps({"type": "move", "x": x, "y": y})
                client.send(move_message.encode('utf-8'))

            elif message.lower() == 'chat':
                chat_message = input("Enter chat message: ")
                chat_message = json.dumps({"type": "chat", "message": chat_message})
                client.send(chat_message.encode('utf-8'))

            elif message.lower() == 'exit':
                quit_message = json.dumps({"type": "quit"})
                client.send(quit_message.encode('utf-8'))
                break

            # Receive server response and update the game state
            response = client.recv(1024).decode('utf-8')
            if response:
                update_game_state(response)

    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    start_client()
