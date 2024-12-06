# import pygame
# import random
#
# # Initialize Pygame
# pygame.init()
#
# # Screen settings
# WIDTH, HEIGHT = 600, 600
# GRID_SIZE = 10  # 10x10 grid
# CELL_SIZE = WIDTH // GRID_SIZE
# FONT = pygame.font.SysFont("Arial", 24)
#
# # Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)
# BLUE = (0, 0, 255)
# YELLOW = (255, 255, 0)
#
# # Initialize screen
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Interactive Minesweeper Chain Reaction Game")
#
#
# # Create game grid
# def create_grid():
#     grid = []
#     for _ in range(GRID_SIZE):
#         row = []
#         for _ in range(GRID_SIZE):
#             row.append(random.choice(["green", "red"]))  # Randomly assign green or red
#         grid.append(row)
#     return grid
#
#
# # Draw the grid
# def draw_grid(grid, clicked, path):
#     for row in range(GRID_SIZE):
#         for col in range(GRID_SIZE):
#             x, y = col * CELL_SIZE, row * CELL_SIZE
#             if (row, col) in path:
#                 color = BLUE  # Path traced by the player
#             elif (row, col) in clicked:
#                 color = YELLOW if grid[row][col] == "green" else RED  # Correct or incorrect click
#             else:
#                 color = WHITE  # Unvisited cells
#             pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
#             pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
#
#
# # Display messages
# def display_text(text, color, x, y):
#     label = FONT.render(text, True, color)
#     screen.blit(label, (x, y))
#
#
# # Main game loop
# def main():
#     grid = create_grid()
#     clicked = []  # Stores all clicked cells
#     path = []  # Stores the player's path
#     score = 0
#     running = True
#     message = "Click a cell to start!"
#
#     while running:
#         screen.fill(WHITE)
#
#         # Handle events
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 x, y = pygame.mouse.get_pos()
#                 col, row = x // CELL_SIZE, y // CELL_SIZE
#
#                 if (row, col) not in clicked:
#                     clicked.append((row, col))
#                     path.append((row, col))
#
#                     if grid[row][col] == "green":
#                         score += 10
#                         message = f"Good move! Score: {score}"
#                     elif grid[row][col] == "red":
#                         score -= 5
#                         message = f"Wrong move! Score: {score}"
#
#         # Draw grid and path
#         draw_grid(grid, clicked, path)
#
#         # Display messages and score
#         display_text(message, BLACK, 10, HEIGHT - 50)
#         display_text(f"Score: {score}", BLACK, WIDTH - 150, HEIGHT - 50)
#
#         # Update screen
#         pygame.display.flip()
#
#     pygame.quit()
#     print("Game Over! Final Score:", score)
#
#
# if __name__ == "__main__":
#     main()
