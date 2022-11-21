import pygame as pg
import random as r

# TODO:
# Make the fruit "Big Hero" themed
# Add thin border around the screen

pg.init()

screen = pg.display.set_mode((900, 600), pg.RESIZABLE)

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

snakeHeadPosition = [300, 300]

snake = [
    snakeHeadPosition
]

def renderSnake():
    for node in snake:
        pg.draw.rect(screen, GREEN, (node[0], node[1], 30, 30))

# There's a very small chance the fruit will render on the same block twice
# But honestly if you're that lucky, you deserve the extra point!
def generateFruitPosition():
    x = 0
    y = 0
    while x <= 30 or x >= screen.get_width() - 30:
        x = r.randint(0, ((screen.get_width() - 30) // 30)) * 30
    while y <= 30 or y >= screen.get_height() - 30:
        y = r.randint(0, ((screen.get_height() - 30) // 30)) * 30

    return [x, y]

# Set initial fruit position
fruitPosition = generateFruitPosition()

def renderFruit():
    pg.draw.rect(screen, RED, (fruitPosition[0], fruitPosition[1], 30, 30))

def moveSnake(addNode):
    if direction == 'U':
        snakeHeadPosition[1] -= offset
    elif direction == 'D':
        snakeHeadPosition[1] += offset
    elif direction == 'R':
        snakeHeadPosition[0] += offset
    elif direction == 'L':
        snakeHeadPosition[0] -= offset
    
    # Adds new node as head
    snake.insert(0, list(snakeHeadPosition))

    # If the snake has eaten the fruit, don't remove the tail
    # Otherwise, remove the tail
    # This simulates movement of the snake
    if (addNode == False):
        snake.pop()

def checkFruitEaten():
    # Retrieve value of fruitPosition
    global fruitPosition

    if snakeHeadPosition[0] == fruitPosition[0] and snakeHeadPosition[1] == fruitPosition[1]:
        fruitPosition = generateFruitPosition()
        renderFruit()
        return True
    else:
        return False

def checkWallCollision():
    if snakeHeadPosition[0] <= 0 or snakeHeadPosition[0] >= screen.get_width() - 30 or snakeHeadPosition[1] <= 0 or snakeHeadPosition[1] >= screen.get_height() - 30:
        return True
    else:
        return False

def checkTailCollision():
    for i in range (1, len(snake)):
        if snakeHeadPosition[0] == snake[i][0] and snakeHeadPosition[1] == snake[i][1]:
            return True
    return False

def writeMessage(text):
    # game over message
    font = pg.font.Font('freesansbold.ttf', 32)
    text = font.render(text, True, BLACK, GREEN)
    textRect = text.get_rect()
    textRect.center = (screen.get_width() // 2, screen.get_height() // 2)
    screen.blit(text, textRect)

def showScore():
    font = pg.font.Font('freesansbold.ttf', 32)
    text = font.render(str(len(snake) - 1), True, BLACK, GREEN)
    textRect = text.get_rect()
    textRect.center = (screen.get_width() - 15, 20)
    screen.blit(text, textRect)

# Doesn't care about turning 180 degrees tho...
def cheapAI():
    go = None
    
    if fruitPosition[1] > snakeHeadPosition[1]:
        go = 'D'
    else:
        go = 'U'

    if snakeHeadPosition[1] == fruitPosition[1]:
        if snakeHeadPosition[0] < fruitPosition[0]:
            go = 'R'
        else:
            go = 'L'
        
    return go
    
run = True
direction = None
offset = 30
pause = False
lastDirection = None

while run:
    pg.time.delay(50)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            break
    
    keys = pg.key.get_pressed()
    

    if keys[pg.K_UP] and direction != 'D':
        direction = 'U'
    elif keys[pg.K_DOWN] and direction != 'U':
        direction = 'D'
    elif keys[pg.K_RIGHT] and direction != 'L':
        direction = 'R'
    elif keys[pg.K_LEFT] and direction != 'R':
        direction = 'L'

    lastDirection = direction

    if keys[pg.K_SPACE] and not pause:
        direction = None
        pause = True

    if keys[pg.K_p] and pause:
        pause = False

    # AI navigation system at its finest
    # direction = cheapAI()

    if not pause:
        direction = lastDirection
        moveSnake(checkFruitEaten())
    else:
        writeMessage('Paused. Press \'P\' to unpause')
        pg.display.update()
        continue

    screen.fill(BLACK)
    showScore()
    renderSnake()
    renderFruit()
    pg.display.update()

    # Check if hit tail
    run = not checkTailCollision()
    # Check if hit wall
    if run:
        run = not checkWallCollision()
    
    # Check for exit condition (to display game over message)
    if not run:
        writeMessage("Game over")
        pg.display.update()
        pg.time.delay(1000)
    
    pg.event.clear()


pg.quit()