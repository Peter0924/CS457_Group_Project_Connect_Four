import socket
import threading
import logging

# Setup to log connection and disconnection events
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def client_connection(client_socket, client_address):
    logging.info(f"Connection established with {client_address}")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            logging.info(f"Message received from {client_address}: {message}")

            # Echo the message back to the client
            client_socket.send(f"Server echoed message: {message}".encode('utf-8'))
        except ConnectionResetError:
            logging.error(f"Connection lost with {client_address}")
            break
        except Exception as e:
            logging.error(f"Unexpected error with client {client_address}: {e}")
            break
    
    logging.info(f"Client {client_address} disconnected.")
    client_socket.close()

def server_startup(server_address='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((server_address, port))
        server.listen(5)  # Set the max number of simultaneous connections
        logging.info(f"Server started on {server_address}:{port}")

        # Start a thread to accept client connections
        accept_thread = threading.Thread(target=accept_connections, args=(server,))
        accept_thread.start()
        
        accept_thread.join()

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Shutting down server.")
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
