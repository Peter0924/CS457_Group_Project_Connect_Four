import socket
import threading
import json
import pygame
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants for Pygame
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 600
COLUMN_COUNT = 7
ROW_COUNT = 6
SQUARE_SIZE = 100
RADIUS = int(SQUARE_SIZE / 2 - 5)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

game_state = {
    "board": [["" for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)],
    "turn": None,
    "players": []
}
username = None
client = None
chat_messages = []
game_over = False

def reset_game_state():
    """Reset the game state for a new round and update the turn."""
    global game_state, game_over
    game_state["board"] = [["" for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
    game_state["turn"] = game_state["players"][0] if game_state["players"] else None  # Set turn to the first player
    game_over = False

def draw_button(screen, text, x, y, width, height, color, text_color):
    """Draw a button on the screen."""
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

def render_board(screen):
    """Draw the game board on the screen."""
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            pygame.draw.rect(screen, BLUE, (col * SQUARE_SIZE, row * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), int(row * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            if game_state["board"][row][col] == username[0]:
                pygame.draw.circle(screen, RED, (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), SCREEN_HEIGHT - int((ROW_COUNT - row - 1) * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif game_state["board"][row][col] != "":
                pygame.draw.circle(screen, YELLOW, (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), SCREEN_HEIGHT - int((ROW_COUNT - row - 1) * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)

def render_chat(screen, font):
    """Display chat messages on the right side of the screen."""
    chat_x = SCREEN_WIDTH
    chat_y = 10
    chat_width = 300
    pygame.draw.rect(screen, WHITE, (chat_x, 0, chat_width, SCREEN_HEIGHT))
    for message in chat_messages[-20:]:  # Show the last 20 messages
        text_surface = font.render(message, True, BLACK)
        screen.blit(text_surface, (chat_x + 10, chat_y))
        chat_y += 30

def update_game_state(response):
    """Update the game state based on the server response."""
    global game_state, game_over
    data = json.loads(response)

    if data['type'] == 'update':
        game_state["board"] = data["board"]
        game_state["turn"] = data["turn"]
        game_state["players"] = data["players"]
    elif data['type'] == 'chat':
        chat_messages.append(data['message'])
    elif data['type'] == 'game_over':
        chat_messages.append(data['message'])
        game_over = True
    elif data['type'] == 'new_game':
        reset_game_state()  # Reset the game state when a new game starts
        chat_messages.append("A new game has started!")
        logging.info("A new game has started!")
    elif data['type'] in ('join', 'move', 'quit'):
        chat_messages.append(data['message'])
        logging.info(data['message'])

def receive_messages():
    """Thread to receive messages from the server."""
    global client
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                for response in data.strip().split('\n'):
                    update_game_state(response)
        except Exception as e:
            logging.error(f"Error receiving data: {e}")
            break

def start_client(ip, port):
    """Connect to the server and handle game interaction."""
    global username, client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ip, port))
        logging.info(f"Connected to server at {ip}:{port}")

        username = input("Enter your username: ")
        client.send(json.dumps({"type": "join", "username": username}).encode('utf-8'))

        threading.Thread(target=receive_messages, daemon=True).start()

        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH + 300, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Connect Four - {username}")
        font = pygame.font.SysFont(None, 24)

        running = True
        chat_input = ""
        while running:
            screen.fill(WHITE)  # Clear the screen once per loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    if game_state["turn"] == username:
                        x_pos = event.pos[0]
                        if x_pos < SCREEN_WIDTH:  # Only register clicks on the game board
                            col = int(x_pos / SQUARE_SIZE)
                            if 0 <= col < COLUMN_COUNT:
                                client.send(json.dumps({"type": "move", "column": col}).encode('utf-8'))

                if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                    mouse_x, mouse_y = event.pos
                    if 20 <= mouse_x <= 170 and 20 <= mouse_y <= 70:  # New Game button
                        reset_game_state()
                        client.send(json.dumps({"type": "new_game"}).encode('utf-8'))
                    elif 200 <= mouse_x <= 350 and 20 <= mouse_y <= 70:  # Quit button
                        running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if chat_input:
                            client.send(json.dumps({"type": "chat", "message": chat_input}).encode('utf-8'))
                            chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    else:
                        chat_input += event.unicode

            # Draw everything
            render_board(screen)
            render_chat(screen, font)

            # If the game is over, show buttons for a new game or quit
            if game_over:
                draw_button(screen, "New Game", 20, 20, 150, 50, BLUE, WHITE)
                draw_button(screen, "Quit", 200, 20, 150, 50, RED, WHITE)

            # Render chat input box
            chat_surface = font.render("Chat: " + chat_input, True, BLACK)
            screen.blit(chat_surface, (SCREEN_WIDTH + 10, SCREEN_HEIGHT - 30))

            pygame.display.update()

    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")
        pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", required=True, help="Server IP address")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server port")
    args = parser.parse_args()
    start_client(args.ip, args.port)
