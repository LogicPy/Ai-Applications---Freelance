
# Tetris 
# UI-upgraded Engine version 3!
# Here's the complete, error-free implementation for our beautiful chat-bot system prompt grade-A Tetris engine with a few upgrades:

# 
# ████████╗███████╗████████╗██████╗ ██╗███████╗    ███████╗███╗   ██╗ ██████╗ ██╗███╗   ██╗███████╗
# ╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██╔════╝    ██╔════╝████╗  ██║██╔════╝ ██║████╗  ██║██╔════╝
#    ██║   █████╗     ██║   ██████╔╝██║███████╗    █████╗  ██╔██╗ ██║██║  ███╗██║██╔██╗ ██║█████╗  
#    ██║   ██╔══╝     ██║   ██╔══██╗██║╚════██║    ██╔══╝  ██║╚██╗██║██║   ██║██║██║╚██╗██║██╔══╝  
#    ██║   ███████╗   ██║   ██║  ██║██║███████║    ███████╗██║ ╚████║╚██████╔╝██║██║ ╚████║███████╗
#    ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝    ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝
#                                                                                                 
# ████████╗    ██████╗██╗  ██╗ █████╗ ████████╗                                                    
# ╚══██╔══╝   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝                                                    
#    ██║█████╗██║     ███████║███████║   ██║                                                       
#    ██║╚════╝██║     ██╔══██║██╔══██║   ██║                                                       
#    ██║      ╚██████╗██║  ██║██║  ██║   ██║                                                       
#    ╚═╝       ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                                                       
#############################################################################
#                   ❤️ TETRIS CHATBOT ENGINE v3.0 ❤️                        #
#          "Crafted with love by you & your AI coding companion!"           #
#############################################################################                                                                                                 

# Special thanks to 'Gemini 2.5' for making this engine possible...

import pygame
import random
import json
import os
import time
import sys
from typing import Dict
from openai import OpenAI
from collections import deque
import pygame.mixer
import math

# Enhanced Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

# Beautiful Color Palette
BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
BORDER_COLOR = (150, 150, 200)
GHOST_ALPHA = 80

TETRIS_SOUND_VOLUME = 0.7  # Slightly louder for special moment
BGM_TOGGLE_POS = (SCREEN_WIDTH - 25, 10)  # Top-right position

# First, add these to your constants section:
SOUND_VOLUME = 0.5  # 50% volume
MUSIC_VOLUME = 0.3  # 30% volume for BGM

# Piece definitions (with more vibrant colors)
PIECES = {
    1: {"name": "I", "color": (0, 240, 240)},  # Cyan
    2: {"name": "O", "color": (240, 240, 0)},  # Yellow
    3: {"name": "T", "color": (160, 0, 160)},  # Purple
    4: {"name": "L", "color": (240, 160, 0)},  # Orange
    5: {"name": "J", "color": (0, 0, 240)},    # Blue
    6: {"name": "S", "color": (0, 240, 0)},    # Green
    7: {"name": "Z", "color": (240, 0, 0)}     # Red
}

