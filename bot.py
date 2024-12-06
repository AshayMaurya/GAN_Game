import pygame
import random
import json
import torch
import numpy as np
from typing import IO
from typing import TextIO
# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 750, 750
GRID_SIZE = 15
CELL_SIZE = WIDTH // GRID_SIZE
FONT = pygame.font.SysFont("Arial", 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DIM_RED = (139, 0, 0)  # Dimmed red for visited red cells
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bot vs Game with Traversal Costs")


# Create the grid
def create_grid():
    grid = [["empty" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Place green cells (targets)
    for _ in range(30):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty":
                grid[row][col] = "green"
                break

    # Place red cells (mines)
    for _ in range(40):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty":
                grid[row][col] = "red"
                break

    # Place blocked cells
    for _ in range(20):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty":
                grid[row][col] = "blocked"
                break

    # End position fixed at bottom-right
    grid[GRID_SIZE - 1][GRID_SIZE - 1] = "end"
    end_pos = (GRID_SIZE - 1, GRID_SIZE - 1)

    return grid, (0, 0), end_pos


# Draw the grid
def draw_grid(grid, player_pos, visited_reds):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            if (row, col) == player_pos:
                color = BLUE
            elif (row, col) in visited_reds:
                pygame.draw.circle(screen, DARK_BLUE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 5)
                color = DIM_RED
            elif grid[row][col] == "green":
                color = GREEN
            elif grid[row][col] == "red":
                color = RED
            elif grid[row][col] == "blocked":
                color = GRAY
            elif grid[row][col] == "end":
                color = BLACK
            else:
                color = WHITE
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)


# Load the trained generator model
class Generator(torch.nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.fc1 = torch.nn.Linear(42*2, 128)  # Flattened input of 42 moves, each with 2 coordinates (x, y)
        self.fc2 = torch.nn.Linear(128, 256)
        self.fc3 = torch.nn.Linear(256, 42*2)  # Output should also be of shape (42, 2) for moves

    def forward(self, z):
        x = torch.relu(self.fc1(z))
        x = torch.relu(self.fc2(x))
        x = torch.tanh(self.fc3(x))  # Use tanh for values in the range [-1, 1] for moves
        return x.view(-1, 42, 2)  # Reshape to (batch_size, 42, 2)

# Load the trained model
generator = Generator()
generator.load_state_dict(torch.load('generator.pth'))
generator.eval()  # Set to evaluation mode


# Function to generate a new sequence of moves
def generate_moves():
    z = torch.randn(1, 42*2)  # Sample random noise
    generated_moves = generator(z)  # Generate moves
    return generated_moves.detach().numpy()  # Convert to NumPy array


# Save the bot's moves and visited cells to a JSON file
# def save_bot_data(moves, visited_cells, filename="bot.json"):
#     bot_data = {
#         "moves": moves.tolist(),  # Convert NumPy array to list for JSON serialization
#         "visited_cells": visited_cells
#     }
#     with open(filename, 'w') as f:
#         json.dump(bot_data, f, indent=4)
#     print(f"Bot's moves and visited cells saved to {filename}")

# Save the bot's moves and visited cells to a JSON file
def save_bot_data(moves, visited_cells, filename="bot.json"):
    bot_data = {
        "moves": moves.tolist(),  # Convert NumPy array to list for JSON serialization
        "visited_cells": visited_cells
    }
    # Ensure proper type hinting for the file object
    with open(filename, 'w', encoding="utf-8") as file:  # Explicitly named 'file' for clarity
        json.dump(bot_data, file, indent=4)
    print(f"Bot's moves and visited cells saved to {filename}")


# Main game loop for bot
def play():
    grid, start_pos, end_pos = create_grid()
    player_pos = start_pos
    visited_reds = set()
    moves = []  # Initialize as a list to store the moves
    visited_cells = {}  # Dictionary to store visited cells serially
    serial_counter = 1  # Counter for marking visited cells serially
    generated_moves = generate_moves()  # Get generated moves
    move_idx = 0  # Keep track of the current move index

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if move_idx < len(generated_moves[0]):  # There are still moves to be made
            x, y = generated_moves[0][move_idx]  # Get the next move from the generated sequence

            # Convert to grid coordinates and move
            next_pos = (int(x * GRID_SIZE), int(y * GRID_SIZE))  # Scale to the grid size
            if 0 <= next_pos[0] < GRID_SIZE and 0 <= next_pos[1] < GRID_SIZE:
                if grid[next_pos[0]][next_pos[1]] != "blocked":
                    player_pos = next_pos
                    moves.append(player_pos)  # Append moves to the list

                    # Track visited cells serially
                    if player_pos not in visited_cells:
                        visited_cells[player_pos] = serial_counter
                        serial_counter += 1

                    # Update score and traversal cost (not needed for now, but could be used later)
                    if grid[player_pos[0]][player_pos[1]] == "green":
                        grid[player_pos[0]][player_pos[1]] = "empty"
                    elif grid[player_pos[0]][player_pos[1]] == "red":
                        visited_reds.add(player_pos)

                    # Check if player reaches the end
                    if player_pos == end_pos:
                        print(f"Bot finished the game!")
                        running = False
                        break

            move_idx += 1  # Move to the next move in the sequence

        # Draw the grid and player
        screen.fill(WHITE)
        draw_grid(grid, player_pos, visited_reds)
        pygame.display.flip()
        pygame.time.delay(500)  # Delay to slow down the bot's movement

    # Save the bot's moves and visited cells after the game ends
    save_bot_data(moves, visited_cells)
    pygame.quit()


if __name__ == "__main__":
    play()
