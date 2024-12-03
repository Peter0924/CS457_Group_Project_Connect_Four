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
ROW_COUNT = 5
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

def get_username(screen, font):
    """Display a pop-up to enter the player's username with animations."""
    username_input = ""
    input_active = True
    clock = pygame.time.Clock()
    pulse_direction = 1
    pulse_value = 255  

    while input_active:
        screen.fill(WHITE) 

        
        instructions = font.render("Enter your username:", True, BLACK)
        screen.blit(instructions, (100, 150))

       
        pulse_value += pulse_direction * 5
        if pulse_value > 255:
            pulse_value = 255
            pulse_direction = -1
        elif pulse_value < 100:
            pulse_value = 100
            pulse_direction = 1

        pulse_color = (pulse_value, pulse_value, pulse_value) 
        pygame.draw.rect(screen, pulse_color, (100, 200, 400, 50), border_radius=5)  
        pygame.draw.rect(screen, WHITE, (100, 200, 400, 50), 2, border_radius=5) 

        
        input_text = font.render(username_input, True, BLACK)
        screen.blit(input_text, (110, 210))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  
                    username_input = username_input[:-1]
                else: 
                    username_input += event.unicode

        pygame.display.update()
        clock.tick(30)

    return username_input.strip()


def reset_game_state():
    """Reset the game state for a new round and update the turn."""
    global game_state, game_over
    game_state["board"] = [["" for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
    game_state["turn"] = game_state["players"][0] if game_state["players"] else None  
    game_over = False

def draw_button(screen, text, x, y, width, height, color, text_color, hover=False):
    """Draw a button with hover effects and a shadow."""
    shadow_color = (50, 50, 50) if not hover else (100, 100, 100)
    pygame.draw.rect(screen, shadow_color, (x + 3, y + 3, width, height)) 
    pygame.draw.rect(screen, color, (x, y, width, height)) 

    if hover:
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 3) 

    font = pygame.font.SysFont(None, 36)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

def render_board(screen):
    """Draw the game board on the screen."""
    for i in range(SCREEN_HEIGHT):
        color_value = int(200 - (200 * (i / SCREEN_HEIGHT)))
        pygame.draw.rect(screen, (0, color_value, 255), (0, i, SCREEN_WIDTH, 1))

    player_colors = [RED, (0, 255, 0)]  

    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            center = (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), int(row * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2))
            pygame.draw.circle(screen, BLACK, center, RADIUS + 3)  
            pygame.draw.circle(screen, (50, 50, 50), center, RADIUS)  

    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT):
            token = game_state["board"][row][col]
            if token:
                color = player_colors[int(token)]  
                center = (int(col * SQUARE_SIZE + SQUARE_SIZE / 2), SCREEN_HEIGHT - int((ROW_COUNT - row - 1) * SQUARE_SIZE + SQUARE_SIZE / 2))
                pygame.draw.circle(screen, (255, 255, 255), center, RADIUS + 5)  
                pygame.draw.circle(screen, color, center, RADIUS)  

def render_chat(screen, font, chat_input):
    """Display chat messages and player colors with an input box for new messages."""
    chat_x = SCREEN_WIDTH
    chat_width = 300
    max_messages = 20

    for i in range(SCREEN_HEIGHT):
        color_value = int(255 - (255 * (i / SCREEN_HEIGHT)))
        pygame.draw.rect(screen, (color_value, color_value, color_value), (chat_x, i, chat_width, 1))

    chat_y = 10  

    player_colors = [RED, (0, 255, 0)]
    for i, player in enumerate(game_state["players"]):
        color = player_colors[i] if i < len(player_colors) else BLACK
        pygame.draw.circle(screen, color, (chat_x + 15, chat_y + 15), 10)
        player_text = font.render(player, True, BLACK)
        screen.blit(player_text, (chat_x + 30, chat_y))
        chat_y += 30

    chat_y += 10  

    visible_messages = chat_messages[-max_messages:]
    for message in visible_messages:
        words = message.split(' ')
        wrapped_lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] > chat_width - 20:  
                wrapped_lines.append(line)
                line = word + " "
            else:
                line = test_line

        if line:
            wrapped_lines.append(line)

        for wrapped_line in wrapped_lines:
            text_surface = font.render(wrapped_line, True, BLACK)
            screen.blit(text_surface, (chat_x + 10, chat_y))
            chat_y += 20  

    input_box_y = SCREEN_HEIGHT - 50
    pygame.draw.rect(screen, BLACK, (chat_x + 10, input_box_y, chat_width - 20, 40), border_radius=5)
    pygame.draw.rect(screen, WHITE, (chat_x + 10, input_box_y, chat_width - 20, 40), 2, border_radius=5)
    chat_surface = font.render(chat_input, True, WHITE)
    screen.blit(chat_surface, (chat_x + 15, input_box_y + 10))

