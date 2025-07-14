import pygame as pg
import random
import heapq

pg.init()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Game variables
screen = pg.display.set_mode((900, 600), pg.RESIZABLE)
clock = pg.time.Clock()
run = True
pause = False
score = 0
computer_mode = False

# Snake
snake_head_position = []
snake = []
snake_direction = None
last_direction = None  # Used to store the last direction the snake was moving in
offset = 30  # Side length of each snake node, and of the fruit

# Fruit
fruit_position = []


class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, text_color=WHITE):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pg.font.Font('freesansbold.ttf', 24)
        self.hovered = False

    def draw(self, screen):
        color = LIGHT_GRAY if self.hovered else self.color
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)


def show_main_menu():
    global run, computer_mode

    # Create buttons
    button_width, button_height = 200, 50
    center_x = screen.get_width() // 2 - button_width // 2
    start_y = screen.get_height() // 2 - 100

    start_button = Button(center_x, start_y, button_width,
                          button_height, "Start Game")
    computer_button = Button(center_x, start_y + 70,
                             button_width, button_height, "Computer Plays")
    exit_button = Button(center_x, start_y + 140,
                         button_width, button_height, "Exit")

    menu_running = True
    while menu_running and run:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                menu_running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if start_button.is_clicked(mouse_pos):
                        computer_mode = False
                        menu_running = False
                    elif computer_button.is_clicked(mouse_pos):
                        computer_mode = True
                        menu_running = False
                    elif exit_button.is_clicked(mouse_pos):
                        run = False
                        menu_running = False

        # Update button hover states
        start_button.update_hover(mouse_pos)
        computer_button.update_hover(mouse_pos)
        exit_button.update_hover(mouse_pos)

        # Draw menu
        screen.fill(BLACK)

        # Title
        title_font = pg.font.Font('freesansbold.ttf', 48)
        title_text = title_font.render("Snake Game", True, GREEN)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_text, title_rect)

        # Draw buttons
        start_button.draw(screen)
        computer_button.draw(screen)
        exit_button.draw(screen)

        pg.display.update()
        clock.tick(60)