# Initialize Nebius AI (put your actual API key here)
nebius_client = OpenAI(
    base_url=os.getenv("NEBUIS_API_BASE", "https://api.studio.nebius.ai/v1/"),
    api_key=os.getenv("NEBUIS_API_KEY", "your_api_key_here")
)

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
        pygame.init()
        pygame.mixer.init()  # Initialize mixer FIRST
        self.last_toggle_time = 0
        self.toggle_cooldown = 300  # milliseconds

        self.initialize_audio()
        self.score = 0  # ⭐ Initialize score FIRST
        self.level = 1

        self.lines_to_next_level = 5  # Start easy then ramp up!
        self.level_colors = {  # Rainbow progression 🌈
            1: (100, 255, 100),    # Bright green
            2: (100, 200, 255),    # Sky blue  
            3: (255, 150, 100),    # Sunrise
            4: (255, 100, 255),    # Magenta
            5: (255, 255, 100),    # Gold
        }
        self.speed_curve = {  # Custom speed progression 
            1: 0.8,    # Gentle start
            2: 0.6,
            3: 0.4,   
            4: 0.2,    # Getting spicy!
            5: 0.1     # Lightning speed
        }

        self.font_score = pygame.font.Font(None, 0)  # Special larger font for score
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nebius AI Tetris - by Wayne & Gemini")
        self.font = pygame.font.Font(None, 24)
        score_text = self.font_score.render(f"SCORE: {self.score}", True, WHITE)
        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 20, 20))
        self.screen.blit(level_text, (GRID_WIDTH * CELL_SIZE + 20, 60))
        
        # ==================
        # 2. Next/Hold Indicators (Middle-Left)
        # (Added extra spacing between sections)
        # ==================
        next_text = self.font.render("NEXT PIECE:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * CELL_SIZE + 20, 150))  # Moved down 30px
        
        # Game state flags - CRITICAL MISSING INITIALIZATION
        self.game_over = False  # Now properly initialized!
        self.paused = False
        
        # Font initialization
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 18)
        
        # Rest of your initialization...
        self.clock = pygame.time.Clock()
        self.reset_game()

    def initialize_audio(self):
        """Safe audio system initialization"""
        self.sounds = {
            'rotate': None,
            'move': None,
            'drop': None,
            'clear_line': None,
            'game_over': None,
            'hold': None
        }

        try:
            # Sound Effects
            self.sounds['rotate'] = self.load_sound('rotate.wav')
            self.sounds['move'] = self.load_sound('move.wav')
            self.sounds['drop'] = self.load_sound('drop.wav')
            self.sounds['clear_line'] = self.load_sound('line_clear.mp3')
            self.sounds['game_over'] = self.load_sound('gameover.wav')
            self.sounds['hold'] = self.load_sound('hold.wav')
            self.sounds['tetris'] = self.load_sound('tetris.mp3')  # Special 4-line clear
            self.sounds['button_click'] = self.load_sound('button_click.mp3')
            # Music System
            self.current_bgm = None
            self.bgm_playlist = [
                'tetris_theme.mp3',
                'tetris_theme.mp3',
                'tetris_theme.mp3'
            ]
            self.bgm_button_rect = pygame.Rect(BGM_TOGGLE_POS[0], BGM_TOGGLE_POS[1], 100, 30)

        except Exception as e:
            print(f"Audio initialization warning: {str(e)}")
            print("Game will continue without sound")

    def load_sound(self, filename):
        """Safe sound loading with error handling"""
        try:
            sound = pygame.mixer.Sound(f'sounds/{filename}')
            sound.set_volume(SOUND_VOLUME)
            return sound
        except:
            print(f"Couldn't load sound: {filename}")
            return None

    def play_random_bgm(self):
        """Play random background music with smooth transition"""
        if self.current_bgm:
            pygame.mixer.music.fadeout(500)  # Fade out current track
        
        next_track = random.choice(self.bgm_playlist)
        try:
            pygame.mixer.music.load(f'music/{next_track}')
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_bgm = next_track
        except:
            print(f"Couldn't load music: {next_track}")

