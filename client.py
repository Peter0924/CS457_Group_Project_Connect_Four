import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '127.0.0.1'  # Server address
PORT = 12345      # Server port

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        logging.info(f"Connected to server at {HOST}:{PORT}")

        while True:
            message = input("Enter message to send (type 'exit' to disconnect): ")
            if message.lower() == 'exit':
                break
            client.send(message.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            logging.info(f"Server response: {response}")
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    start_client()
