import pygame
import random
import json

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
pygame.display.set_caption("Player vs Game with Traversal Costs")


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


# Save game data
def save_game_data(data, file_path="game_data.json"):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


# Main game loop
def main():
    # Reset the JSON file
    save_game_data([])

    all_games_data = []
    for game_num in range(5):
        grid, start_pos, end_pos = create_grid()
        player_pos = start_pos
        player_score = 0
        traversal_cost = 0
        visited_reds = set()
        moves = []

        print(f"Game {game_num + 1} starting...")
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game_data(all_games_data)
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    next_pos = None
                    if event.key == pygame.K_UP:
                        next_pos = (player_pos[0] - 1, player_pos[1])
                    elif event.key == pygame.K_DOWN:
                        next_pos = (player_pos[0] + 1, player_pos[1])
                    elif event.key == pygame.K_LEFT:
                        next_pos = (player_pos[0], player_pos[1] - 1)
                    elif event.key == pygame.K_RIGHT:
                        next_pos = (player_pos[0], player_pos[1] + 1)

                    if next_pos and 0 <= next_pos[0] < GRID_SIZE and 0 <= next_pos[1] < GRID_SIZE:
                        if grid[next_pos[0]][next_pos[1]] != "blocked":
                            player_pos = next_pos
                            moves.append(player_pos)

                            # Update score and traversal cost
                            if grid[player_pos[0]][player_pos[1]] == "green":
                                player_score += 10
                                traversal_cost += 1
                                grid[player_pos[0]][player_pos[1]] = "empty"
                            elif grid[player_pos[0]][player_pos[1]] == "red":
                                if player_pos not in visited_reds:
                                    player_score -= 5
                                    traversal_cost += 3
                                    visited_reds.add(player_pos)
                            else:
                                traversal_cost += 2

                            # Check if player reaches the end
                            if player_pos == end_pos:
                                print(f"Game {game_num + 1} finished with score: {player_score}")
                                game_data = {
                                    "game_num": game_num + 1,
                                    "start_pos": start_pos,
                                    "end_pos": end_pos,
                                    "moves": moves,
                                    "score": player_score,
                                    "traversal_cost": traversal_cost,
                                }
                                all_games_data.append(game_data)
                                running = False
                                break

            # Draw the grid and player
            screen.fill(WHITE)
            draw_grid(grid, player_pos, visited_reds)
            pygame.display.flip()

    save_game_data(all_games_data)
    print("All games completed and saved to game_data.json.")
    pygame.quit()


if __name__ == "__main__":
    main()
