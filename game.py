import pygame
import math
import requests

pygame.init()

WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Traffic Controller")

#game variables
FPS = 60
planes = []
chat_history = []
game_started = False

def welcome_screen():
    # draw the welcome screen
    font = pygame.font.SysFont(None, 48)
    title_text = font.render("Welcome to Air Traffic Controller", True, (255, 255, 255))
    play_text = font.render("Press P to Play", True, (255, 255, 255))
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    WINDOW.blit(title_text, title_rect)
    WINDOW.blit(play_text, play_rect)
    WINDOW.blit(quit_text, quit_rect)
    pygame.display.update()

chat_history = []

def handle_input():
    global chat_history
    global game_started
    global planes

    if INPUT_TEXT:
        # send the message to the game
        chat_history.append("You: " + INPUT_TEXT)
        response_text = send_message(INPUT_TEXT)
        chat_history.append("AI: " + response_text)

        if not game_started:
            pygame.init()
            pygame.display.set_caption("Air Traffic Control")
            WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
            clock = pygame.time.Clock()
            all_sprites = pygame.sprite.Group()
            planes = generate_planes(NUM_PLANES)
            game_started = True
        else:

            # parse the user input to get the flight number and speed
            parts = INPUT_TEXT.split()
            flight_number = parts[0]
            speed = int(parts[3].replace("kts", ""))
            altitude = parts[3]
            direction = parts[2]

            # find the plane with the matching flight number
            for plane in planes:
                if plane.flight_number == flight_number:
                    # update the plane speed and print the response
                    chat_history.append("You: " + INPUT_TEXT)
                    response_text = "Reducing to {}kts {}".format(speed, flight_number)
                    chat_history.append("AI: " + response_text)
                    if plane.speed > speed:
                        plane.speed = speed
                    break

            for plane in planes:
                if plane.flight_number == flight_number:
                    # update the plane altitude and print the response
                    if direction == "climb":
                        chat_history.append("You: " + INPUT_TEXT)
                        response_text = "Climbing to {}ft {}".format(altitude, flight_number)
                        chat_history.append("AI: " + response_text)
                        plane.altitude = int(altitude)
                    elif direction == "descend":
                        chat_history.append("You: " + INPUT_TEXT)
                        response_text = "Descending to {}ft {}".format(altitude, flight_number)
                        chat_history.append("AI: " + response_text)
                        plane.altitude = int(altitude)
                    break
        INPUT_TEXT = ""  # clear the input field

def chat_screen():
    global INPUT_TEXT
    INPUT_TEXT = ""
    # set up the chat screen
    chat_font = pygame.font.SysFont(None, 24)
    chat_history = []
    input_text = ""
    input_rect = pygame.Rect(10, HEIGHT - 40, WIDTH - 20, 30)

    while True:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # user has pressed Enter, send the message and receive a response
                    response_text = send_message(INPUT_TEXT)
                    chat_history.append("You: " + input_text)
                    chat_history.append("AI: " + response_text)
                    input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    # user has pressed Escape, return to game mode
                    return

                # handle input field events
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_DELETE:
                    input_text = ""
                elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    pygame.scrap.init()
                    pygame.scrap.put(pygame.SCRAP_TEXT, input_text)
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    input_text += pygame.scrap.get(pygame.SCRAP_TEXT).decode("utf-8")

                # handle typing events
                else:
                    input_text += event.unicode

        # draw the chat screen
        WINDOW.fill((0, 0, 0))
        for i, text in enumerate(chat_history[-10:]):  # show only the last 10 messages
            text_surface = chat_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(10, 10 + i * 20))
            WINDOW.blit(text_surface, text_rect)
        pygame.draw.rect(WINDOW, (255, 255, 255), input_rect, 2)
        input_surface = chat_font.render(input_text, True, (255, 255, 255))
        input_rect.w = max(100, input_surface.get_width() + 10)
        WINDOW.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.display.update()

def draw_radar():
    # draw the radar circles
    pygame.draw.circle(WINDOW, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 100, 2)
    pygame.draw.circle(WINDOW, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 200, 2)
    pygame.draw.circle(WINDOW, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 300, 2)
    pygame.draw.circle(WINDOW, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 400, 2)
    pygame.draw.circle(WINDOW, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 500, 2)

    # draw the runway
    runway1 = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 5, 150, 10)
    runway2 = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 15, 150, 10)
    pygame.draw.rect(WINDOW, (255, 255, 255), runway1)
    pygame.draw.rect(WINDOW, (255, 255, 255), runway2)

def send_message(message):
    url = "https://some-chat-api.com/send_message"
    response = requests.post(url, data={"message": message})
    return response.text

all_sprites = pygame.sprite.Group()
planes = pygame.sprite.Group()

running = True
clock = pygame.time.Clock()

chat_mode = False

while running:
    if not game_started:
        welcome_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_started = True
                    # remove the welcome screen
                    WINDOW.fill((0, 0, 0))
                    pygame.display.update()
    else:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # user has pressed Enter, handle the input
                    handle_input()
                elif event.key == pygame.K_LEFT:
                    # switch to chat mode when the left arrow key is pressed
                    chat_mode = True
                    chat_screen()
                    chat_mode = False
                elif event.key == pygame.K_RIGHT:
                    # switch back to radar mode when the right arrow key is pressed
                    chat_mode = False

        # update the game objects
        all_sprites.update()

        # draw the game objects to the screen
        WINDOW.fill((0, 0, 0))
        draw_radar()
        if chat_mode:
            # draw the chat history on the screen
            # handled by chat_screen() function
            pass
        else:
            # draw the planes on the screen
            all_sprites.draw(WINDOW)
        pygame.display.update()

pygame.quit()