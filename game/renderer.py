from collections import deque
import pygame
from game.block import Block
from game.board import Board
from game.game_logic import GameLogic
from game.input_handler import InputHandler
from game.state_adapter import block_to_state, update_block_from_state
from game.transition import create_board_for_state, is_goal_state, transition
from search_algorithms import Problem
from search_algorithms import a_star
from search_algorithms import breadth_first_search
from search_algorithms import depth_first_search
from search_algorithms import greedy_search
from search_algorithms import iterative_deepening_search
from search_algorithms import uniform_cost_search
from search_algorithms import run_search

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (51, 51, 255)  # grid
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)  # new path discovered by button
PURPLE = (128, 0, 128)  # button
TRANSPARENT_BLUE = (0, 0, 255, 128)  # glass floor
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)  # sky
HOT_PINK = (255, 0, 127)  # block
WHITE_CLOUD = (204, 255, 204)  # clouds
ORANGE = (255, 165, 0)  # split switch / active cube
INACTIVE_CUBE = (255, 105, 180)

# Game states
MAIN_MENU = 0
RULES = 1
LEVEL_SELECT = 2
PLAYING = 3
GAME_OVER = 4
LEVEL_COMPLETE = 5
AI_OR_HUMAN = 6
ALGORITHMS_LEVEL_SELECT = 7
ALGORITHMS = 8
AI_PLAYING = 9
AI_LEVEL_COMPLETE = 10