def update_game_state(response):
    """Update the game state based on the server response."""
    global game_state, game_over
    try:
        data = json.loads(response)
        logging.info(f"Received server message: {data}")

        if data['type'] == 'update':
            game_state["board"] = data["board"]
            game_state["turn"] = data["turn"]
            game_state["players"] = data["players"]
        elif data['type'] == 'chat':
            chat_messages.append(data['message'])
        elif data['type'] == 'error':  # Display server error messages
            chat_messages.append(f"Error: {data['message']}")
        elif data['type'] == 'game_over':
            chat_messages.append(data['message'])
            game_over = True
        elif data['type'] == 'game_tie':
            chat_messages.append(data['message'])
            game_over = True
        elif data['type'] == 'new_game':
            reset_game_state()
            chat_messages.append("A new game has started!")
        elif data['type'] in ('join', 'move', 'quit'):
            chat_messages.append(data['message'])
    except json.JSONDecodeError:
        logging.error(f"Malformed response from server: {response}")


def receive_messages():
    """Thread to receive messages from the server."""
    global client
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                for response in data.strip().split('\n'):
                    update_game_state(response)
        except (ConnectionResetError, OSError):
            chat_messages.append("Disconnected from server. Please restart the client.")
            break
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

        pygame.init()
        screen = pygame.display.set_mode((500, 400)) 
        pygame.display.set_caption("Enter Username")
        font = pygame.font.SysFont(None, 24)

        username = get_username(screen, font)
        client.send(json.dumps({"type": "join", "username": username}).encode('utf-8'))

        screen = pygame.display.set_mode((SCREEN_WIDTH + 300, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Connect Four - {username}")
        font = pygame.font.SysFont(None, 24)

        threading.Thread(target=receive_messages, daemon=True).start()

        running = True
        chat_input = ""
        while running:
            screen.fill(WHITE) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                
                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    if game_state["turn"] == username:
                        x_pos = event.pos[0]
                        if x_pos < SCREEN_WIDTH:  
                            col = int(x_pos / SQUARE_SIZE)
                            if 0 <= col < COLUMN_COUNT:
                                client.send(json.dumps({"type": "move", "column": col}).encode('utf-8'))

                if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                    mouse_x, mouse_y = event.pos
                    if 20 <= mouse_x <= 170 and 20 <= mouse_y <= 70: 
                        reset_game_state()
                        client.send(json.dumps({"type": "new_game"}).encode('utf-8'))
                    elif 200 <= mouse_x <= 350 and 20 <= mouse_y <= 70: 
                        running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if chat_input.strip(): 
                            client.send(json.dumps({"type": "chat", "message": chat_input.strip()}).encode('utf-8'))
                            chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    else:
                        chat_input += event.unicode

            render_board(screen)
            render_chat(screen, font, chat_input)

            if game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_game_hover = 20 <= mouse_x <= 170 and 20 <= mouse_y <= 70
                quit_hover = 200 <= mouse_x <= 350 and 20 <= mouse_y <= 70

                # Draw buttons
                draw_button(screen, "New Game", 20, 20, 150, 50, BLUE, WHITE, hover=new_game_hover)
                draw_button(screen, "Quit", 200, 20, 150, 50, RED, WHITE, hover=quit_hover)

                # Handle button clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_hover:
                        reset_game_state()
                        client.send(json.dumps({"type": "new_game"}).encode('utf-8'))
                    elif quit_hover:
                        running = False
                
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
