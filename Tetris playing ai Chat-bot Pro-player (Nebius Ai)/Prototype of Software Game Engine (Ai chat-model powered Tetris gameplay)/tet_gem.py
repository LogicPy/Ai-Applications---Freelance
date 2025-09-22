import pygame
import random
import json
import os
import time
from typing import Dict
from openai import OpenAI
from collections import deque

# Built by Wayne Kenney, DSv3 and Gemini 2.5
# A professional Tetris playing Chat-bot model hosted with Nebius's API system.
# Special thanks to Gemini for helping me figure out the rotation logic for our chat-bot's concluding placement decisions.

# Initialize pygame
pygame.init()

# Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

PIECES = {
    1: {"name": "I", "color": (0, 255, 255)}, 2: {"name": "O", "color": (255, 255, 0)},
    3: {"name": "T", "color": (128, 0, 128)}, 4: {"name": "L", "color": (255, 165, 0)},
    5: {"name": "J", "color": (0, 0, 255)},   6: {"name": "S", "color": (0, 255, 0)},
    7: {"name": "Z", "color": (255, 0, 0)}
}
PIECE_NAME_TO_NUM = {v["name"]: k for k, v in PIECES.items()}
COLORS = {k: v["color"] for k, v in PIECES.items()}
COLORS[0] = (0, 0, 0)
SHAPES = {
    'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    'O': [[[1, 1], [1, 1]]],
    'T': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
    'L': [[[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]], [[0, 0, 1], [1, 1, 1]]],
    'J': [[[0, 1], [0, 1], [1, 1]], [[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]]],
    'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]
}

# --- Nebius API Configuration ---
nebius_client = OpenAI(
    base_url=os.getenv("NEBUIS_API_BASE", "https://api.studio.nebius.ai/v1/"),
    api_key=os.getenv("NEBUIS_API_KEY", "YOUR_API_KEY_HERE")
)

