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
                logging.info(f"Empty message received from {client_address}. Closing connection.")
                break
            logging.info(f"Message received from {client_address}: {message}")
            client_socket.send(f"Server echoed message: {message}".encode('utf-8'))
        except (ConnectionResetError, socket.error) as e:
            logging.error(f"Connection lost with {client_address}: {e}")
            break
        finally:
            logging.info(f"Client {client_address} disconnected.")
            client_socket.close()

def server_startup(server_address='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((server_address, port))
        server.listen(5) 
        logging.info(f"Server started on {server_address}:{port}")
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