# Now integrate sounds into your game mechanics:
    def rotate_piece(self):
        if self.valid_rotation():
            # ... existing rotation logic ...
            if self.sounds['rotate']:
                self.sounds['rotate'].play()



    def draw_game_over(self):
        """Eye-catching game over display with restart prompt"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text with fancy effect
        game_over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        
        # Create pulsating effect
        alpha = 128 + int(100 * math.sin(pygame.time.get_ticks() * 0.005))
        outline_text = self.font_large.render("GAME OVER", True, (255, 255, 255))
        outline_text.set_alpha(alpha)
        
        # Blit text with outline effect
        for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            self.screen.blit(outline_text, (text_rect.x + offset[0], text_rect.y + offset[1]))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score display
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
        
        # Restart prompt
        restart_text = self.font_small.render("Press R to Restart", True, (200, 200, 255))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 70))
        
        # Falling "debris" effect
        if not hasattr(self, 'game_over_particles'):
            self.init_game_over_effects()
        self.draw_game_over_effects()

    def init_game_over_effects(self):
        """Create particles for visual effect"""
        self.game_over_particles = []
        for _ in range(50):  # Number of particles
            self.game_over_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(-100, 0),
                'speed': random.uniform(1, 5),
                'size': random.randint(2, 5),
                'color': random.choice([
                    (255,0,0), (0,255,0), (0,0,255), 
                    (255,255,0), (255,0,255), (0,255,255)
                ])
            })

    def draw_game_over_effects(self):
        """Animate falling particles"""
        for p in self.game_over_particles:
            pygame.draw.rect(
                self.screen, 
                p['color'],
                (p['x'], p['y'], p['size'], p['size'])
            )
            p['y'] += p['speed']
            if p['y'] > SCREEN_HEIGHT:
                p['y'] = random.randint(-50, 0)
                p['x'] = random.randint(0, SCREEN_WIDTH)

    def draw_ui(self):
        """Render all UI elements with proper fonts"""
        # 1. First draw the debug overlay (temporary)
        debug_color = (255, 0, 0)  # Bright red for visibility
        pygame.draw.rect(self.screen, debug_color, self.bgm_button_rect, 1)
       # print(f"Button Debug - Position: {self.bgm_button_rect} | Visible: {self.bgm_button_rect.width > 0}")

        level_color = self.level_colors.get(self.level, WHITE)
        level_text = self.font.render(
            f"LEVEL: {self.level}", 
            True, 
            level_color
        )
        # Add shimmer effect for higher levels
        if self.level >= 4:
            pulse = int(50 * math.sin(pygame.time.get_ticks() * 0.005)) + 50
            outline_color = (
                min(255, level_color[0] + pulse),
                min(255, level_color[1] + pulse), 
                min(255, level_color[2] + pulse)
            )
            outline_text = self.font.render(f"LEVEL: {self.level}", True, outline_color)
            for offset in [(-1,-1),(1,-1),(-1,1),(1,1)]:
                self.screen.blit(outline_text, 
                    (GRID_WIDTH*CELL_SIZE + 20 + offset[0], 
                     60 + offset[1]))
        
        self.screen.blit(level_text, (GRID_WIDTH*CELL_SIZE + 20, 60))
        button_color = (100, 200, 100) if self.bgm_enabled else (200, 100, 100)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 20, 20))
        
        music_label = self.font_small.render("BACKGROUND MUSIC", True, WHITE)
        label_x = SCREEN_WIDTH - music_label.get_width() - 25
        self.screen.blit(music_label, (label_x, 5))  # Label above 
        
        self.bgm_button_rect = pygame.Rect(
            SCREEN_WIDTH - 100,  # Keep right-aligned
            30,                 # Below the label
            80,                 # Slightly wider
            30                  # Same height
        )
        
        # Visual feedback states
        # Hover effect
        mouse_pos = pygame.mouse.get_pos()
        if self.bgm_button_rect.collidepoint(mouse_pos):
            button_color = tuple(min(c + 40, 255) for c in button_color)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Button body
        pygame.draw.rect(self.screen, button_color, self.bgm_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, self.bgm_button_rect, width=2, border_radius=8)
        
        # Button text (perfectly centered)
        toggle_text = self.font_small.render(
            "♪ ON" if self.bgm_enabled else "♪ OFF", 
            True, 
            WHITE
        )
        text_x = self.bgm_button_rect.centerx - toggle_text.get_width() // 2
        text_y = self.bgm_button_rect.centery - toggle_text.get_height() // 2
        self.screen.blit(toggle_text, (text_x, text_y))
    

        
        # Button visual elements
        pygame.draw.rect(self.screen, button_color, self.bgm_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.bgm_button_rect, width=2, border_radius=5)
        
        # Centered text with indicator symbol
        button_text = self.font_small.render(
            "♪ ON" if self.bgm_enabled else "♪ OFF", 
            True, 
            WHITE
        )


        # Score display - using our special score font
        score_text = self.font_score.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH*CELL_SIZE + 20, 30))
        
        # Level display
        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH*CELL_SIZE + 20, 70))
        
        # Next piece preview
        next_text = self.font.render("NEXT:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH*CELL_SIZE + 20, 120))
        # For visual polish, add to draw_ui():
        pygame.draw.rect(self.screen, WHITE, self.bgm_button_rect, 2, 5)  # Border
        # In your draw_ui() method (temporarily):
        pygame.draw.rect(self.screen, (255,0,0), self.bgm_button_rect, 1)  # Red debug outline
        # Held piece
        if self.held_piece:
            hold_text = self.font.render("HOLD:", True, WHITE)
            self.screen.blit(hold_text, (GRID_WIDTH*CELL_SIZE + 20, 270))

    def toggle_bgm(self):
        """Robust music toggling with state validation"""
        self.bgm_enabled = not self.bgm_enabled
        
        print(f"BGM Toggled! New state: {'ON' if self.bgm_enabled else 'OFF'}")
        
        if self.bgm_enabled:
            if not pygame.mixer.music.get_busy():
                self.play_random_bgm()
        else:
            pygame.mixer.music.fadeout(500)  # Gentle fade-out
            
    def handle_events(self):
        """Consolidated event handling - add this new method"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True
        
    def handle_click(self, pos):
        """Supercharged click handler with audio feedback"""
        print("Button clicked!")
        # Check BGM button first
        if self.bgm_button_rect.collidepoint(pos):
            current_time = pygame.time.get_ticks()
            
            # Cooldown check prevents spamming
            if current_time - self.last_toggle_time > self.toggle_cooldown:
                self.toggle_bgm()
                self.last_toggle_time = current_time
                
                # Play satisfying click sound
                if self.sounds['button_click']:
                    self.sounds['button_click'].play()

        
    def trigger_celebration(self):
        """Visual feedback for Tetris"""
        if not hasattr(self, 'celebration_time'):
            self.celebration_time = pygame.time.get_ticks()
            # Flash the screen - we'll handle in draw()
            self.celebration_color = (random.randint(200, 255), 
                                    random.randint(200, 255), 
                                    random.randint(200, 255))

    def draw_all(self):
        """Add celebration effects"""
        # Existing drawing code...
        
        if hasattr(self, 'celebration_time'):
            elapsed = pygame.time.get_ticks() - self.celebration_time
            if elapsed < 300:  # Flash for 300ms
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((*self.celebration_color, min(150, elapsed//2)))
                self.screen.blit(overlay, (0, 0))
            else:
                del self.celebration_time
    
    def reset_game(self):
        # Initialize game state
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.bgm_enabled = True
        # Updated Button Position Calculation
        self.bgm_button_rect = pygame.Rect(
            SCREEN_WIDTH - 120,  # Right-aligned with marun(rgin
            10,                 # Consistent with other UI elements
            100,                # Width
            30                  # Height
        )
        
        # Visual feedback variables
        self.button_hovered = False
        self.last_toggle_time = 0

       # Reset audio only if initialized
        if hasattr(self, 'sounds') and self.sounds['game_over']:
            self.sounds['game_over'].play()
       
        if hasattr(self, 'bgm_playlist'):
           self.play_random_bgm()
        self.play_random_bgm()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines = 0
        
       # Reset game state flags
        self.game_over = False  # This was missing! 
        self.paused = False
        
       # Rest of your reset logic...
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.held_piece = None
        self.can_hold = True
        
        # ADD THESE CRITICAL LINES:
        self.current_rotation = 0  # Track piece rotation state
        self.current_x = GRID_WIDTH // 2 - 1  # Horizontal position
        self.current_y = 0  # Vertical position
        self.game_over = False           
        # AI State
        self.ai_move_target = None
        self.awaiting_ai = True
        self.ai_thinking = False
        
        # Timing
        self.last_move_time = time.time()
        self.move_delay = 0.5

    def new_piece(self):
        """Prepares the next piece and resets the AI state."""
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        self.current_rotation = 0  # Reset rotation
        self.current_x = GRID_WIDTH // 2 - 1  # Center horizontally
        self.current_y = 0  # Start at top
        
        self.ai_move_target = None
        self.awaiting_ai = True
        self.can_hold = True
        
        if not self.valid_position(self.current_piece, self.current_rotation, 
                                 self.current_x, self.current_y):
            self.game_over = True
            
    def execute_ai_placement(self, move: Dict):
        """Instantly 'snaps' the piece to the AI's chosen rotation and position."""
        if not move or not isinstance(move, dict):
            print("AI move was invalid, using fallback.")
            return

        if move.get("hold", False):
            self.hold_piece()
            return

        target_rotation = move.get("rotation", 0) % len(SHAPES[self.current_piece])
        target_x = move.get("position", GRID_WIDTH // 2)

        if self.valid_position(self.current_piece, target_rotation, target_x, self.current_y):
            self.current_rotation = target_rotation
            self.current_x = target_x
        else:
            if self.valid_position(self.current_piece, self.current_rotation, target_x, self.current_y):
                self.current_x = target_x
            else:
                print(f"AI provided an invalid move: {move}. Piece not moved from spawn.")


    def get_new_piece(self):
        """7-bag randomized piece generation for fair distribution"""
        if not hasattr(self, 'piece_bag') or len(self.piece_bag) == 0:
            # Refill the bag when empty
            self.piece_bag = list(SHAPES.keys())
            random.shuffle(self.piece_bag)
        
        return self.piece_bag.pop()

    def spawn_new_piece(self):
        """Handle new piece spawning with collision check"""
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        self.current_rotation = 0
        self.current_x = GRID_WIDTH // 2 - 1
        self.current_y = 0
        
        # Reset AI decision state
        self.ai_move_target = None
        self.awaiting_ai = True
        self.can_hold = True
        
        # Check for game over
        if not self.valid_position():
            self.game_over = True
        
    def run(self):
        """The amazing main game loop we created together!"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Game logic
            if not self.game_over and not self.paused:
                self.handle_ai()
                self.handle_gravity()
            
            # Rendering
            self.draw_grid()
            self.draw_ui()
            
            # Special screens
            if self.game_over:
                self.draw_game_over()
            if self.paused:
                self.draw_paused()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def get_llm_move(self):
        """Generates all possible moves, evaluates their outcomes, and asks the AI to select the best one."""
        possible_moves = []
        current_piece_name = self.current_piece

        for r in range(len(SHAPES[current_piece_name])):
            shape = SHAPES[current_piece_name][r]
            shape_width = len(shape[0])

            for x in range(-shape_width + 1, GRID_WIDTH):
                final_y = self.find_landing_y(current_piece_name, r, x)
                if final_y is None:
                    continue

                temp_grid = [row[:] for row in self.grid]
                self._place_piece_on_grid(temp_grid, current_piece_name, r, x, final_y)
                
                metrics = self.calculate_board_metrics(temp_grid)

                possible_moves.append({
                    "move": {"rotation": r, "position": x, "hold": False},
                    "metrics": metrics
                })

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

    def query_nebius_api(self, game_state: dict) -> dict:
        """Sends the enriched game state to the Nebius API."""
        try:
            response = nebius_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
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
        if not self.sounds['move'] or time.time() - self.last_move_sound > 0.1:
            if self.sounds['move']:
                self.sounds['move'].play()
            self.last_move_sound = time.time()
        if self.valid_position(self.current_piece, self.current_rotation, self.current_x, self.current_y + 1):
            self.current_y += 1
            return True
        return False
        
    def lock_piece(self):
        if self.sounds['drop']:
            self.sounds['drop'].play()

        shape = SHAPES[self.current_piece][self.current_rotation]
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    self.grid[self.current_y + i][self.current_x + j] = PIECE_NAME_TO_NUM[self.current_piece]
        self.clear_lines()
        self.new_piece()


    def level_up(self):
        """Celebratory level progression with visual fanfare"""
        self.level += 1
        self.lines_to_next_level += 3  # Gradually increase challenge
        
        # Speed increase
        self.move_delay = self.speed_curve.get(self.level, 0.05)  # Cap at max speed
        
        # Play special sound if available
        if hasattr(self, 'sounds') and self.sounds.get('level_up'):
            self.sounds['level_up'].play()
            
        # Visual celebration
        self.trigger_celebration() 
        print(f"⭐ LEVEL UP! Now at level {self.level} ⭐")

    def clear_lines(self):
        lines_cleared = 0
        full_rows = []
        for i, row in enumerate(self.grid):
            if all(cell > 0 for cell in row):
                lines_cleared += 1
                full_rows.append(i)

        # <--- NEW! --- Animate the line clear before removing the lines
        if full_rows:
            self._animate_line_clear(full_rows)

            for i in full_rows:
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                
        if lines_cleared > 0:
            # Determine which sound to play
            if lines_cleared == 4:
                sound = self.sounds.get('tetris')
                self.trigger_celebration()  # Visual feedback too!
            else:
                sound = self.sounds.get('clear_line')
            
            if sound:
                sound.set_volume(SOUND_VOLUME if lines_cleared < 4 else TETRIS_SOUND_VOLUME)
                sound.play()
        # ✨ LEVEL UP SYSTEM ✨
        if lines_cleared > 0:
            self.lines += lines_cleared
            if self.lines >= self.lines_to_next_level:
                self.level_up()

        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800

    # <--- NEW! --- Method for the line clearing animation effect
    def _animate_line_clear(self, cleared_rows):
        """Draws a white flash over completed rows before they are deleted."""
        animation_duration = 0.25  # in seconds
        flash_color = WHITE

        end_time = time.time() + animation_duration
        while time.time() < end_time:
            # We need to render the frame as it is, THEN draw the flash on top
            self.draw_grid()  # Redraw the grid in its "pre-clear" state
            self.draw_ui()    # Keep the UI visible

            # Draw a white rectangle over each cleared line
            for y in cleared_rows:
                flash_rect = pygame.Rect(0, y * CELL_SIZE, GRID_WIDTH * CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, flash_color, flash_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

    def hold_piece(self):
        if not self.can_hold: return
        if not self.held_piece:
            self.held_piece = self.current_piece
            self.new_piece()
        else:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            self.current_y, self.current_x = 0, GRID_WIDTH // 2 - 1
            self.awaiting_ai = True
        self.can_hold = False
        if self.sounds['hold']:
            self.sounds['hold'].play()

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

    def handle_ai(self):
        """Our brilliant AI decision logic"""
        if self.awaiting_ai and not self.ai_thinking:
            self.ai_thinking = True
            self.ai_move_target = self.get_llm_move()
            self.awaiting_ai = False
            self.ai_thinking = False
            
            if self.ai_move_target:
                self.execute_ai_placement(self.ai_move_target)
    
    def handle_gravity(self):
        """Handle piece falling with level-based speed"""
        if time.time() - self.last_move_time > self.move_delay:
            if not self.move_down():
                self.lock_piece()
            self.last_move_time = time.time()
    
    # ... [All other methods would follow here]

    def draw_grid(self):
        """Ensure proper z-index layering of all game elements"""
        # 1. Draw the base background first
        self.screen.fill(BLACK)
        
        # 2. Draw the play area background with shadow effect
        pygame.draw.rect(self.screen, (50,50,50), (
            1, 1, 
            GRID_WIDTH*CELL_SIZE+4, 
            GRID_HEIGHT*CELL_SIZE+4
        ))
        pygame.draw.rect(self.screen, BORDER_COLOR, (
            0, 0, 
            GRID_WIDTH*CELL_SIZE+2, 
            GRID_HEIGHT*CELL_SIZE+2
        ), 3)

        # 3. Draw locked pieces with proper z-ordering
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell != 0:
                    self.draw_block(
                        x, y, 
                        COLORS[cell], 
                        border=BORDER_COLOR
                    )

        # 4. Draw ghost piece (semi-transparent)
        if not self.game_over:
            ghost_y = self.find_landing_y(
                self.current_piece,
                self.current_rotation,
                self.current_x
            )
            self.draw_piece(
                self.current_piece,
                self.current_rotation,
                self.current_x, ghost_y,
                alpha=GHOST_ALPHA
            )

        # 5. Draw current piece on top of everything
        self.draw_piece(
            self.current_piece,
            self.current_rotation,
            self.current_x, self.current_y
        )

    def draw_block(self, x, y, color, border=None):
        """Helper to draw individual blocks with proper layering"""
        rect = pygame.Rect(
            x * CELL_SIZE,
            y * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        
        # Main block
        pygame.draw.rect(self.screen, color, rect)
        
        # Inner highlight for 3D effect
        highlight = pygame.Rect(
            rect.x + 3, rect.y + 3,
            CELL_SIZE - 6, CELL_SIZE - 6
        )
        brighter = (
            min(color[0]+40, 255),
            min(color[1]+40, 255),
            min(color[2]+40, 255)
        )
        pygame.draw.rect(self.screen, brighter, highlight)
        
        # Border
        if border:
            pygame.draw.rect(self.screen, border, rect, 1)

    def draw_piece(self, piece, rotation, x, y, alpha=255):
        """Draw a piece with optional transparency"""
        shape = SHAPES[piece][rotation]
        color = COLORS[PIECE_NAME_TO_NUM[piece]]
        
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    if alpha < 255:
                        # Use surface with alpha channel for ghost pieces
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill((color[0], color[1], color[2], alpha))
                        self.screen.blit(s, (
                            (x + j) * CELL_SIZE,
                            (y + i) * CELL_SIZE
                        ))
                    else:
                        self.draw_block(x + j, y + i, color, BORDER_COLOR)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