# All buttons shape and color
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# Running the game itself
class Renderer:
    def __init__(self, block, board, game_logic, input_handler):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roll the Block!")
        self.clock = pygame.time.Clock()
        self.game_state = MAIN_MENU
        self.block = block
        self.board = board
        self.game_logic = game_logic
        self.input_handler = input_handler
        self.init_buttons()
        self.running = True
        self.algorithm = None
        self.solution = None
        self.algorithm_completed = False
        self.search_result = None
        self.level_name = None
        self.current_level = None
        self.current_state = block_to_state(block, board)
        self.move_count = 0

        self.animation_active = False
        self.animation_direction = None
        self.animation_progress = 0
        self.animation_speed = 0.1
        self.old_block_position = None
        self.target_block_position = None

    def init_buttons(self):
        center_x = SCREEN_WIDTH // 2
        # Main menu
        self.play_button = Button(center_x - 100, 200, 200, 50, "Play", WHITE_CLOUD, (204, 255, 204))
        self.rules_button = Button(center_x - 100, 270, 200, 50, "Rules", WHITE_CLOUD, (204, 255, 204))
        # AI or Human
        self.human_button = Button(center_x - 250, 200, 200, 50, "Human", WHITE_CLOUD, (204, 255, 204))
        self.ai_button = Button(center_x + 70, 200, 200, 50, "AI", WHITE_CLOUD, (204, 255, 204))

        # Back from rules
        self.back_button = Button(center_x - 100, 500, 200, 50, "Back", WHITE_CLOUD, (204, 255, 204))

        # Search algorithms
        self.solve_button = Button(20, 100, 100, 40, "Solve", WHITE_CLOUD, (204, 255, 204))
        self.algorithm_buttons = []
        algorithms = ["A*", "BFS", "DFS", "Greedy", "UCS", "IDS"]
        for i, algo in enumerate(algorithms):
            self.algorithm_buttons.append(Button(SCREEN_WIDTH // 2 - 70, 100 + i*50, 100, 40, algo, CYAN, (100, 255, 255)))

        # Level select buttons: LEVEL1 ... LEVEL10
        self.level_buttons = []
        for index in range(10):
            row = index // 5
            column = index % 5
            level_num = index + 1
            x = 25 + column * 155
            y = 150 + row * 130
            self.level_buttons.append(
                Button(
                    x,
                    y,
                    130,
                    80,
                    f"Level {level_num}",
                    CYAN,
                    (100, 255, 255),
                )
            )

        # Game buttons
        self.menu_button = Button(SCREEN_WIDTH - 120, 20, 100, 40, "Menu", WHITE_CLOUD, (204, 255, 204))
        self.restart_button = Button(SCREEN_WIDTH - 120, 70, 100, 40, "Restart", WHITE_CLOUD, (204, 255, 204))
        self.next_level_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "Next Level", BLUE, (51, 51, 255))
        self.retry_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, "Try Again", YELLOW, (225, 255, 100))

    def initialize_level(self, level_name, AI=False):
        self.current_level = level_name
        self.board = Board(level_name)

        x, y = self.board.level.start
        self.block = Block(x, y)
        self.game_logic = GameLogic(self.block, self.board)
        self.input_handler = InputHandler(
            self.block,
            self.board,
            self.game_logic,
            self,
        )

        self.board.refresh_layout(self.block)
        self.current_state = block_to_state(
            self.block,
            self.board,
        )
        self.move_count = 0

        if not AI:
            self.solution = None
            self.algorithm_completed = False
            self.search_result = None
        elif not self.algorithm_completed:
            self.search_result = None

        self._sync_view_from_state()
        self.calculate_camera_offset()

        if AI and not self.algorithm_completed:
            layout_only = not bool(self.board.level.button)
            problem = Problem(
                self.block,
                self.board,
                layout_only=layout_only,
            )

            solver_map = {
                "a*": ("A*", a_star),
                "bfs": ("BFS", breadth_first_search),
                "dfs": ("DFS", depth_first_search),
                "greedy": ("Greedy", greedy_search),
                "ucs": ("UCS", uniform_cost_search),
                "ids": ("IDS", iterative_deepening_search),
            }

            if self.algorithm not in solver_map:
                raise ValueError(
                    f"Unsupported algorithm: {self.algorithm!r}"
                )

            algorithm_name, solver = solver_map[self.algorithm]

            self.search_result = run_search(
                algorithm_name,
                solver,
                problem,
            )

            print(self.search_result.as_dict())

            if self.search_result.solved:
                self.solution = deque(
                    self.search_result.actions
                )
            else:
                self.solution = None

            self.algorithm_completed = True

    def _sync_view_from_state(self):
        """
        Synchronize the legacy Board/Block objects with current_state.

        The search/game rules use immutable GameState. The old objects are kept
        only so the existing menu and GameLogic structure continue to work.
        """
        state_board = create_board_for_state(
            self.current_level,
            self.current_state,
        )

        # Keep the same Board object because other objects hold references to it.
        self.board.level = state_board.level

        if not self.current_state.is_split:
            update_block_from_state(
                self.block,
                self.current_state,
            )

        if hasattr(self.block, "move_counter"):
            self.block.move_counter = self.move_count

    def apply_game_action(self, action):
        """
        Apply one human or AI action through the shared transition engine.
        """
        try:
            next_state = transition(
                self.current_state,
                action,
                self.current_level,
            )
        except ValueError:
            # Example: pressing SPACE while the block is not split.
            return False

        if next_state is None:
            self.game_logic.game_over = True
            return False

        self.current_state = next_state
        self.move_count += 1
        self._sync_view_from_state()

        if is_goal_state(
            self.current_state,
            self.current_level,
        ):
            self.game_logic.level_completed = True

        return True

    def calculate_camera_offset(self):
        level_pixel_width = len(self.board.level.layout[0]) * TILE_SIZE
        level_pixel_height = len(self.board.level.layout) * TILE_SIZE
        self.camera_offset_x = (SCREEN_WIDTH - level_pixel_width) // 2
        self.camera_offset_y = (SCREEN_HEIGHT - level_pixel_height) // 2

    def draw(self):
        self.screen.fill(LIGHT_BLUE)

        if self.game_state == MAIN_MENU:
            self.draw_main_menu()
        elif self.game_state == AI_OR_HUMAN:
            self.draw_ai_or_human()
        elif self.game_state == ALGORITHMS:
            self.draw_algorithms()
        elif self.game_state == RULES:
            self.draw_rules_screen()
        elif self.game_state == LEVEL_SELECT or self.game_state == ALGORITHMS_LEVEL_SELECT:
            self.draw_level_select()
        elif self.game_state == PLAYING or self.game_state == AI_PLAYING:
            self.draw_level()
        elif self.game_state == GAME_OVER:
            self.draw_level()
            self.draw_game_over()
        elif self.game_state == LEVEL_COMPLETE or self.game_state == AI_LEVEL_COMPLETE:
            self.draw_level()
            self.draw_level_complete()

        pygame.display.flip()

    # GAME STATE 0 - MAIN_MENU
    def handle_main_menu(self, mouse_pos):
        self.play_button.update(mouse_pos)
        self.rules_button.update(mouse_pos)

        if self.play_button.is_clicked(mouse_pos):
            self.game_state = AI_OR_HUMAN
        elif self.rules_button.is_clicked(mouse_pos):
            self.game_state = RULES

    def draw_main_menu(self):
        # Draw title
        font = pygame.font.Font(None, 72)
        title = font.render("Roll the Block", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        # Draw buttons
        self.play_button.draw(self.screen)
        self.rules_button.draw(self.screen)

    # GAME_STATE 1 - RULES
    def handle_rules_screen(self, mouse_pos):
        self.back_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

    def draw_rules_screen(self):
        # Draw title
        font = pygame.font.Font(None, 40)
        title = font.render("Game Rules", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        rules = [
            "MOVEMENT KEYS: WASD or ARROWS",
            "SPACE: switch the active cube after splitting",
            "",
            "BLOCK STATES:",
            "   - Upright: cannot stand on fragile glass",
            "   - Horizontal/Vertical: occupies two cells",
            "   - Split: control one cube at a time",
            "",
            "GAME ELEMENTS:",
            "   - Blue: regular floor",
            "   - Green: goal",
            "   - Cyan: fragile/glass floor",
            "   - Yellow/Purple: bridge switches",
            "   - Orange: split switch",
            "   - Black: void or closed bridge",
        ]

        font = pygame.font.Font(None, 24)
        for i, line in enumerate(rules):
            text = font.render(line, True, BLACK)
            self.screen.blit(text, (100, 120 + i * 25))

        # Draw back button
        self.back_button.draw(self.screen)

    # GAME_STATE 2 - LEVEL_SELECT
    def handle_level_select(self, mouse_pos):
        self.back_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

        for i, button in enumerate(self.level_buttons):
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos):
                self.level_name = f"LEVEL{i+1}"
                if self.game_state == ALGORITHMS_LEVEL_SELECT:
                    self.game_state = ALGORITHMS
                else:
                    self.initialize_level(self.level_name)
                    self.game_state = PLAYING

    def draw_level_select(self):
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Select Level", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        # Draw level buttons
        for button in self.level_buttons:
            button.draw(self.screen)

        # Draw back button
        self.back_button.draw(self.screen)

    # GAME_STATE 3 - PLAYING
    def handle_playing(self, mouse_pos):
        self.menu_button.update(mouse_pos)
        self.restart_button.update(mouse_pos)

        if self.menu_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU
        elif self.restart_button.is_clicked(mouse_pos):
            self.initialize_level(self.current_level)

        if self.game_logic.game_over:
            self.game_state = GAME_OVER

    # GAME_STATE 4 - GAME_OVER
    def handle_game_over(self, mouse_pos):
        self.restart_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)
        self.retry_button.update(mouse_pos)

        if self.retry_button.is_clicked(mouse_pos):
            self.initialize_level(self.current_level)
            self.game_state = PLAYING
        elif self.menu_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        font = pygame.font.Font(None, 72)
        text = font.render("Game Over", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 -50))
        self.screen.blit(text, text_rect)

        # Buttons
        self.retry_button.draw(self.screen)

    # GAME_STATE 5 - LEVEL_COMPLETE
    def handle_level_complete(self, mouse_pos):
        self.menu_button.update(mouse_pos)
        self.next_level_button.update(mouse_pos)

        if self.next_level_button.is_clicked(mouse_pos):
            if self.game_state == AI_LEVEL_COMPLETE:
                self.game_state = ALGORITHMS_LEVEL_SELECT
            else:
                self.board.switch_level()
                next_level = self.board.level.level_name
                self.initialize_level(next_level)
                self.game_state = PLAYING
        elif self.menu_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

    def draw_level_complete(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Level complete text
        font = pygame.font.Font(None, 72)
        text = font.render("Level Complete!", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 -50))
        self.screen.blit(text, text_rect)

        # Display move count
        font = pygame.font.Font(None, 36)
        moves_text = font.render(f"Moves: {self.move_count}", True, WHITE)
        moves_rect = moves_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(moves_text, moves_rect)

        # Buttons
        self.next_level_button.draw(self.screen)

        self.menu_button.update(pygame.mouse.get_pos())
        self.menu_button.draw(self.screen)

        if (
            self.game_state == AI_LEVEL_COMPLETE
            and self.search_result is not None
        ):
            self._draw_search_metrics()

    # GAME_STATE 6 - AI_OR_HUMAN
    def handle_ai_or_human(self, mouse_pos):
        self.back_button.update(mouse_pos)
        self.human_button.update(mouse_pos)
        self.ai_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU
        elif self.human_button.is_clicked(mouse_pos):
            self.game_state = LEVEL_SELECT
        elif self.ai_button.is_clicked(mouse_pos):
            self.game_state = ALGORITHMS_LEVEL_SELECT

    def draw_ai_or_human(self):
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Play as Human or AI?", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        # Draw buttons
        self.human_button.draw(self.screen)
        self.ai_button.draw(self.screen)
        self.back_button.draw(self.screen)

    # GAME_STATE 8 - ALGORITHMS
    def handle_algorithms(self, mouse_pos):
        """
        Handle one algorithm-selection click.

        The return statements prevent one mouse click from starting the
        solver more than once, which would otherwise clear search_result.
        """
        self.back_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = AI_OR_HUMAN
            return

        for button in self.algorithm_buttons:
            button.update(mouse_pos)

            if button.is_clicked(mouse_pos):
                self.algorithm = button.text.lower()
                self.algorithm_completed = False

                self.initialize_level(
                    self.level_name,
                    AI=True,
                )

                self.game_state = AI_PLAYING
                return

    def draw_algorithms(self):
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render(
            "Choose the search algorithm",
            True,
            BLUE,
        )
        title_rect = title.get_rect(
            center=(SCREEN_WIDTH // 2, 60)
        )
        self.screen.blit(title, title_rect)

        # Draw algorithm buttons and Back.
        for button in self.algorithm_buttons:
            button.draw(self.screen)

        self.back_button.draw(self.screen)

    def start_animation(self, direction):
        self.animation_active = True
        self.animation_direction = direction
        self.animation_progress = 0
        self.old_block_position = (self.block.x1, self.block.y1, self.block.x2, self.block.y2)

        # Temporary block used to calculate following moves
        temp_block = Block(self.block.x1, self.block.y1)
        temp_block.x2 = self.block.x2
        temp_block.y2 = self.block.y2
        temp_block.orientation = self.block.orientation
        temp_block.move(direction)

        self.target_block_position = (temp_block.x1, temp_block.y1, temp_block.x2, temp_block.y2)

    def draw_solve_options(self):
        if hasattr(self, 'show_solution') and self.show_solution:
            font = pygame.font.Font(None, 24)
            text = font.render(f"Solving... Step {self.solution_index}/{len(self.solution_actions)}", True, BLACK)
            self.screen.blit(text, (20, 150))

        self.solve_button.draw(self.screen)

    def _draw_search_metrics(self):
        """
        Draw the standardized search measurements collected by run_search().
        """
        if self.search_result is None:
            return

        panel_width = 255
        panel_height = 205
        panel_x = SCREEN_WIDTH - panel_width - 15
        panel_y = 120

        panel = pygame.Surface(
            (panel_width, panel_height),
            pygame.SRCALPHA,
        )
        panel.fill((0, 0, 0, 205))
        self.screen.blit(
            panel,
            (panel_x, panel_y),
        )

        title_font = pygame.font.Font(None, 30)
        text_font = pygame.font.Font(None, 23)

        title = title_font.render(
            "Search Statistics",
            True,
            WHITE,
        )
        self.screen.blit(
            title,
            (panel_x + 14, panel_y + 12),
        )

        status = (
            "Solved"
            if self.search_result.solved
            else "No solution"
        )

        lines = [
            f"Algorithm: {self.search_result.algorithm}",
            f"Status: {status}",
            (
                "Time: "
                f"{self.search_result.search_time_ms:.3f} ms"
            ),
            (
                "Peak memory: "
                f"{self.search_result.peak_memory_mb:.4f} MB"
            ),
            (
                "Expanded nodes: "
                f"{self.search_result.expanded_nodes}"
            ),
            (
                "Solution length: "
                f"{self.search_result.solution_length}"
            ),
            (
                "Total cost: "
                f"{self.search_result.total_cost:g}"
            ),
        ]

        for index, line in enumerate(lines):
            text = text_font.render(
                line,
                True,
                WHITE_CLOUD,
            )
            self.screen.blit(
                text,
                (
                    panel_x + 14,
                    panel_y + 48 + index * 21,
                ),
            )

    def _draw_state_blocks(self):
        if self.current_state is None:
            return

        font = pygame.font.Font(None, 28)

        for index, (row, column) in enumerate(
            self.current_state.positions
        ):
            x = column * TILE_SIZE + self.camera_offset_x
            y = row * TILE_SIZE + self.camera_offset_y

            if self.current_state.is_split:
                is_active = index == self.current_state.active_cube
                color = ORANGE if is_active else INACTIVE_CUBE
                margin = 6

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        x + margin,
                        y + margin,
                        TILE_SIZE - 2 * margin,
                        TILE_SIZE - 2 * margin,
                    ),
                    border_radius=6,
                )

                border_color = WHITE if is_active else BLACK
                pygame.draw.rect(
                    self.screen,
                    border_color,
                    (
                        x + margin,
                        y + margin,
                        TILE_SIZE - 2 * margin,
                        TILE_SIZE - 2 * margin,
                    ),
                    3,
                    border_radius=6,
                )

                label = font.render(
                    str(index + 1),
                    True,
                    BLACK,
                )
                label_rect = label.get_rect(
                    center=(
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2,
                    )
                )
                self.screen.blit(label, label_rect)

            else:
                pygame.draw.rect(
                    self.screen,
                    HOT_PINK,
                    (
                        x + 3,
                        y + 3,
                        TILE_SIZE - 6,
                        TILE_SIZE - 6,
                    ),
                    border_radius=5,
                )
                pygame.draw.rect(
                    self.screen,
                    BLACK,
                    (
                        x + 3,
                        y + 3,
                        TILE_SIZE - 6,
                        TILE_SIZE - 6,
                    ),
                    2,
                    border_radius=5,
                )

    def draw_level(self):
        layout = self.board.level.layout

        for i in range(self.board.level.height):
            for j in range(self.board.level.width):
                x = j * TILE_SIZE + self.camera_offset_x
                y = i * TILE_SIZE + self.camera_offset_y
                tile = layout[i][j]

                if tile == -1:
                    color = BLACK
                elif tile == -2:
                    color = DARK_GRAY
                elif tile == 0:
                    color = BLUE
                elif tile == 3:
                    color = CYAN
                elif tile == 4:
                    color = YELLOW
                elif tile == 5:
                    color = PURPLE
                elif tile == 6:
                    color = GRAY
                elif tile == 7:
                    color = GREEN
                elif tile == 8:
                    color = ORANGE
                else:
                    color = BLUE

                pygame.draw.rect(
                    self.screen,
                    color,
                    (x, y, TILE_SIZE, TILE_SIZE),
                )
                pygame.draw.rect(
                    self.screen,
                    BLACK,
                    (x, y, TILE_SIZE, TILE_SIZE),
                    1,
                )

                if tile == 8:
                    # Bracket-like visual for a split switch.
                    pygame.draw.arc(
                        self.screen,
                        BLACK,
                        (x + 8, y + 8, 15, TILE_SIZE - 16),
                        1.57,
                        4.71,
                        3,
                    )
                    pygame.draw.arc(
                        self.screen,
                        BLACK,
                        (x + TILE_SIZE - 23, y + 8, 15, TILE_SIZE - 16),
                        -1.57,
                        1.57,
                        3,
                    )

        self._draw_state_blocks()

        if self.game_state != AI_PLAYING:
            self.menu_button.draw(self.screen)
            self.restart_button.draw(self.screen)

        font = pygame.font.Font(None, 32)

        level_text = font.render(
            f"Level: {self.current_level.replace('LEVEL', '')}",
            True,
            WHITE_CLOUD,
        )
        self.screen.blit(level_text, (20, 20))

        moves_text = font.render(
            f"Moves: {self.move_count}",
            True,
            WHITE_CLOUD,
        )
        self.screen.blit(moves_text, (20, 60))

        if self.current_state.is_split:
            cube_text = font.render(
                (
                    f"Active cube: {self.current_state.active_cube + 1} "
                    "(SPACE to switch)"
                ),
                True,
                WHITE_CLOUD,
            )
            self.screen.blit(cube_text, (20, 100))

        if self.game_state in {
            AI_PLAYING,
            AI_LEVEL_COMPLETE,
        }:
            self._draw_search_metrics()

        if self.game_state == AI_PLAYING and self.solution:
            action = self.solution.popleft()
            self.apply_game_action(action)
            pygame.time.delay(500)

        elif self.solution is not None and not self.solution:
            pygame.time.delay(500)
            self.solution = None
            self.algorithm = None
            self.algorithm_completed = False

            if is_goal_state(
                self.current_state,
                self.current_level,
            ):
                self.game_state = AI_LEVEL_COMPLETE

    def update_animation(self):
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.running = self.input_handler.handle_events()
            if self.game_logic.game_over:
                self.game_state = GAME_OVER

            if self.game_logic.level_completed:
                self.game_logic.level_completed = False
                if self.game_state == PLAYING:
                    self.game_state = LEVEL_COMPLETE
                elif self.game_state == AI_PLAYING:
                    self.game_state = AI_LEVEL_COMPLETE

            self.draw()
            self.update_animation()