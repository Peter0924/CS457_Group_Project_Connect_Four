import socket
import logging
import json
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '127.0.0.1'  # Server address
PORT = 12345      # Server port

game_state = {
    "board": [["" for _ in range(7)] for _ in range(6)],
    "turn": None,
    "players": []
}
username = None

def render_board():
    """Render the game board in the console."""
    print("\nCurrent Board:")
    for row in game_state["board"]:
        print(" | ".join(cell or " " for cell in row))
    print("\n")

def update_game_state(response):
    response_data = json.loads(response)
    global game_state
    
    if response_data['type'] == 'update':
        game_state["board"] = response_data["board"]
        game_state["turn"] = response_data["turn"]
        game_state["players"] = response_data["players"]
        render_board()
        
        if game_state["turn"] == username:
            logging.info("It's your turn!")
        else:
            logging.info(f"Waiting for {game_state['turn']} to make a move.")

    elif response_data['type'] == 'join':
        logging.info(response_data['message'])

    elif response_data['type'] == 'move':
        logging.info(response_data['message'])

    elif response_data['type'] == 'chat':
        logging.info(f"Chat message: {response_data['message']}")

    elif response_data['type'] == 'quit':
        logging.info(response_data['message'])

def receive_messages(client):
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                for response in data.strip().split('\n'):
                    update_game_state(response)
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
            break

def start_client():
    global username
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        logging.info(f"Connected to server at {HOST}:{PORT}")

        # Start message receiving thread
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()

        # Send a join message to the server
        username = input("Enter your username: ")
        join_message = json.dumps({"type": "join", "username": username})
        client.send((join_message + '\n').encode('utf-8'))

        while True:
            if game_state["turn"] == username:
                # Only allow input when it's the client's turn
                message = input("Enter 'move' to play, 'chat' to send a message, or 'quit' to disconnect: ")

                if message.lower() == 'move':
                    try:
                        column = int(input("Enter column (0-6): "))
                        if column < 0 or column > 6:
                            print("Invalid column. Please enter a number between 0 and 6.")
                            continue
                        move_message = json.dumps({"type": "move", "column": column})
                        client.send((move_message + '\n').encode('utf-8'))
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                    
                elif message.lower() == 'chat':
                    chat_message = input("Enter chat message: ")
                    chat_message = json.dumps({"type": "chat", "message": chat_message})
                    client.send((chat_message + '\n').encode('utf-8'))

                elif message.lower() == 'quit':
                    quit_message = json.dumps({"type": "quit"})
                    client.send((quit_message + '\n').encode('utf-8'))
                    break
            else:
                # Display turn information and wait if it's not the client's turn
                logging.info(f"Waiting for {game_state['turn']} to make a move...")

    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    start_client()
