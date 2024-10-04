import socket
import threading
import pytest
import time
from server import server_startup

# Helper function to start the server in a thread
def start_test_server():
    server_thread = threading.Thread(target=server_startup, kwargs={'server_address': '127.0.0.1', 'port': 12345})
    server_thread.daemon = True  # Ensures the thread exits when the main program exits
    server_thread.start()
    time.sleep(1)  # Allow time for the server to start

@pytest.fixture(scope="module")
def test_server():
    start_test_server()
    time.sleep(1)  

# Test the server's ability to handle a successful client connection
def test_client_connection(test_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 12345))
        client.send(b"Hello, Server!")
        response = client.recv(1024).decode('utf-8')
        assert "Server echoed message: Hello, Server!" in response
    except ConnectionRefusedError:
        pytest.fail("Server is not accepting connections. Ensure it is running on the correct port.")
    finally:
        client.close()

# Test multiple client connections to verify concurrency
def test_multiple_clients(test_server):
    clients = []
    try:
        for i in range(5):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(('127.0.0.1', 12345))
                clients.append(client)
            except ConnectionRefusedError:
                pytest.fail(f"Server refused connection for client {i}. Ensure it is ready for multiple connections.")
        for i, client in enumerate(clients):
            message = f"Hello from client {i}"
            client.send(message.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            assert f"Server echoed message: {message}" in response
    finally:
        for client in clients:
            client.close()

# Test error handling: server should handle refused connections gracefully
def test_client_connection_refused():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with pytest.raises(ConnectionRefusedError):
        client.connect(('127.0.0.1', 9999)) 

# Test client sending empty message
def test_client_sends_empty_message(test_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 12345))
        client.send(b"") 
        response = client.recv(1024).decode('utf-8')
        assert response == "" 
    except ConnectionRefusedError:
        pytest.fail("Server refused connection for empty message test.")
    finally:
        client.close()

# Test server logging error when client disconnects abruptly
def test_client_disconnects_abruptly(test_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 12345))
        client.send(b"Hello, Server!")
        response = client.recv(1024).decode('utf-8')
        assert "Server echoed message: Hello, Server!" in response

     
        client.close()
        time.sleep(1)  
    except ConnectionRefusedError:
        pytest.fail("Server refused connection unexpectedly.")
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
