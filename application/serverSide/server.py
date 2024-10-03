import socket
import threading
import logging

# setup to log connection and disconnection events
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def clientConnection(clientSocket, clientAddress):
    logging.info(f"Connection Established with {clientAddress}")

    while True:
        try:
            message = clientSocket.recv(1024).decode('utf-8')
            if not message:
                break
            logging.info(f"Message received from {clientAddress}: {message}")

            clientSocket.send(f"Server Echoed Message: {message}".encode('utf-8'))
        except ConnectionResetError:
            logging.error(f"{clientAddress} Connection Lost.")
            break
    
    logging.info(f"{clientAddress} disconnected.")
    clientSocket.close()

# change server IP and PORT # in parameters
def serverStartup(serverAddress='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((serverAddress, port))
    server.listen(5) # change the max number of simultaneous connections here, initial set to 5
    logging.info(f"Server started on {serverAddress}:{port}")

    while True:
        clientSocket, clientAddress = server.accept()
        logging.info(f"Connection from {clientAddress} established.")

        clientHandler = threading.Thread(target=clientConnection, args=(clientSocket, clientAddress))
        clientHandler.start()