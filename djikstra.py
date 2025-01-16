import pygame
import time
import random
import os
import sys  # For memory measurement
from heapq import heappop, heappush

# Initialize pygame
pygame.init()

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
pygame.display.set_caption('Snake Game with AI')
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
ai_mode = False  # AI mode toggle

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

# Display complexity metrics
def show_complexity_metrics(frame_count, memory_usage, color, font, size):
    complexity_font = pygame.font.SysFont(font, size)
    complexity_surface = complexity_font.render(
        f'Time Complexity (Frames): {frame_count} | Space Complexity (Bytes): {memory_usage}', True, color
    )
    complexity_rect = complexity_surface.get_rect()
    complexity_rect.topleft = (10, 40)  # Position below the score
    game_window.blit(complexity_surface, complexity_rect)

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

# Dijkstra's Algorithm to find the shortest path
def dijkstra_move(snake_position, snake_body, fruit_position, grid_width, grid_height, obstacles):
    # Initialize the grid and priority queue
    grid_width //= 10
    grid_height //= 10
    start = (snake_position[0] // 10, snake_position[1] // 10)
    goal = (fruit_position[0] // 10, fruit_position[1] // 10)
    queue = []
    heappush(queue, (0, start))
    distances = {start: 0}
    previous_nodes = {start: None}
    visited = set()

    # Obstacles and snake body as blocked nodes
    blocked = set((x // 10, y // 10) for x, y in obstacles + snake_body)

    # Directions for movement
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current_distance, current_node = heappop(queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        # Stop if we reach the goal
        if current_node == goal:
            break

        # Explore neighbors
        for dx, dy in directions:
            neighbor = (current_node[0] + dx, current_node[1] + dy)
            if 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height and neighbor not in blocked:
                distance = current_distance + 1  # Constant weight
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heappush(queue, (distance, neighbor))

    # Reconstruct path
    path = []
    node = goal
    while node and node != start:
        path.append(node)
        node = previous_nodes.get(node)
    path.reverse()

    # Determine the next move
    if path:
        next_node = path[0]
        if next_node[0] < start[0]:
            return 'LEFT'
        elif next_node[0] > start[0]:
            return 'RIGHT'
        elif next_node[1] < start[1]:
            return 'UP'
        elif next_node[1] > start[1]:
            return 'DOWN'

    # Default to current direction if no path found
    return direction

# Main Function
frame_count = 0  # To measure time complexity

while True:
    # Calculate memory usage (space complexity)
    memory_usage = (
        sys.getsizeof(snake_body) +
        sys.getsizeof(obstacles) +
        sys.getsizeof(fruit_position) +
        sys.getsizeof(snake_position)
    )

    # Event handling
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
                paused = not paused
            if event.key == pygame.K_a:  # Toggle AI
                ai_mode = not ai_mode

    if paused:
        continue

    # Use AI if enabled
    if ai_mode:
        change_to = dijkstra_move(snake_position, snake_body, fruit_position, window_x, window_y, obstacles)

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

    # Wall collision (Game over)
    if snake_position[0] < 0 or snake_position[0] >= window_x or snake_position[1] < 0 or snake_position[1] >= window_y:
        game_over()

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

    # Display scores and complexity metrics
    show_score(1, white, 'times new roman', 20)
    show_high_score(white, 'times new roman', 20)
    show_complexity_metrics(frame_count, memory_usage, white, 'times new roman', 20)

    # Update screen
    pygame.display.update()

    # Control game speed
    fps.tick(10 + (score // 20))

    # Increment frame count for time complexity
    frame_count += 1
