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
    response_data = json.loads(response)
    
    if response_data['type'] == 'join':
        logging.info(response_data['message'])
        game_state["players"].append(response_data['message']) 
    elif response_data['type'] == 'move':
        logging.info(response_data['message'])
        game_state["player_position"] = response_data['message']

    elif response_data['type'] == 'chat':
        logging.info(f"Chat message: {response_data['message']}")

    elif response_data['type'] == 'quit':
        logging.info(response_data['message'])
        # Assuming response['message'] is "{username} has left the game."
        leaving_player = response_data['message'].split(" ")[0]
        game_state["players"] = [p for p in game_state["players"] if leaving_player not in p]

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        logging.info(f"Connected to server at {HOST}:{PORT}")

        # Send a join message to the server
        username = input("Enter your username: ")
        join_message = json.dumps({"type": "join", "username": username})
        client.send((join_message + '\n').encode('utf-8'))  # Add a delimiter when sending

        while True:
            message = input("Enter message (type 'move', 'chat', or 'quit' to disconnect): ")

            if message.lower() == 'move':
                x = int(input("Enter x coordinate: "))
                y = int(input("Enter y coordinate: "))
                move_message = json.dumps({"type": "move", "x": x, "y": y})
                client.send((move_message + '\n').encode('utf-8'))  # Add delimiter

            elif message.lower() == 'chat':
                chat_message = input("Enter chat message: ")
                chat_message = json.dumps({"type": "chat", "message": chat_message})
                client.send((chat_message + '\n').encode('utf-8'))  # Add delimiter

            elif message.lower() == 'quit':
                quit_message = json.dumps({"type": "quit"})
                client.send((quit_message + '\n').encode('utf-8'))  # Add delimiter
                break

            # Receive and process messages
            data = client.recv(1024).decode('utf-8')
            if data:
                # Split the data on the newline delimiter and process each message
                for response in data.strip().split('\n'):
                    update_game_state(response)

    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    start_client()
