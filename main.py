import pygame as pg
import random

pg.init()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game variables
screen = pg.display.set_mode((900, 600), pg.RESIZABLE)
clock = pg.time.Clock()
run = True
pause = False
score = 0

# Snake
snake_head_position = []
snake = []
snake_direction = None
last_direction = None  # Used to store the last direction the snake was moving in
offset = 30  # Side length of each snake node, and of the fruit

# Fruit
fruit_position = []


def reset_game():
    global run, pause, snake_head_position, snake, snake_direction, last_direction, fruit_position

    # Reset game variables
    run = True
    pause = False

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


def move_snake(add_node):
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

    # If the snake has eaten the fruit, keep the tail to grow the snake
    if not add_node:
        snake.pop()


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

    pg.display.update()


def start():
    global run
    reset_game()

    while run:
        handle_events()
        render_screen()
        clock.tick(25)

        if check_tail_collision() or check_wall_collision():
            render_border(RED)
            run = False
            game_over()


def handle_events():
    global run, pause, snake_direction, last_direction

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            return

    if snake_direction is not None:
        last_direction = snake_direction

    keys = pg.key.get_pressed()

    if keys[pg.K_p] and pause:
        snake_direction = last_direction
        pause = False

    if not pause:
        if keys[pg.K_UP] and snake_direction != 'D':
            snake_direction = 'U'
        elif keys[pg.K_DOWN] and snake_direction != 'U':
            snake_direction = 'D'
        elif keys[pg.K_RIGHT] and snake_direction != 'L':
            snake_direction = 'R'
        elif keys[pg.K_LEFT] and snake_direction != 'R':
            snake_direction = 'L'
        elif keys[pg.K_SPACE]:
            snake_direction = None
            pause = True
            return

    add_node = check_fruit_eaten()
    move_snake(add_node)


def game_over():
    write_message_to_screen(
        "Game over. Press ENTER to restart or ESC to exit")
    pg.display.update()

    deciding = True
    while deciding:
        clock.tick(10)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                deciding = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    reset_game()
                    deciding = False
                    break
                if event.key == pg.K_ESCAPE:
                    deciding = False
                    break


if __name__ == '__main__':
    start()

pg.quit()