def computer_ai_move():
    global snake_direction

    head = tuple(snake_head_position)
    fruit = tuple(fruit_position)
    width = screen.get_width() // offset
    height = screen.get_height() // offset

    blocked = set((x // offset, y // offset) for x, y in snake)
    blocked.discard((fruit[0] // offset, fruit[1] // offset))

    reverse_dir = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}

    growing = head == fruit

    # Allow moving toward tail since it won't be occupied once snake is there
    if not growing:
        tail = (snake[-1][0] // offset, snake[-1][1] // offset)
        blocked.discard(tail)

    def neighbors(pos, incoming_dir):
        x, y = pos
        for dx, dy, dir in [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]:
            if incoming_dir and dir == reverse_dir[incoming_dir]:
                continue
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and (nx, ny) not in blocked:
                yield (nx, ny), dir

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_safe_move():
        current_pos = (head[0] // offset, head[1] // offset)
        for _, dir in neighbors(current_pos, snake_direction):
            return dir
        return None

    start = (head[0] // offset, head[1] // offset)
    goal = (fruit[0] // offset, fruit[1] // offset)

    frontier = []
    heapq.heappush(frontier, (heuristic(start, goal),
                   0, start, snake_direction, None))
    visited = set()

    move = None
    while frontier:
        _, cost, current, incoming_dir, first = heapq.heappop(frontier)
        if current == goal:
            move = first
            break
        for neighbor, dir in neighbors(current, incoming_dir):
            state = (neighbor, dir)
            if state not in visited:
                visited.add(state)
                heapq.heappush(frontier, (
                    cost + 1 + heuristic(neighbor, goal),
                    cost + 1,
                    neighbor,
                    dir,
                    dir if first is None else first
                ))

    # If no path found, try to find any safe move
    if not move:
        move = find_safe_move()

    # If there's no move at this point, the snake is trapped
    if move:
        snake_direction = move


def reset_game():
    global run, pause, snake_head_position, snake, snake_direction, last_direction, fruit_position, score

    # Reset game variables
    run = True
    pause = False
    score = 0

    # Reset snake variables
    snake_head_position = [300, 300]
    snake = [
        snake_head_position
    ]
    snake_direction = None
    last_direction = None

    # Reset fruit variables
    fruit_position = generate_fruit_position()


def render_snake():
    for node in snake:
        pg.draw.rect(screen, GREEN, (node[0], node[1], 30, 30))


def generate_fruit_position():
    while True:
        x = random.randint(1, (screen.get_width() // offset) - 2) * offset
        y = random.randint(1, (screen.get_height() // offset) - 2) * offset

        if [x, y] not in snake:
            break

    return [x, y]


def render_fruit():
    pg.draw.rect(screen, RED, (fruit_position[0], fruit_position[1], 30, 30))


def move_snake():
    global snake_head_position

    if snake_direction is None:
        return

    new_head_position = list(snake_head_position)

    if snake_direction == 'U':
        new_head_position[1] -= offset
    elif snake_direction == 'D':
        new_head_position[1] += offset
    elif snake_direction == 'R':
        new_head_position[0] += offset
    elif snake_direction == 'L':
        new_head_position[0] -= offset

    # Update the snake's head position
    snake.insert(0, new_head_position)
    snake_head_position = new_head_position


def check_fruit_eaten():
    global fruit_position, score

    if snake_head_position[0] == fruit_position[0] and snake_head_position[1] == fruit_position[1]:
        fruit_position = generate_fruit_position()
        render_fruit()
        score += 1
        return True
    else:
        return False


def check_wall_collision():
    if snake_head_position[0] <= 0 or snake_head_position[0] >= screen.get_width() - offset or snake_head_position[1] <= 0 or snake_head_position[1] >= screen.get_height() - offset:
        return True
    else:
        return False


def check_tail_collision():
    for i in range(1, len(snake)):
        if snake_head_position[0] == snake[i][0] and snake_head_position[1] == snake[i][1]:
            return True
    return False


def write_message_to_screen(text):
    font = pg.font.Font('freesansbold.ttf', 32)
    text = font.render(text, True, BLACK, GREEN)
    text_rect = text.get_rect()
    text_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
    screen.blit(text, text_rect)


def show_score():
    font = pg.font.Font('freesansbold.ttf', 25)
    text = font.render("Score: " + str(score), True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (screen.get_width() / 2, 25)
    screen.blit(text, text_rect)


def render_border(color=GREEN):
    pg.draw.rect(screen, color, (0, 0, screen.get_width(), 5))
    pg.draw.rect(screen, color, (0, 0, 5, screen.get_height()))
    pg.draw.rect(screen, color, (screen.get_width() -
                 5, 0, 5, screen.get_height()))
    pg.draw.rect(screen, color, (0, screen.get_height() -
                 5, screen.get_width(), 5))


def render_screen():
    screen.fill(BLACK)
    render_snake()
    render_fruit()
    render_border()
    show_score()

    if pause:
        write_message_to_screen('Paused. Press \'P\' to unpause')

    if computer_mode:
        # Show computer mode indicator
        font = pg.font.Font('freesansbold.ttf', 20)
        text = font.render("Computer Mode - Press ESC for menu", True, WHITE)
        screen.blit(text, (10, 10))

    pg.display.update()


def start():
    while run:
        show_main_menu()
        if run:
            reset_game()
            game_loop()


def game_loop():
    while run:
        if not handle_events():
            break

        if computer_mode and not pause:
            computer_ai_move()

        render_screen()
        clock.tick(25)

        if check_tail_collision() or check_wall_collision():
            render_border(RED)
            pg.display.update()
            pg.time.wait(1000)  # Show red border for 1 second
            break  # Return to main menu


def handle_events():
    global run, pause, snake_direction, last_direction

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            return False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False

    if snake_direction is not None:
        last_direction = snake_direction

    keys = pg.key.get_pressed()

    if keys[pg.K_p] and pause:
        snake_direction = last_direction
        pause = False

    if not pause and not computer_mode:  # Only allow manual control in human mode
        if (keys[pg.K_UP] or keys[pg.K_w]) and snake_direction != 'D':
            snake_direction = 'U'
        elif (keys[pg.K_DOWN] or keys[pg.K_s]) and snake_direction != 'U':
            snake_direction = 'D'
        elif (keys[pg.K_RIGHT] or keys[pg.K_d]) and snake_direction != 'L':
            snake_direction = 'R'
        elif (keys[pg.K_LEFT] or keys[pg.K_a]) and snake_direction != 'R':
            snake_direction = 'L'
        elif keys[pg.K_SPACE]:
            snake_direction = None
            pause = True
            return True

    move_snake()

    if not check_fruit_eaten():
        if len(snake) > 1:
            # Remove the last segment to simulate movement if fruit not eaten
            snake.pop()

    return True


if __name__ == '__main__':
    start()

pg.quit()