# The beautiful key to our ai magic gameplay kingdom is in this lower region of text defined as a string variable
SYSTEM_PROMPT = """
You are a world-class Tetris AI. Your goal is to analyze a list of pre-calculated possible moves and select the single best one.

**Your Task:**
You will be provided with a JSON object containing a list under the key "possible_moves". Each item in the list represents a valid final placement for the current piece and includes:
- `move`: The `{"rotation": r, "position": x}` to execute.
- `metrics`: The calculated state of the board *after* the move is made (`holes`, `aggregate_height`, `bumpiness`).

**Decision-Making Hierarchy:**
1.  **SURVIVAL:** First, eliminate any move that results in a board height in any column reaching the top of the screen.
2.  **LINE CLEARS:** Prioritize moves that result in the most `lines_cleared`. A "Tetris" (4 lines) is the ultimate goal.
3.  **MINIMIZE HOLES:** From the remaining options, choose the one that results in the fewest `holes`.
4.  **MINIMIZE HEIGHT:** Next, prefer moves that result in a lower `aggregate_height`.
5.  **MAINTAIN A FLAT SURFACE:** Finally, choose the move with the lowest `bumpiness`.

**CRITICAL RESPONSE FORMAT:**
- Respond ONLY with the JSON object for the single best move you have selected from the list.
- Do not include any explanations, just the chosen `move` object.

**Example Response:**
```json
{"rotation": 1, "position": 4, "hold": false}
"""

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nebius AI Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = random.choice(list(SHAPES.keys()))
        self.next_piece = random.choice(list(SHAPES.keys()))
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.game_over = False

        # --- New AI state variables ---
        self.ai_move_target = None # Stores the AI's final decision for the current piece
        self.awaiting_ai = True    # Flag to tell the game loop we need a decision

        self.last_move_time = time.time()
        self.move_delay = 0.5  # Gravity speed
        self.new_piece()

    def new_piece(self):
        """Prepares the next piece and resets the AI state."""
        self.current_piece = self.next_piece
        self.next_piece = random.choice(list(SHAPES.keys()))
        self.current_rotation = 0
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0

        # Reset AI state for the new piece
        self.ai_move_target = None
        self.awaiting_ai = True
        self.can_hold = True

        if not self.valid_position(self.current_piece, self.current_rotation, self.current_x, self.current_y):
            self.game_over = True

    def execute_ai_placement(self, move: Dict):
        """Instantly 'snaps' the piece to the AI's chosen rotation and position."""
        if not move or not isinstance(move, dict):
            print("AI move was invalid, using fallback.")
            return

        # 1. Handle holding first
        if move.get("hold", False):
            self.hold_piece()
            return

        # 2. Get target rotation and horizontal position
        target_rotation = move.get("rotation", 0) % len(SHAPES[self.current_piece])
        target_x = move.get("position", GRID_WIDTH // 2)

        # 3. Validate and apply the move
        if self.valid_position(self.current_piece, target_rotation, target_x, self.current_y):
            self.current_rotation = target_rotation
            self.current_x = target_x
        else:
            # Simple fallback if AI gives a bad move: try just moving horizontally
            if self.valid_position(self.current_piece, self.current_rotation, target_x, self.current_y):
                self.current_x = target_x
            else:
                print(f"AI provided an invalid move: {move}. Piece not moved from spawn.")

    def run(self):
        """Main game loop with the new 'Decide and Snap' logic."""
        while True:
            current_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.reset_game()

            if not self.game_over:
                # === AI Decision Logic ===
                # If this piece needs a decision, get one.
                if self.awaiting_ai:
                    print("Requesting move from AI...")
                    self.ai_move_target = self.get_llm_move() # This is a blocking call
                    self.awaiting_ai = False # We have the decision now
                    print(f"AI decided: {self.ai_move_target}")

                    # As soon as we get the move, execute the placement!
                    if self.ai_move_target:
                        self.execute_ai_placement(self.ai_move_target)

                # === Gravity and Locking Logic ===
                # This part runs regardless of the AI, controlling the fall
                if current_time - self.last_move_time > self.move_delay:
                    if not self.move_down():
                        self.lock_piece()
                    self.last_move_time = current_time

            # --- Rendering ---
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_ui()
            if self.game_over:
                # Draw game over text
                pass
            pygame.display.flip()
            self.clock.tick(FPS)

    def get_llm_move(self):
        """Generates all possible moves, evaluates their outcomes, and asks the AI to select the best one."""
        possible_moves = []
        current_piece_name = self.current_piece

        # Iterate through each possible rotation
        for r in range(len(SHAPES[current_piece_name])):
            shape = SHAPES[current_piece_name][r]
            shape_width = len(shape[0])

            # Iterate through each possible horizontal position
            for x in range(-shape_width + 1, GRID_WIDTH):
                # Find where the piece would land
                final_y = self.find_landing_y(current_piece_name, r, x)
                if final_y is None:
                    continue # Invalid starting position

                # Simulate the move on a temporary grid
                temp_grid = [row[:] for row in self.grid]
                self._place_piece_on_grid(temp_grid, current_piece_name, r, x, final_y)
                
                # Calculate metrics for the outcome of this move
                metrics = self.calculate_board_metrics(temp_grid)

                possible_moves.append({
                    "move": {"rotation": r, "position": x, "hold": False},
                    "metrics": metrics
                })

        # Prepare the payload for the AI
        if not possible_moves:
            print("No possible moves found, falling back.")
            return {"rotation": 0, "position": GRID_WIDTH // 2, "hold": False}

        game_state_for_ai = {
            "current_piece": self.current_piece,
            "next_piece": self.next_piece,
            "possible_moves": possible_moves
        }
        
        print(f"Found {len(possible_moves)} possible moves. Asking AI to choose...")
        return self.query_nebius_api(game_state_for_ai)


    def find_landing_y(self, piece, rotation, x):
        """Finds the final Y position for a piece at a given X and rotation."""
        y = 0
        while self.valid_position(piece, rotation, x, y + 1):
            y += 1
        if not self.valid_position(piece, rotation, x, 0):
            return None
        return y

    def _place_piece_on_grid(self, grid, piece, rotation, x, y):
        """Places a piece on a given grid (for simulation purposes)."""
        shape = SHAPES[piece][rotation]
        piece_num = PIECE_NAME_TO_NUM[piece]
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    grid[y + i][x + j] = piece_num

    def calculate_board_metrics(self, grid_to_eval) -> Dict:
        """Calculates key metrics about a given board state."""
        heights = [0] * GRID_WIDTH
        lines_cleared = 0

        # Check for cleared lines
        full_rows = 0
        for y in range(GRID_HEIGHT):
            if all(cell != 0 for cell in grid_to_eval[y]):
                full_rows += 1
        lines_cleared = full_rows
        
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if grid_to_eval[y][x] != 0:
                    heights[x] = GRID_HEIGHT - y
                    break

        aggregate_height = sum(heights)
        holes = 0
        for x in range(GRID_WIDTH):
            col_height = heights[x]
            if col_height > 0:
                for y in range(GRID_HEIGHT - int(col_height), GRID_HEIGHT):
                    if grid_to_eval[y][x] == 0:
                        holes += 1

        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i+1])

        return {
            "lines_cleared": lines_cleared,
            "aggregate_height": aggregate_height,
            "holes": holes,
            "bumpiness": bumpiness
        }
                
    # Working version
    def query_nebius_api(self, game_state: dict) -> dict:
        """Sends the enriched game state to the Nebius API."""
        try:

            response = nebius_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324", # Or your preferred model
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    # Pass the whole dictionary directly!
                    {"role": "user", "content": json.dumps(game_state)}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=5.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"API Error or Timeout: {str(e)}. Falling back to a default move.")
            return {"rotation": 0, "position": GRID_WIDTH // 2, "hold": False}

    def valid_position(self, piece, rotation, x, y):
        shape = SHAPES[piece][rotation]
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    grid_x, grid_y = x + j, y + i
                    if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT and self.grid[grid_y][grid_x] == 0):
                        return False
        return True

    def move_down(self):
        if self.valid_position(self.current_piece, self.current_rotation, self.current_x, self.current_y + 1):
            self.current_y += 1
            return True
        return False
        
    def lock_piece(self):
        shape = SHAPES[self.current_piece][self.current_rotation]
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    self.grid[self.current_y + i][self.current_x + j] = PIECE_NAME_TO_NUM[self.current_piece]
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
            lines_cleared = 0
            full_rows = []
            for i, row in enumerate(self.grid):
                if all(cell > 0 for cell in row):
                    lines_cleared += 1
                    full_rows.append(i)

            for i in full_rows:
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

            # --- SCORING LOGIC ---
            if lines_cleared == 1:
                self.score += 100
            elif lines_cleared == 2:
                self.score += 300
            elif lines_cleared == 3:
                self.score += 500
            elif lines_cleared == 4: # A TETRIS!
                self.score += 800

    def hold_piece(self):
        if not self.can_hold: return
        if not self.held_piece:
            self.held_piece = self.current_piece
            self.new_piece()
        else:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            self.current_y, self.current_x = 0, GRID_WIDTH // 2 - 1
            self.awaiting_ai = True # IMPORTANT: need a new move for the swapped piece
        self.can_hold = False

    def draw_grid(self): # Dummy draw function
        self.screen.fill(BLACK)
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pygame.draw.rect(self.screen, COLORS[cell], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        shape = SHAPES[self.current_piece][self.current_rotation]
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    pygame.draw.rect(self.screen, COLORS[PIECE_NAME_TO_NUM[self.current_piece]], ((self.current_x + j)*CELL_SIZE, (self.current_y + i)*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_ui(self): # Dummy ui function
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 20, 20))


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
