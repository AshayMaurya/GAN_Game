import pygame
import random
import json
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 750, 750
GRID_SIZE = 15
CELL_SIZE = WIDTH // GRID_SIZE
FONT = pygame.font.SysFont("Arial", 18)
NUMBER_FONT = pygame.font.SysFont("Arial", 10)  # Smaller font for multiple visits

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Initialize screen
screen = pygame.display.set_mode((WIDTH + 200, HEIGHT))
pygame.display.set_caption("Player vs Game with Multi-Visit Tracking")


# Create the grid with strategic positioning
def create_grid():
    grid = [["empty" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Fixed start position at [0, 0]
    start_pos = (0, 0)

    # Determine end position in the bottom-right quadrant
    end_row = random.randint(GRID_SIZE // 2 + 2, GRID_SIZE - 1)
    end_col = random.randint(GRID_SIZE // 2 + 2, GRID_SIZE - 1)
    end_pos = (end_row, end_col)

    # Place green cells (targets)
    for _ in range(30):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty" and (row, col) not in [start_pos, end_pos]:
                grid[row][col] = "green"
                break

    # Place red cells (mines)
    for _ in range(40):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty" and (row, col) not in [start_pos, end_pos]:
                grid[row][col] = "red"
                break

    # Place blocked cells
    for _ in range(20):
        while True:
            row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[row][col] == "empty" and (row, col) not in [start_pos, end_pos]:
                grid[row][col] = "blocked"
                break

    # Mark end position
    grid[end_pos[0]][end_pos[1]] = "end"

    return grid, start_pos, end_pos


# Draw the grid with multi-visit tracking
def draw_grid(grid, player_pos, visited_cells, moves_count, score, traversal_cost):
    # Create a dictionary to track multiple visits
    visit_tracking = {}
    for idx, pos in enumerate(visited_cells):
        if pos not in visit_tracking:
            visit_tracking[pos] = []
        visit_tracking[pos].append(idx)

    # Draw game grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * CELL_SIZE, row * CELL_SIZE

            # Determine cell color
            if (row, col) == player_pos:
                color = BLUE
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

            # Draw visit numbers for cells
            if (row, col) in visit_tracking:
                # Concatenate visit numbers with comma
                visit_nums = visit_tracking[(row, col)]
                visit_text = ','.join(map(str, visit_nums))

                # Render the visit numbers
                number_text = NUMBER_FONT.render(visit_text, True, BLACK)
                number_rect = number_text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                screen.blit(number_text, number_rect)

    # Draw stats panel
    stats_x = WIDTH
    screen.fill(WHITE, (stats_x, 0, 200, HEIGHT))

    # Render stats text
    stats = [
        f"Moves: {moves_count}",
        f"Score: {score}",
        f"Traversal Cost: {traversal_cost}",
        f"Efficiency: {calculate_efficiency(score, traversal_cost):.2f}"
    ]

    for i, stat in enumerate(stats):
        text = FONT.render(stat, True, BLACK)
        screen.blit(text, (stats_x + 10, 50 + i * 50))


# Calculate game efficiency metric
def calculate_efficiency(score, traversal_cost):
    if traversal_cost == 0:
        return 0
    return score / traversal_cost


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
        visited_cells = [start_pos]
        moves = [start_pos]
        moves_count = 0

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

                            # Always add to visited cells
                            visited_cells.append(player_pos)

                            moves.append(player_pos)
                            moves_count += 1

                            # Traversal cost is 1 per each cell
                            traversal_cost += 1

                            # Update score based on cell type
                            if grid[player_pos[0]][player_pos[1]] == "green":
                                player_score += 10
                            elif grid[player_pos[0]][player_pos[1]] == "red":
                                player_score -= 5

                            # Check if player reaches the end
                            if player_pos == end_pos:
                                efficiency = calculate_efficiency(player_score, traversal_cost)
                                print(
                                    f"Game {game_num + 1} finished with score: {player_score}, Efficiency: {efficiency:.2f}")
                                game_data = {
                                    "game_num": game_num + 1,
                                    "start_pos": start_pos,
                                    "end_pos": end_pos,
                                    "moves": moves,
                                    "score": player_score,
                                    "traversal_cost": traversal_cost,
                                    "efficiency": efficiency,
                                    "moves_count": moves_count
                                }
                                all_games_data.append(game_data)
                                running = False
                                break

            # Draw the grid and player
            screen.fill(WHITE)
            draw_grid(grid, player_pos, visited_cells, moves_count, player_score, traversal_cost)
            pygame.display.flip()

    save_game_data(all_games_data)
    print("All games completed and saved to game_data.json.")
    pygame.quit()


if __name__ == "__main__":
    main()