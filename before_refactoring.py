import pygame
import time
import random
import os
import sys

# Initialize pygame
pygame.init()
print(sys.getsizeof(pygame.init()))

# Game Variables
snake_speed = 10
window_x = 720
window_y = 480
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# Initialize game window
pygame.display.set_caption('Snake Game')
game_window = pygame.display.set_mode((window_x, window_y))
fps = pygame.time.Clock()

# Snake initial setup
snake_position = [100, 50]
snake_body = [[100, 50]]
fruit_position = [random.randrange(1, (window_x // 10)) * 10,
                  random.randrange(1, (window_y // 10)) * 10]
fruit_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0
growth_queue = 0
obstacles = []
paused = False

# High Score Management
high_score_file = "high_score.txt"

def save_high_score(score):
    if not os.path.exists(high_score_file):
        with open(high_score_file, "w") as file:
            file.write(str(score))
    else:
        with open(high_score_file, "r") as file:
            high_score = int(file.read())
        if score > high_score:
            with open(high_score_file, "w") as file:
                file.write(str(score))

def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            return int(file.read())
    return 0

high_score = load_high_score()

# Generate obstacles
def generate_obstacles(grid_width, grid_height, num_obstacles, snake_body, fruit_position):
    global obstacles
    while len(obstacles) < num_obstacles:
        obstacle = [random.randrange(1, (grid_width // 10)) * 10,
                    random.randrange(1, (grid_height // 10)) * 10]
        if obstacle not in snake_body and obstacle != fruit_position:
            obstacles.append(obstacle)

generate_obstacles(window_x, window_y, 5, snake_body, fruit_position)

# Display score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    score_rect.topleft = (10, 10)
    game_window.blit(score_surface, score_rect)

def show_high_score(color, font, size):
    high_score_font = pygame.font.SysFont(font, size)
    high_score_surface = high_score_font.render('High Score : ' + str(high_score), True, color)
    high_score_rect = high_score_surface.get_rect()
    high_score_rect.midtop = (window_x / 2, 20)
    game_window.blit(high_score_surface, high_score_rect)

# Game over function
def game_over():
    global score
    save_high_score(score)
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x / 2, window_y / 4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

# Flood-fill to validate reachability
def flood_fill(snake_body, fruit_position, grid_width, grid_height):
    visited = set()
    queue = [tuple(snake_body[0])]

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited or x < 0 or y < 0 or x >= grid_width or y >= grid_height or [x, y] in snake_body[1:]:
            continue
        visited.add((x, y))
        if (x, y) == tuple(fruit_position):
            return True
        queue.extend([(x-10, y), (x+10, y), (x, y-10), (x, y+10)])
    return False

# Toggle pause
def toggle_pause():
    global paused
    paused = not paused

# Main Function
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                change_to = 'UP'
            if event.key == pygame.K_DOWN and direction != 'UP':
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT and direction != 'RIGHT':
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT and direction != 'LEFT':
                change_to = 'RIGHT'
            if event.key == pygame.K_p:  # Pause game
                toggle_pause()

    if paused:
        continue

    # Update direction
    direction = change_to

    # Move snake
    if direction == 'UP':
        snake_position[1] -= 10
    if direction == 'DOWN':
        snake_position[1] += 10
    if direction == 'LEFT':
        snake_position[0] -= 10
    if direction == 'RIGHT':
        snake_position[0] += 10

    # Wall wrapping (should this be removed so that wall hits are also game over?)
    #snake_position[0] %= window_x
    #snake_position[1] %= window_y

    # Snake growth
    if snake_position == fruit_position:
        score += 10
        fruit_spawn = False
        growth_queue += 3
    if growth_queue > 0:
        snake_body.insert(0, list(snake_position))
        growth_queue -= 1
    else:
        snake_body.insert(0, list(snake_position))
        snake_body.pop()

    # Spawn fruit
    if not fruit_spawn:
        fruit_position = [random.randrange(1, (window_x // 10)) * 10,
                          random.randrange(1, (window_y // 10)) * 10]
        fruit_spawn = True

    # Check if fruit is reachable
    if not flood_fill(snake_body, fruit_position, window_x, window_y):
        game_over()

    # Collision with itself or obstacles
    if snake_position in snake_body[1:] or snake_position in obstacles:
        game_over()

    # Draw game elements
    game_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    for obstacle in obstacles:
        pygame.draw.rect(game_window, red, pygame.Rect(obstacle[0], obstacle[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

    # Display scores
    show_score(1, white, 'times new roman', 20)
    show_high_score(white, 'times new roman', 20)

    # Update screen
    pygame.display.update()

    # Control game speed
    fps.tick(10 + (score // 20))

print(sys.getsizeof(size))