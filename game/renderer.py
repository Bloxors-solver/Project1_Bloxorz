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
from search_algorithms.comparison import (
    run_comparison,
    save_comparison_csv,
    select_replay_result,
)

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 42
FPS = 60

GAME_AREA_WIDTH = 1000
SIDEBAR_X = 1015
SIDEBAR_WIDTH = 250
HEADER_HEIGHT = 72

# Isometric 2.5D projection
ISO_TILE_WIDTH = 60
ISO_TILE_HEIGHT = 32
ISO_TILE_DEPTH = 12
ISO_CUBE_HEIGHT = 34
ISO_UPRIGHT_HEIGHT = 68

# Modern dark-blue theme
BLACK = (8, 13, 24)
WHITE = (244, 248, 255)
GRAY = (111, 127, 151)
BLUE = (67, 139, 232)
GREEN = (78, 205, 146)
RED = (245, 99, 99)
YELLOW = (255, 202, 79)
CYAN = (91, 209, 235)
PURPLE = (157, 116, 255)
TRANSPARENT_BLUE = (64, 136, 230, 145)
DARK_GRAY = (31, 43, 62)
LIGHT_BLUE = (20, 35, 58)
HOT_PINK = (240, 94, 170)
WHITE_CLOUD = (223, 233, 247)
ORANGE = (255, 153, 72)
INACTIVE_CUBE = (177, 105, 214)

BACKGROUND_TOP = (10, 18, 34)
BACKGROUND_BOTTOM = (28, 54, 88)
PANEL = (20, 31, 50)
PANEL_ALT = (27, 42, 66)
PANEL_LIGHT = (38, 56, 83)
BORDER = (70, 96, 132)
TEXT_PRIMARY = (240, 246, 255)
TEXT_MUTED = (160, 177, 201)
ACCENT = (66, 163, 255)
ACCENT_HOVER = (103, 187, 255)
SUCCESS = (76, 208, 145)
DANGER = (244, 102, 105)
WARNING = (255, 193, 74)

FLOOR_TOP = (65, 116, 188)
FLOOR_SIDE = (34, 69, 124)
FRAGILE_TOP = (111, 211, 231)
FRAGILE_SIDE = (57, 132, 161)
GOAL_TOP = (50, 173, 119)
GOAL_SIDE = (26, 102, 75)
HIDDEN_TOP = (74, 83, 101)
HIDDEN_SIDE = (39, 45, 59)

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
COMPARISON = 11


# Reusable modern button
class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color,
        hover_color,
        text_color=TEXT_PRIMARY,
        font_size=28,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.is_hovered = False

    def draw(self, screen):
        fill_color = self.hover_color if self.is_hovered else self.color

        shadow_rect = self.rect.move(0, 6)
        pygame.draw.rect(
            screen,
            (6, 12, 22),
            shadow_rect,
            border_radius=16,
        )

        pygame.draw.rect(
            screen,
            fill_color,
            self.rect,
            border_radius=16,
        )

        inner_rect = self.rect.inflate(-4, -4)
        inner_overlay = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            inner_overlay,
            (255, 255, 255, 22 if self.is_hovered else 12),
            (0, 0, inner_rect.width, inner_rect.height // 2),
            border_radius=14,
        )
        screen.blit(inner_overlay, inner_rect.topleft)

        border_color = WHITE if self.is_hovered else BORDER
        pygame.draw.rect(
            screen,
            border_color,
            self.rect,
            2,
            border_radius=16,
        )

        highlight = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 7,
            self.rect.width - 20,
            4,
        )
        pygame.draw.rect(
            screen,
            (245, 248, 255),
            highlight,
            border_radius=3,
        )

        font = pygame.font.Font(None, self.font_size)
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
        # Use a large resizable window. Fullscreen mode was removed because
        # repeated fullscreen/window toggling was unreliable on some systems.
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SCALED | pygame.RESIZABLE,
        )
        pygame.display.set_caption("Bloxorz AI Lab")
        self.background_surface = self._create_background_surface()
        self.clock = pygame.time.Clock()
        self.game_state = MAIN_MENU
        self.block = block
        self.board = board
        self.game_logic = game_logic
        self.input_handler = input_handler
        self.init_buttons()

        self.pause_button = Button(
            SIDEBAR_X + 16,
            590,
            SIDEBAR_WIDTH - 32,
            42,
            "PAUSE",
            WARNING,
            (255, 218, 123),
            BLACK,
            20,
        )

        self.running = True
        self.algorithm = None
        self.solution = None
        self.algorithm_completed = False
        self.search_result = None
        self.search_result_level = None
        self.comparison_results = []
        self.comparison_level = None
        self.comparison_status = ""
        self.comparison_csv_path = None
        self.level_name = None
        self.current_level = None
        self.current_state = block_to_state(block, board)
        self.move_count = 0

        # Keep the older, stable step-by-step movement style.
        self.animation_active = False
        self.animation_direction = None
        self.animation_progress = 0
        self.animation_speed = 0.1
        self.old_block_position = None
        self.target_block_position = None

        self.ai_paused = False
        self.ai_step_interval = 500
        self.last_ai_step_at = 0

    def _create_background_surface(self):
        surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        for y in range(SCREEN_HEIGHT):
            ratio = y / max(1, SCREEN_HEIGHT - 1)
            color = tuple(
                int(
                    BACKGROUND_TOP[index]
                    + (
                        BACKGROUND_BOTTOM[index]
                        - BACKGROUND_TOP[index]
                    )
                    * ratio
                )
                for index in range(3)
            )
            pygame.draw.line(
                surface,
                color,
                (0, y),
                (SCREEN_WIDTH, y),
            )

        # Subtle decorative dots.
        dots = [
            (82, 90, 2),
            (185, 142, 3),
            (325, 66, 2),
            (480, 126, 2),
            (660, 84, 3),
            (790, 155, 2),
            (950, 72, 2),
            (1030, 178, 3),
            (120, 610, 2),
            (315, 660, 3),
            (720, 625, 2),
            (995, 650, 2),
        ]

        for x, y, radius in dots:
            pygame.draw.circle(
                surface,
                (75, 111, 154),
                (x, y),
                radius,
            )

        return surface

    def _draw_background(self):
        self.screen.blit(
            self.background_surface,
            (0, 0),
        )

    def _draw_panel(
        self,
        rect,
        fill=PANEL,
        border=BORDER,
        alpha=235,
        radius=20,
    ):
        panel = pygame.Surface(
            (rect.width, rect.height),
            pygame.SRCALPHA,
        )
        panel.fill((0, 0, 0, 0))

        pygame.draw.rect(
            panel,
            (*fill, alpha),
            panel.get_rect(),
            border_radius=radius,
        )
        pygame.draw.rect(
            panel,
            (*border, min(255, alpha)),
            panel.get_rect(),
            2,
            border_radius=radius,
        )
        self.screen.blit(panel, rect.topleft)

    def _draw_text(
        self,
        text,
        size,
        color=TEXT_PRIMARY,
        center=None,
        topleft=None,
    ):
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, color)
        rect = surface.get_rect()

        if center is not None:
            rect.center = center
        elif topleft is not None:
            rect.topleft = topleft

        self.screen.blit(surface, rect)
        return rect

    def _draw_header(self, title, subtitle=""):
        pygame.draw.rect(
            self.screen,
            (10, 18, 31),
            (0, 0, SCREEN_WIDTH, HEADER_HEIGHT),
        )
        pygame.draw.line(
            self.screen,
            BORDER,
            (0, HEADER_HEIGHT - 1),
            (SCREEN_WIDTH, HEADER_HEIGHT - 1),
            2,
        )

        self._draw_text(
            title,
            42,
            TEXT_PRIMARY,
            topleft=(28, 15),
        )

        if subtitle:
            self._draw_text(
                subtitle,
                23,
                TEXT_MUTED,
                topleft=(30, 48),
            )

    def _draw_cube_logo(self, center_x, center_y, size=130):
        depth = size // 4
        left = center_x - size // 2
        top = center_y - size // 2

        top_face = [
            (left, top + depth),
            (left + depth, top),
            (left + size, top),
            (left + size - depth, top + depth),
        ]
        front_face = [
            (left, top + depth),
            (left + size - depth, top + depth),
            (left + size - depth, top + size),
            (left, top + size),
        ]
        right_face = [
            (left + size - depth, top + depth),
            (left + size, top),
            (left + size, top + size - depth),
            (left + size - depth, top + size),
        ]

        pygame.draw.polygon(
            self.screen,
            (104, 193, 255),
            top_face,
        )
        pygame.draw.polygon(
            self.screen,
            (63, 127, 218),
            front_face,
        )
        pygame.draw.polygon(
            self.screen,
            (35, 83, 158),
            right_face,
        )

        for face in (top_face, front_face, right_face):
            pygame.draw.polygon(
                self.screen,
                WHITE,
                face,
                2,
            )

    def _draw_status_chip(
        self,
        text,
        x,
        y,
        color=ACCENT,
    ):
        font = pygame.font.Font(None, 23)
        text_surface = font.render(
            text,
            True,
            TEXT_PRIMARY,
        )
        width = text_surface.get_width() + 24

        rect = pygame.Rect(
            x,
            y,
            width,
            30,
        )
        pygame.draw.rect(
            self.screen,
            color,
            rect,
            border_radius=15,
        )
        self.screen.blit(
            text_surface,
            (
                rect.x + 12,
                rect.y + 6,
            ),
        )

    def _iso_project(self, row, column):
        """
        Convert a board position into an isometric screen-space center.
        """
        half_width = ISO_TILE_WIDTH // 2
        half_height = ISO_TILE_HEIGHT // 2

        screen_x = (
            self.iso_origin_x
            + (column - row) * half_width
        )
        screen_y = (
            self.iso_origin_y
            + (column + row) * half_height
        )

        return screen_x, screen_y

    @staticmethod
    def _shade(color, factor):
        return tuple(
            max(0, min(255, int(component * factor)))
            for component in color
        )

    def _tile_palette(self, tile):
        """Return solid isometric colors for every tile type."""
        top_color = (52, 94, 170)       # floor

        if tile == -2:
            top_color = (79, 88, 106)   # closed bridge / hidden path
        elif tile == 3:
            top_color = (237, 145, 66)  # fragile: orange, per specification
        elif tile == 4:
            top_color = (218, 171, 55)  # heavy switch
        elif tile == 5:
            top_color = (76, 190, 204)  # soft switch
        elif tile == 6:
            top_color = (119, 130, 148) # permanent / one-time switch
        elif tile == 7:
            top_color = (59, 174, 103)  # goal
        elif tile == 8:
            top_color = (154, 105, 216) # split switch

        return (
            top_color,
            self._shade(top_color, 0.74),
            self._shade(top_color, 0.54),
        )

    def _draw_iso_tile(self, row, column, tile):
        if tile == -1:
            return

        center_x, center_y = self._iso_project(row, column)
        half_width = ISO_TILE_WIDTH // 2
        half_height = ISO_TILE_HEIGHT // 2
        depth = ISO_TILE_DEPTH

        top = (center_x, center_y - half_height)
        right = (center_x + half_width, center_y)
        bottom = (center_x, center_y + half_height)
        left = (center_x - half_width, center_y)
        bottom_depth = (bottom[0], bottom[1] + depth)
        left_depth = (left[0], left[1] + depth)
        right_depth = (right[0], right[1] + depth)

        top_color, left_color, right_color = self._tile_palette(tile)

        pygame.draw.polygon(self.screen, left_color, [left, bottom, bottom_depth, left_depth])
        pygame.draw.polygon(self.screen, right_color, [right, bottom, bottom_depth, right_depth])
        pygame.draw.polygon(self.screen, top_color, [top, right, bottom, left])
        pygame.draw.lines(self.screen, self._shade(top_color, 1.30), True, [top, right, bottom, left], 2)
        pygame.draw.line(self.screen, self._shade(left_color, 0.72), left_depth, bottom_depth, 1)
        pygame.draw.line(self.screen, self._shade(right_color, 0.72), bottom_depth, right_depth, 1)

        # Fragile: crack pattern.
        if tile == 3:
            crack = (255, 237, 213)
            pygame.draw.line(self.screen, crack, (center_x - 12, center_y - 3), (center_x - 2, center_y + 1), 2)
            pygame.draw.line(self.screen, crack, (center_x - 2, center_y + 1), (center_x + 4, center_y - 5), 2)
            pygame.draw.line(self.screen, crack, (center_x - 2, center_y + 1), (center_x + 10, center_y + 5), 2)

        # Heavy switch: clear X symbol.
        elif tile == 4:
            pygame.draw.ellipse(self.screen, (55, 42, 18), (center_x - 12, center_y - 7, 24, 14))
            pygame.draw.line(self.screen, WHITE, (center_x - 7, center_y - 4), (center_x + 7, center_y + 4), 3)
            pygame.draw.line(self.screen, WHITE, (center_x + 7, center_y - 4), (center_x - 7, center_y + 4), 3)

        # Soft switch: circle / octagon-like ring.
        elif tile == 5:
            points = [
                (center_x - 8, center_y - 6),
                (center_x + 8, center_y - 6),
                (center_x + 12, center_y),
                (center_x + 8, center_y + 6),
                (center_x - 8, center_y + 6),
                (center_x - 12, center_y),
            ]
            pygame.draw.polygon(self.screen, (23, 70, 78), points)
            pygame.draw.lines(self.screen, WHITE, True, points, 2)
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 3)

        # Permanent/one-time switch: ring with center lock dot.
        elif tile == 6:
            pygame.draw.ellipse(self.screen, (44, 49, 60), (center_x - 11, center_y - 6, 22, 12))
            pygame.draw.ellipse(self.screen, WHITE, (center_x - 11, center_y - 6, 22, 12), 2)
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 4)

        elif tile == 7:
            pygame.draw.ellipse(self.screen, (4, 33, 18), (center_x - 13, center_y - 8, 26, 16))
            pygame.draw.ellipse(self.screen, (180, 255, 204), (center_x - 13, center_y - 8, 26, 16), 3)
            pygame.draw.ellipse(self.screen, (78, 225, 128), (center_x - 8, center_y - 4, 16, 8), 1)

        # Split switch: bracket symbol.
        elif tile == 8:
            bracket = WHITE
            pygame.draw.arc(self.screen, bracket, (center_x - 15, center_y - 8, 12, 16), 1.35, 4.95, 3)
            pygame.draw.arc(self.screen, bracket, (center_x + 3, center_y - 8, 12, 16), -1.80, 1.80, 3)

    def _iso_grid_point(self, row, column):
        half_width = ISO_TILE_WIDTH / 2
        half_height = ISO_TILE_HEIGHT / 2

        return (
            int(self.iso_origin_x + (column - row) * half_width),
            int(self.iso_origin_y + (column + row) * half_height),
        )

    def _state_prism_bounds(self, state):
        rows = [
            position[0]
            for position in state.positions
        ]
        columns = [
            position[1]
            for position in state.positions
        ]

        # Keep a small border around the block so the floor remains visible.
        # The same inset is used for upright, lying and split unit cubes,
        # making every 1x1x1 part visually consistent.
        inset = 0.08

        return (
            min(rows) - 0.5 + inset,
            max(rows) + 0.5 - inset,
            min(columns) - 0.5 + inset,
            max(columns) + 0.5 - inset,
        )

    def _draw_prism_from_bounds(
        self,
        bounds,
        height,
        active=False,
        split=False,
        label=None,
        lift=0,
    ):
        """
        Draw one fully opaque isometric prism.

        Only the two visible vertical faces are rendered. Drawing all four
        faces made the block look transparent or multi-coloured.
        """
        row_min, row_max, column_min, column_max = bounds

        base = [
            self._iso_grid_point(row_min, column_min),  # back
            self._iso_grid_point(row_min, column_max),  # right
            self._iso_grid_point(row_max, column_max),  # front
            self._iso_grid_point(row_max, column_min),  # left
        ]
        base = [(x, y + lift) for x, y in base]
        top = [(x, y - height) for x, y in base]

        if split:
            if active:
                top_color = (250, 193, 112)
                left_color = (201, 121, 56)
                right_color = (142, 79, 38)
            else:
                top_color = (188, 155, 218)
                left_color = (126, 89, 158)
                right_color = (82, 54, 111)
        else:
            # A compact bronze palette keeps the block readable and solid.
            top_color = (239, 173, 82)
            left_color = (190, 112, 43)
            right_color = (124, 69, 29)

        # Visible faces meet at the front corner (base[2]).
        right_face = [
            top[1],
            top[2],
            base[2],
            base[1],
        ]
        left_face = [
            top[2],
            top[3],
            base[3],
            base[2],
        ]

        pygame.draw.polygon(
            self.screen,
            right_color,
            right_face,
        )
        pygame.draw.polygon(
            self.screen,
            left_color,
            left_face,
        )
        pygame.draw.polygon(
            self.screen,
            top_color,
            top,
        )

        outline = WHITE if active else (78, 44, 21)
        pygame.draw.lines(
            self.screen,
            outline,
            True,
            right_face,
            2,
        )
        pygame.draw.lines(
            self.screen,
            outline,
            True,
            left_face,
            2,
        )
        pygame.draw.lines(
            self.screen,
            outline,
            True,
            top,
            2,
        )

        # One subtle highlight, without translucent overlays.
        pygame.draw.line(
            self.screen,
            (255, 225, 161),
            (top[0][0] + 5, top[0][1] + 3),
            (top[1][0] - 5, top[1][1] + 3),
            2,
        )

        if label is not None:
            center_x = sum(point[0] for point in top) // 4
            center_y = sum(point[1] for point in top) // 4
            self._draw_text(
                str(label),
                18,
                BLACK,
                center=(center_x, center_y),
            )

    def _draw_iso_cube(
        self,
        row,
        column,
        cube_height,
        active=False,
        split=False,
        label=None,
    ):
        class VisualState:
            positions = ((row, column),)
            orientation = "split" if split else "upright"
            is_split = split

        self._draw_prism_from_bounds(
            self._state_prism_bounds(VisualState),
            cube_height,
            active=active,
            split=split,
            label=label,
        )

    def _draw_tile_3d(self, x, y, tile):
        if tile == -1:
            return

        top_color = FLOOR_TOP
        side_color = FLOOR_SIDE

        if tile == -2:
            top_color = HIDDEN_TOP
            side_color = HIDDEN_SIDE
        elif tile == 3:
            top_color = FRAGILE_TOP
            side_color = FRAGILE_SIDE
        elif tile == 4:
            top_color = WARNING
            side_color = (152, 100, 32)
        elif tile == 5:
            top_color = PURPLE
            side_color = (88, 57, 150)
        elif tile == 6:
            top_color = GRAY
            side_color = (62, 72, 87)
        elif tile == 7:
            top_color = GOAL_TOP
            side_color = GOAL_SIDE
        elif tile == 8:
            top_color = ORANGE
            side_color = (154, 80, 29)

        depth = 5
        top_rect = pygame.Rect(
            x + 2,
            y + 2,
            TILE_SIZE - 5,
            TILE_SIZE - depth - 4,
        )
        side_rect = pygame.Rect(
            x + 4,
            y + TILE_SIZE - depth - 2,
            TILE_SIZE - 8,
            depth,
        )

        pygame.draw.rect(
            self.screen,
            (5, 10, 18),
            (
                x + 4,
                y + 7,
                TILE_SIZE - 3,
                TILE_SIZE - 2,
            ),
            border_radius=7,
        )
        pygame.draw.rect(
            self.screen,
            side_color,
            side_rect,
            border_radius=3,
        )
        pygame.draw.rect(
            self.screen,
            top_color,
            top_rect,
            border_radius=7,
        )
        pygame.draw.rect(
            self.screen,
            (133, 170, 213),
            top_rect,
            1,
            border_radius=7,
        )

        if tile == 3:
            pygame.draw.line(
                self.screen,
                WHITE,
                (
                    top_rect.x + 7,
                    top_rect.y + 8,
                ),
                (
                    top_rect.right - 9,
                    top_rect.bottom - 8,
                ),
                2,
            )
            pygame.draw.line(
                self.screen,
                (195, 245, 255),
                (
                    top_rect.right - 13,
                    top_rect.y + 6,
                ),
                (
                    top_rect.x + 13,
                    top_rect.bottom - 5,
                ),
                1,
            )

        elif tile in {4, 5, 6}:
            pygame.draw.circle(
                self.screen,
                PANEL,
                top_rect.center,
                10,
            )
            pygame.draw.circle(
                self.screen,
                WHITE,
                top_rect.center,
                10,
                2,
            )

        elif tile == 7:
            pygame.draw.circle(
                self.screen,
                (7, 34, 28),
                top_rect.center,
                12,
            )
            pygame.draw.circle(
                self.screen,
                (135, 255, 194),
                top_rect.center,
                12,
                2,
            )

        elif tile == 8:
            center_x, center_y = top_rect.center
            pygame.draw.line(
                self.screen,
                PANEL,
                (center_x - 10, center_y - 10),
                (center_x - 10, center_y + 10),
                4,
            )
            pygame.draw.line(
                self.screen,
                PANEL,
                (center_x + 10, center_y - 10),
                (center_x + 10, center_y + 10),
                4,
            )
            pygame.draw.circle(
                self.screen,
                WHITE,
                (center_x - 10, center_y),
                4,
            )
            pygame.draw.circle(
                self.screen,
                WHITE,
                (center_x + 10, center_y),
                4,
            )

    def _draw_block_prism(
        self,
        cell_x,
        cell_y,
        height,
        active=False,
        split=False,
    ):
        width = 30
        depth = 8
        left = cell_x + (TILE_SIZE - width) // 2
        base = cell_y + TILE_SIZE - 8
        top_y = base - height

        if split:
            top_color = ORANGE if active else INACTIVE_CUBE
            front_color = (
                (205, 101, 37)
                if active
                else (120, 67, 151)
            )
            side_color = (
                (122, 63, 28)
                if active
                else (74, 43, 98)
            )
        else:
            top_color = (255, 145, 203)
            front_color = HOT_PINK
            side_color = (132, 38, 94)

        shadow_rect = pygame.Rect(
            left + 5,
            base - 4,
            width,
            8,
        )
        pygame.draw.ellipse(
            self.screen,
            (4, 8, 15),
            shadow_rect,
        )

        top_face = [
            (left, top_y + depth),
            (left + depth, top_y),
            (left + width, top_y),
            (left + width - depth, top_y + depth),
        ]
        front_face = [
            (left, top_y + depth),
            (left + width - depth, top_y + depth),
            (left + width - depth, base),
            (left, base),
        ]
        side_face = [
            (left + width - depth, top_y + depth),
            (left + width, top_y),
            (left + width, base - depth),
            (left + width - depth, base),
        ]

        pygame.draw.polygon(
            self.screen,
            top_color,
            top_face,
        )
        pygame.draw.polygon(
            self.screen,
            front_color,
            front_face,
        )
        pygame.draw.polygon(
            self.screen,
            side_color,
            side_face,
        )

        outline = WHITE if active else (41, 20, 48)
        for face in (top_face, front_face, side_face):
            pygame.draw.polygon(
                self.screen,
                outline,
                face,
                2,
            )

    def _draw_iso_block_span(self, positions):
        """
        Draw a normal lying block as one solid 2x1x1 prism.

        A seam is drawn at the shared cell boundary so the shape clearly
        looks like two equal 1x1x1 cubes joined into one rectangle.
        """
        if len(positions) != 2:
            return

        positions = tuple(positions)

        class VisualState:
            pass

        state = VisualState()
        state.positions = positions
        state.orientation = "horizontal"
        state.is_split = False

        bounds = self._state_prism_bounds(state)

        self._draw_prism_from_bounds(
            bounds,
            ISO_CUBE_HEIGHT,
            active=False,
            split=False,
        )

        (row_1, column_1), (
            row_2,
            column_2,
        ) = positions

        row_min, row_max, column_min, column_max = bounds

        # Draw the division between the two unit cubes.
        if row_1 == row_2:
            boundary_column = (
                column_1 + column_2
            ) / 2

            top_back = self._iso_grid_point(
                row_min,
                boundary_column,
            )
            top_front = self._iso_grid_point(
                row_max,
                boundary_column,
            )
        else:
            boundary_row = (
                row_1 + row_2
            ) / 2

            top_back = self._iso_grid_point(
                boundary_row,
                column_min,
            )
            top_front = self._iso_grid_point(
                boundary_row,
                column_max,
            )

        top_back = (
            top_back[0],
            top_back[1] - ISO_CUBE_HEIGHT,
        )
        top_front = (
            top_front[0],
            top_front[1] - ISO_CUBE_HEIGHT,
        )

        # Seam on the top face.
        seam_color = (112, 66, 30)
        pygame.draw.line(
            self.screen,
            seam_color,
            top_back,
            top_front,
            2,
        )

        # Seam on the visible front side.
        front_base = (
            top_front[0],
            top_front[1] + ISO_CUBE_HEIGHT,
        )
        pygame.draw.line(
            self.screen,
            seam_color,
            top_front,
            front_base,
            2,
        )

    def _draw_game_sidebar(self):
        rect = pygame.Rect(
            SIDEBAR_X,
            18,
            SIDEBAR_WIDTH,
            SCREEN_HEIGHT - 36,
        )
        self._draw_panel(
            rect,
            fill=(16, 27, 46),
            border=BORDER,
            alpha=250,
            radius=22,
        )

        if self.game_state == AI_PLAYING and self.ai_paused:
            mode = "AI · PAUSED"
            mode_color = WARNING
        elif self.game_state in {AI_PLAYING, AI_LEVEL_COMPLETE}:
            mode = "AI · ISOMETRIC"
            mode_color = ACCENT
        else:
            mode = "HUMAN · ISOMETRIC"
            mode_color = SUCCESS

        self._draw_status_chip(
            mode,
            SIDEBAR_X + 16,
            32,
            mode_color,
        )

        level_number = (
            self.current_level.replace("LEVEL", "")
            if self.current_level
            else "-"
        )
        self._draw_text(
            f"LEVEL {level_number}",
            31,
            TEXT_PRIMARY,
            topleft=(SIDEBAR_X + 16, 76),
        )
        self._draw_text(
            f"Moves  {self.move_count}",
            23,
            TEXT_MUTED,
            topleft=(SIDEBAR_X + 16, 110),
        )

        orientation = (
            self.current_state.orientation.upper()
            if self.current_state is not None
            else "-"
        )
        self._draw_text(
            "BLOCK STATE",
            19,
            TEXT_MUTED,
            topleft=(SIDEBAR_X + 16, 150),
        )
        self._draw_text(
            orientation,
            25,
            TEXT_PRIMARY,
            topleft=(SIDEBAR_X + 16, 174),
        )

        y = 210
        if (
            self.current_state is not None
            and self.current_state.is_split
        ):
            self._draw_text(
                f"Active cube  {self.current_state.active_cube + 1}",
                20,
                ORANGE,
                topleft=(SIDEBAR_X + 16, y),
            )
            y += 28

        if self.algorithm:
            self._draw_text(
                "ALGORITHM",
                19,
                TEXT_MUTED,
                topleft=(SIDEBAR_X + 16, y),
            )
            self._draw_text(
                self.algorithm.upper(),
                24,
                TEXT_PRIMARY,
                topleft=(SIDEBAR_X + 16, y + 22),
            )
            y += 54

        self._draw_text(
            "CONTROLS",
            19,
            TEXT_MUTED,
            topleft=(SIDEBAR_X + 16, y),
        )
        controls = [
            "WASD / Arrows   Move",
            "Space           Switch cube",
            "Mouse           Buttons",
        ]
        for index, line in enumerate(controls):
            self._draw_text(
                line,
                17,
                TEXT_PRIMARY,
                topleft=(
                    SIDEBAR_X + 16,
                    y + 23 + index * 22,
                ),
            )

        legend_y = y + 94
        self._draw_text(
            "TILE LEGEND",
            19,
            TEXT_MUTED,
            topleft=(SIDEBAR_X + 16, legend_y),
        )

        legend = [
            ("Floor", (52, 94, 170)),
            ("Fragile", (237, 145, 66)),
            ("Goal", (59, 174, 103)),
            ("Soft switch", (76, 190, 204)),
            ("Heavy switch", (218, 171, 55)),
            ("Permanent", (119, 130, 148)),
            ("Split switch", (154, 105, 216)),
            ("Closed bridge", (79, 88, 106)),
        ]

        for index, (label, color) in enumerate(legend):
            item_y = legend_y + 25 + index * 22
            pygame.draw.rect(
                self.screen,
                color,
                (
                    SIDEBAR_X + 17,
                    item_y,
                    19,
                    17,
                ),
                border_radius=5,
            )
            self._draw_text(
                label,
                16,
                TEXT_PRIMARY,
                topleft=(
                    SIDEBAR_X + 44,
                    item_y,
                ),
            )

        # One large pause button, then Restart and New Game.
        self.pause_button.rect = pygame.Rect(
            SIDEBAR_X + 16,
            586,
            SIDEBAR_WIDTH - 32,
            42,
        )
        self.restart_button.rect = pygame.Rect(
            SIDEBAR_X + 16,
            642,
            102,
            42,
        )
        self.menu_button.rect = pygame.Rect(
            SIDEBAR_X + 132,
            642,
            102,
            42,
        )

        self.pause_button.text = (
            "RESUME" if self.ai_paused else "PAUSE"
        )
        self.menu_button.text = "NEW GAME"

    def init_buttons(self):
        # Main menu
        self.play_button = Button(
            745,
            285,
            260,
            64,
            "START GAME",
            ACCENT,
            ACCENT_HOVER,
            WHITE,
            30,
        )
        self.rules_button = Button(
            745,
            375,
            260,
            58,
            "HOW TO PLAY",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            27,
        )

        # Human / AI selection
        self.human_button = Button(
            250,
            300,
            250,
            115,
            "HUMAN",
            SUCCESS,
            (107, 226, 170),
            WHITE,
            34,
        )
        self.ai_button = Button(
            600,
            300,
            250,
            115,
            "AI SOLVER",
            ACCENT,
            ACCENT_HOVER,
            WHITE,
            34,
        )

        self.back_button = Button(
            38,
            645,
            170,
            48,
            "BACK",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            25,
        )

        # Algorithms: two columns.
        self.algorithm_buttons = []
        algorithms = [
            "A*",
            "BFS",
            "DFS",
            "Greedy",
            "UCS",
            "IDS",
        ]
        positions = [
            (200, 175),
            (460, 175),
            (200, 255),
            (460, 255),
            (200, 335),
            (460, 335),
        ]

        for algorithm, (x, y) in zip(
            algorithms,
            positions,
        ):
            self.algorithm_buttons.append(
                Button(
                    x,
                    y,
                    215,
                    58,
                    algorithm,
                    PANEL_LIGHT,
                    (62, 89, 126),
                    WHITE,
                    30,
                )
            )

        self.run_all_button = Button(
            770,
            225,
            260,
            95,
            "RUN ALL (4)",
            WARNING,
            (255, 215, 120),
            BLACK,
            32,
        )

        self.comparison_replay_button = Button(
            295,
            630,
            225,
            54,
            "REPLAY A*",
            SUCCESS,
            (108, 226, 170),
            WHITE,
            27,
        )
        self.comparison_back_button = Button(
            580,
            630,
            225,
            54,
            "BACK",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            27,
        )

        # Level selection: five cards per row.
        self.level_buttons = []
        for index in range(10):
            row = index // 5
            column = index % 5
            level_num = index + 1
            x = 58 + column * 207
            y = 190 + row * 145

            self.level_buttons.append(
                Button(
                    x,
                    y,
                    170,
                    96,
                    f"LEVEL {level_num}",
                    PANEL_LIGHT,
                    (62, 89, 126),
                    WHITE,
                    28,
                )
            )

        # In-game and modal buttons.
        self.menu_button = Button(
            SIDEBAR_X + 28,
            592,
            174,
            44,
            "MENU",
            PANEL_LIGHT,
            (58, 80, 112),
            WHITE,
            23,
        )
        self.restart_button = Button(
            SIDEBAR_X + 28,
            646,
            174,
            44,
            "RESTART",
            ACCENT,
            ACCENT_HOVER,
            WHITE,
            23,
        )
        self.next_level_button = Button(
            SCREEN_WIDTH // 2 - 120,
            510,
            240,
            58,
            "NEXT LEVEL",
            SUCCESS,
            (108, 226, 170),
            WHITE,
            28,
        )
        self.retry_button = Button(
            SCREEN_WIDTH // 2 - 120,
            500,
            240,
            58,
            "TRY AGAIN",
            DANGER,
            (255, 135, 137),
            WHITE,
            28,
        )

        # Retained for compatibility.
        self.solve_button = Button(
            20,
            100,
            120,
            42,
            "SOLVE",
            ACCENT,
            ACCENT_HOVER,
            WHITE,
            23,
        )

    def _clear_ai_run(self, clear_algorithm=False):
        """
        Remove solution and metric data from the previous AI run.
        """
        self.solution = None
        self.search_result = None
        self.search_result_level = None
        self.algorithm_completed = False
        self.ai_paused = False
        self.last_ai_step_at = 0
        self.animation_active = False
        self.animation_from_state = None
        self.animation_to_state = None

        if clear_algorithm:
            self.algorithm = None

    def _clear_comparison(self):
        self.comparison_results = []
        self.comparison_level = None
        self.comparison_status = ""
        self.comparison_csv_path = None

    def initialize_level(self, level_name, AI=False):
        self.current_level = level_name

        # Never reuse data from the previous level.
        self._clear_ai_run(clear_algorithm=False)

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
        self.ai_paused = False
        self.last_ai_step_at = 0
        self.animation_active = False

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
            self.search_result_level = self.current_level

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
        Apply one action immediately.

        This restores the older stable movement effect while keeping the new
        solid block colours.
        """
        try:
            next_state = transition(
                self.current_state,
                action,
                self.current_level,
            )
        except ValueError:
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
        rows = self.board.level.height
        columns = self.board.level.width

        half_width = ISO_TILE_WIDTH // 2
        half_height = ISO_TILE_HEIGHT // 2

        self.board_pixel_width = (
            rows + columns
        ) * half_width
        self.board_pixel_height = (
            rows + columns
        ) * half_height + ISO_TILE_DEPTH

        board_left = max(
            14,
            (GAME_AREA_WIDTH - self.board_pixel_width) // 2,
        )
        board_top = (
            HEADER_HEIGHT
            + max(
                18,
                (
                    SCREEN_HEIGHT
                    - HEADER_HEIGHT
                    - self.board_pixel_height
                )
                // 2,
            )
        )

        self.iso_origin_x = board_left + rows * half_width
        self.iso_origin_y = board_top + half_height
        self.camera_offset_x = board_left
        self.camera_offset_y = board_top

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
        elif self.game_state == COMPARISON:
            self.draw_comparison()

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
        self._draw_background()

        hero_width = 570
        action_width = 360
        gap = 70
        total_width = (
            hero_width
            + action_width
            + gap
        )
        start_x = (
            SCREEN_WIDTH - total_width
        ) // 2

        hero_rect = pygame.Rect(
            start_x,
            105,
            hero_width,
            510,
        )
        action_rect = pygame.Rect(
            hero_rect.right + gap,
            165,
            action_width,
            350,
        )

        self._draw_panel(
            hero_rect,
            fill=(15, 27, 47),
            border=(56, 91, 132),
            alpha=235,
            radius=28,
        )
        self._draw_panel(
            action_rect,
            fill=PANEL,
            border=BORDER,
            alpha=245,
            radius=24,
        )

        hero_center_x = hero_rect.centerx
        action_center_x = action_rect.centerx

        self._draw_cube_logo(
            hero_rect.x + 190,
            310,
            175,
        )

        self._draw_text(
            "BLOXORZ",
            78,
            TEXT_PRIMARY,
            center=(
                hero_rect.x + 365,
                200,
            ),
        )
        self._draw_text(
            "AI LAB",
            46,
            ACCENT,
            center=(
                hero_rect.x + 365,
                250,
            ),
        )

        self._draw_text(
            "Roll. Split. Search. Solve.",
            30,
            TEXT_MUTED,
            center=(hero_center_x, 520),
        )
        self._draw_text(
            "Interactive puzzle + algorithm visualizer",
            24,
            TEXT_MUTED,
            center=(hero_center_x, 555),
        )

        self._draw_text(
            "WELCOME",
            40,
            TEXT_PRIMARY,
            center=(action_center_x, 220),
        )
        self._draw_text(
            "Choose an option to begin",
            24,
            TEXT_MUTED,
            center=(action_center_x, 255),
        )

        self.play_button.rect = pygame.Rect(
            action_rect.x + 50,
            285,
            action_rect.width - 100,
            64,
        )
        self.rules_button.rect = pygame.Rect(
            action_rect.x + 50,
            375,
            action_rect.width - 100,
            58,
        )

        self.play_button.draw(self.screen)
        self.rules_button.draw(self.screen)

        first_chip_x = action_rect.x + 42
        self._draw_status_chip(
            "10 LEVELS",
            first_chip_x,
            470,
            ACCENT,
        )
        self._draw_status_chip(
            "6 ALGORITHMS",
            action_rect.x + 188,
            470,
            PURPLE,
        )

    def handle_rules_screen(self, mouse_pos):
        self.back_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

    def draw_rules_screen(self):
        self._draw_background()
        self._draw_header(
            "HOW TO PLAY",
            "Learn the controls and special tile mechanics.",
        )

        left = pygame.Rect(
            55,
            110,
            470,
            470,
        )
        right = pygame.Rect(
            575,
            110,
            470,
            470,
        )

        self._draw_panel(left)
        self._draw_panel(right)

        self._draw_text(
            "CONTROLS",
            34,
            ACCENT,
            topleft=(85, 140),
        )

        controls = [
            ("W / Arrow Up", "Move upward"),
            ("S / Arrow Down", "Move downward"),
            ("A / Arrow Left", "Move left"),
            ("D / Arrow Right", "Move right"),
            ("Space", "Switch active split cube"),
        ]

        for index, (key, action) in enumerate(controls):
            y = 205 + index * 63

            key_rect = pygame.Rect(
                86,
                y,
                150,
                38,
            )
            pygame.draw.rect(
                self.screen,
                PANEL_LIGHT,
                key_rect,
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                BORDER,
                key_rect,
                2,
                border_radius=10,
            )

            self._draw_text(
                key,
                23,
                TEXT_PRIMARY,
                center=key_rect.center,
            )
            self._draw_text(
                action,
                23,
                TEXT_MUTED,
                topleft=(258, y + 8),
            )

        self._draw_text(
            "TILES",
            34,
            ACCENT,
            topleft=(605, 140),
        )

        tiles = [
            ("Regular floor", FLOOR_TOP),
            ("Fragile glass", FRAGILE_TOP),
            ("Goal hole", GOAL_TOP),
            ("Bridge switch", WARNING),
            ("Split switch", ORANGE),
            ("Void / closed path", BLACK),
        ]

        for index, (label, color) in enumerate(tiles):
            y = 200 + index * 58

            pygame.draw.rect(
                self.screen,
                color,
                (608, y, 40, 40),
                border_radius=9,
            )
            pygame.draw.rect(
                self.screen,
                BORDER,
                (608, y, 40, 40),
                2,
                border_radius=9,
            )
            self._draw_text(
                label,
                25,
                TEXT_PRIMARY,
                topleft=(670, y + 8),
            )

        self.back_button.draw(self.screen)

    def handle_level_select(self, mouse_pos):
        self.back_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = MAIN_MENU

        for i, button in enumerate(self.level_buttons):
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos):
                self.level_name = f"LEVEL{i+1}"
                self._clear_comparison()
                if self.game_state == ALGORITHMS_LEVEL_SELECT:
                    self.game_state = ALGORITHMS
                else:
                    self.initialize_level(self.level_name)
                    self.game_state = PLAYING

    def draw_level_select(self):
        self._draw_background()

        mode = (
            "AI MODE"
            if self.game_state
            == ALGORITHMS_LEVEL_SELECT
            else "HUMAN MODE"
        )
        self._draw_header(
            "SELECT LEVEL",
            f"{mode} · Choose one of 10 available puzzles.",
        )

        panel = pygame.Rect(
            35,
            120,
            1030,
            435,
        )
        self._draw_panel(panel)

        for index, button in enumerate(
            self.level_buttons
        ):
            button.draw(self.screen)

            number = index + 1
            badge_color = (
                ORANGE
                if number == 10
                else ACCENT
            )
            badge_text = (
                "SPLIT"
                if number == 10
                else f"{number:02}"
            )

            badge_rect = pygame.Rect(
                button.rect.x + 10,
                button.rect.y + 10,
                52,
                24,
            )
            pygame.draw.rect(
                self.screen,
                badge_color,
                badge_rect,
                border_radius=12,
            )
            self._draw_text(
                badge_text,
                19,
                WHITE,
                center=badge_rect.center,
            )

        self._draw_text(
            "Level 10 demonstrates split-cube mechanics.",
            23,
            TEXT_MUTED,
            center=(SCREEN_WIDTH // 2, 585),
        )

        self.back_button.draw(self.screen)

    def handle_playing(self, mouse_pos):
        self.menu_button.update(mouse_pos)
        self.restart_button.update(mouse_pos)

        if self.game_state == AI_PLAYING:
            self.pause_button.update(mouse_pos)

        if self.menu_button.is_clicked(mouse_pos):
            self._clear_ai_run(clear_algorithm=True)
            self.game_state = MAIN_MENU
            return

        if (
            self.game_state == AI_PLAYING
            and self.pause_button.is_clicked(mouse_pos)
        ):
            self.ai_paused = not self.ai_paused
            self.last_ai_step_at = pygame.time.get_ticks()
            return

        if self.restart_button.is_clicked(mouse_pos):
            if (
                self.game_state == AI_PLAYING
                and self.algorithm
            ):
                self.initialize_level(
                    self.current_level,
                    AI=True,
                )
                self.ai_paused = False
                self.game_state = AI_PLAYING
            else:
                self.initialize_level(
                    self.current_level
                )
                self.game_state = PLAYING

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
        self.menu_button.text = "MENU"
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 8, 15, 220))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_WIDTH // 2 - 270, 150, 540, 420)
        self._draw_panel(panel, fill=(39, 24, 38), border=DANGER, alpha=250, radius=30)
        pygame.draw.line(self.screen, self._shade(DANGER, 1.12), (panel.x + 32, panel.y + 92), (panel.right - 32, panel.y + 92), 2)

        self._draw_text("BLOCK LOST", 56, DANGER, center=(SCREEN_WIDTH // 2, 220))
        self._draw_text("The block fell into the void.", 27, TEXT_MUTED, center=(SCREEN_WIDTH // 2, 280))
        self._draw_text(f"Moves attempted: {self.move_count}", 28, TEXT_PRIMARY, center=(SCREEN_WIDTH // 2, 328))

        self.retry_button.rect = pygame.Rect(SCREEN_WIDTH // 2 - 245, 435, 220, 58)
        self.menu_button.rect = pygame.Rect(SCREEN_WIDTH // 2 + 25, 435, 220, 58)
        self.retry_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def handle_level_complete(self, mouse_pos):
        self.menu_button.update(mouse_pos)
        self.next_level_button.update(mouse_pos)

        if self.next_level_button.is_clicked(mouse_pos):
            if self.game_state == AI_LEVEL_COMPLETE:
                self._clear_ai_run(clear_algorithm=True)
                self.game_state = ALGORITHMS_LEVEL_SELECT
            else:
                self.board.switch_level()
                next_level = self.board.level.level_name
                self.initialize_level(next_level)
                self.game_state = PLAYING

        elif self.menu_button.is_clicked(mouse_pos):
            self._clear_ai_run(clear_algorithm=True)
            self.game_state = MAIN_MENU

    def draw_level_complete(self):
        self.menu_button.text = "MENU"
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 8, 14, 230))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_WIDTH // 2 - 320, 62, 640, 600)
        self._draw_panel(panel, fill=(18, 37, 42), border=SUCCESS, alpha=252, radius=30)

        pygame.draw.line(self.screen, self._shade(SUCCESS, 1.15), (panel.x + 32, panel.y + 96), (panel.right - 32, panel.y + 96), 2)

        self._draw_text("LEVEL COMPLETE", 58, SUCCESS, center=(SCREEN_WIDTH // 2, 138))
        self._draw_text(f"Level {self.current_level.replace('LEVEL', '')}", 30, TEXT_PRIMARY, center=(SCREEN_WIDTH // 2, 188))

        move_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 220, 240, 80)
        pygame.draw.rect(self.screen, PANEL_LIGHT, move_rect, border_radius=20)
        pygame.draw.rect(self.screen, BORDER, move_rect, 2, border_radius=20)
        self._draw_text("MOVES", 20, TEXT_MUTED, center=(SCREEN_WIDTH // 2, 242))
        self._draw_text(str(self.move_count), 44, WHITE, center=(SCREEN_WIDTH // 2, 278))

        button_y = 560
        if self.game_state == AI_LEVEL_COMPLETE and self.search_result is not None and self.search_result_level == self.current_level:
            self._draw_search_metrics(x=SCREEN_WIDTH // 2 - 245, y=326, width=490, compact=True)
            button_y = 560
        else:
            button_y = 350

        self.next_level_button.rect = pygame.Rect(SCREEN_WIDTH // 2 - 245, button_y, 220, 58)
        self.menu_button.rect = pygame.Rect(SCREEN_WIDTH // 2 + 25, button_y, 220, 58)
        self.next_level_button.draw(self.screen)
        self.menu_button.draw(self.screen)

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
        self._draw_background()
        self._draw_header(
            "SELECT PLAY MODE",
            (
                "Play manually or let a search "
                "algorithm solve the puzzle."
            ),
        )

        card_width = 360
        card_height = 400
        gap = 100
        total_width = (
            card_width * 2 + gap
        )
        start_x = (
            SCREEN_WIDTH - total_width
        ) // 2
        card_y = 150

        human_rect = pygame.Rect(
            start_x,
            card_y,
            card_width,
            card_height,
        )
        ai_rect = pygame.Rect(
            human_rect.right + gap,
            card_y,
            card_width,
            card_height,
        )

        self._draw_panel(human_rect)
        self._draw_panel(ai_rect)

        self.human_button.rect = pygame.Rect(
            human_rect.centerx - 105,
            455,
            210,
            56,
        )
        self.ai_button.rect = pygame.Rect(
            ai_rect.centerx - 105,
            455,
            210,
            56,
        )

        self._draw_cube_logo(
            human_rect.centerx,
            250,
            90,
        )
        self._draw_text(
            "HUMAN PLAY",
            38,
            TEXT_PRIMARY,
            center=(
                human_rect.centerx,
                345,
            ),
        )
        self._draw_text(
            "Solve levels yourself using",
            22,
            TEXT_MUTED,
            center=(
                human_rect.centerx,
                388,
            ),
        )
        self._draw_text(
            "keyboard controls.",
            22,
            TEXT_MUTED,
            center=(
                human_rect.centerx,
                414,
            ),
        )

        self._draw_text(
            "AI",
            72,
            ACCENT,
            center=(
                ai_rect.centerx,
                238,
            ),
        )
        self._draw_text(
            "SEARCH SOLVER",
            38,
            TEXT_PRIMARY,
            center=(
                ai_rect.centerx,
                345,
            ),
        )
        self._draw_text(
            "Visualize BFS, DFS, UCS, A*",
            22,
            TEXT_MUTED,
            center=(
                ai_rect.centerx,
                388,
            ),
        )
        self._draw_text(
            "and more.",
            22,
            TEXT_MUTED,
            center=(
                ai_rect.centerx,
                414,
            ),
        )

        self.human_button.draw(self.screen)
        self.ai_button.draw(self.screen)
        self.back_button.draw(self.screen)

    def handle_algorithms(self, mouse_pos):
        """
        Handle one algorithm-selection click or run the comparison.
        """
        self.back_button.update(mouse_pos)
        self.run_all_button.update(mouse_pos)

        if self.back_button.is_clicked(mouse_pos):
            self.game_state = AI_OR_HUMAN
            return

        if self.run_all_button.is_clicked(mouse_pos):
            self.run_all_comparison()
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
        self._draw_background()
        level_number = (
            self.level_name.replace("LEVEL", "")
            if self.level_name
            else "-"
        )
        self._draw_header(
            "SEARCH ALGORITHMS",
            f"Selected level: {level_number} · Choose one solver or compare all required algorithms.",
        )

        left_panel = pygame.Rect(
            135,
            120,
            590,
            380,
        )
        right_panel = pygame.Rect(
            755,
            150,
            300,
            300,
        )

        self._draw_panel(left_panel)
        self._draw_panel(
            right_panel,
            fill=(35, 47, 60),
            border=WARNING,
        )

        self._draw_text(
            "INDIVIDUAL SOLVERS",
            28,
            TEXT_MUTED,
            topleft=(175, 140),
        )

        for button in self.algorithm_buttons:
            button.draw(self.screen)

        self._draw_text(
            "COMPARE",
            30,
            WARNING,
            center=(905, 190),
        )
        self._draw_text(
            "BFS · DFS · UCS · A*",
            25,
            TEXT_PRIMARY,
            center=(905, 340),
        )
        self._draw_text(
            "Exports results to CSV",
            22,
            TEXT_MUTED,
            center=(905, 375),
        )

        self.run_all_button.draw(self.screen)
        self.back_button.draw(self.screen)

    def run_all_comparison(self):
        """
        Run BFS, DFS, UCS and A* on fresh copies of the selected level.
        """
        self._clear_ai_run(clear_algorithm=True)
        self.comparison_level = self.level_name
        self.comparison_results = []
        self.comparison_csv_path = None
        self.comparison_status = "Preparing comparison..."
        self.game_state = COMPARISON

        self.draw()
        pygame.display.flip()
        pygame.event.pump()

        def update_progress(algorithm_name, index, total):
            self.comparison_status = (
                f"Running {algorithm_name} ({index}/{total})..."
            )
            self.draw()
            pygame.display.flip()
            pygame.event.pump()

        self.comparison_results = run_comparison(
            self.comparison_level,
            progress_callback=update_progress,
        )

        self.comparison_csv_path = save_comparison_csv(
            self.comparison_results,
            self.comparison_level,
        )

        self.comparison_status = "Comparison completed."

    def handle_comparison(self, mouse_pos):
        self.comparison_back_button.update(mouse_pos)
        self.comparison_replay_button.update(mouse_pos)

        if self.comparison_back_button.is_clicked(mouse_pos):
            self.game_state = ALGORITHMS
            return

        if self.comparison_replay_button.is_clicked(mouse_pos):
            replay_result = select_replay_result(
                self.comparison_results,
                preferred_algorithm="A*",
            )

            if replay_result is None:
                return

            replay_level = self.comparison_level
            self.initialize_level(
                replay_level,
                AI=False,
            )

            self.search_result = replay_result
            self.search_result_level = replay_level
            self.solution = deque(replay_result.actions)
            self.algorithm = replay_result.algorithm.lower()
            self.algorithm_completed = True
            self.game_state = AI_PLAYING

    def draw_comparison(self):
        self._draw_background()
        self._draw_header(
            "ALGORITHM COMPARISON",
            "Compare time, memory, explored states and solution quality.",
        )

        info_rect = pygame.Rect(
            35,
            92,
            1030,
            72,
        )
        self._draw_panel(
            info_rect,
            fill=PANEL_ALT,
            border=BORDER,
            alpha=245,
            radius=16,
        )

        level_label = (
            self.comparison_level
            if self.comparison_level
            else "-"
        )
        self._draw_status_chip(
            f"LEVEL {level_label.replace('LEVEL', '')}",
            58,
            112,
            ACCENT,
        )
        self._draw_text(
            self.comparison_status,
            25,
            TEXT_PRIMARY,
            topleft=(220, 118),
        )

        table_rect = pygame.Rect(
            35,
            185,
            1030,
            390,
        )
        self._draw_panel(
            table_rect,
            fill=(16, 27, 45),
            border=BORDER,
            alpha=248,
            radius=20,
        )

        columns = [
            ("ALGORITHM", 65),
            ("TIME (ms)", 215),
            ("MEMORY", 365),
            ("EXPANDED", 510),
            ("LENGTH", 665),
            ("COST", 785),
            ("STATUS", 900),
        ]

        header_y = 215
        pygame.draw.rect(
            self.screen,
            PANEL_LIGHT,
            (53, 202, 994, 48),
            border_radius=12,
        )

        for label, x in columns:
            self._draw_text(
                label,
                21,
                TEXT_MUTED,
                topleft=(x, header_y),
            )

        for row_index, entry in enumerate(
            self.comparison_results
        ):
            y = 270 + row_index * 67
            row_rect = pygame.Rect(
                53,
                y - 8,
                994,
                54,
            )

            pygame.draw.rect(
                self.screen,
                (
                    PANEL_ALT
                    if row_index % 2 == 0
                    else PANEL
                ),
                row_rect,
                border_radius=12,
            )

            result = entry.result
            if result is None:
                values = [
                    entry.algorithm,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    "ERROR",
                ]
            else:
                values = [
                    result.algorithm,
                    f"{result.search_time_ms:.3f}",
                    f"{result.peak_memory_mb:.4f}",
                    str(result.expanded_nodes),
                    str(result.solution_length),
                    (
                        f"{result.total_cost:g}"
                        if result.solved
                        else "-"
                    ),
                    (
                        "SOLVED"
                        if result.solved
                        else "NO PATH"
                    ),
                ]

            for value, (_, x) in zip(
                values,
                columns,
            ):
                color = (
                    DANGER
                    if value in {"ERROR", "NO PATH"}
                    else (
                        SUCCESS
                        if value == "SOLVED"
                        else TEXT_PRIMARY
                    )
                )
                self._draw_text(
                    value,
                    23,
                    color,
                    topleft=(x, y + 5),
                )

            if entry.error:
                self._draw_text(
                    entry.error[:90],
                    18,
                    DANGER,
                    topleft=(215, y + 31),
                )

        if self.comparison_csv_path is not None:
            self._draw_text(
                f"CSV saved: {self.comparison_csv_path}",
                20,
                TEXT_MUTED,
                topleft=(55, 588),
            )

        if self.comparison_results:
            self.comparison_replay_button.draw(
                self.screen
            )

        self.comparison_back_button.draw(self.screen)

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

    def _draw_search_metrics(
        self,
        x=None,
        y=None,
        width=210,
        compact=False,
    ):
        if self.search_result is None:
            return

        if x is None:
            x = SIDEBAR_X + 10
        if y is None:
            y = 355

        height = 204 if compact else 220
        rect = pygame.Rect(x, y, width, height)
        self._draw_panel(rect, fill=(10, 22, 38), border=ACCENT, alpha=248, radius=18)

        self._draw_text("SEARCH RESULT", 26, ACCENT, topleft=(x + 16, y + 14))

        result = self.search_result
        status = "SOLVED" if result.solved else "NO SOLUTION"
        entries = [
            ("Algorithm", result.algorithm),
            ("Time", f"{result.search_time_ms:.3f} ms"),
            ("Memory", f"{result.peak_memory_mb:.4f} MB"),
            ("Expanded", str(result.expanded_nodes)),
            ("Length", str(result.solution_length)),
            ("Cost", f"{result.total_cost:g}"),
        ]

        if compact:
            left_x = x + 22
            right_x = x + width // 2 + 12
            for index, (label, value) in enumerate(entries):
                column_x = left_x if index < 3 else right_x
                row_index = index if index < 3 else index - 3
                row_y = y + 54 + row_index * 35
                self._draw_text(label, 18, TEXT_MUTED, topleft=(column_x, row_y))
                self._draw_text(value, 22, TEXT_PRIMARY, topleft=(column_x, row_y + 16))
        else:
            for index, (label, value) in enumerate(entries):
                row_y = y + 50 + index * 25
                self._draw_text(label, 19, TEXT_MUTED, topleft=(x + 14, row_y))
                self._draw_text(value, 20, TEXT_PRIMARY, topleft=(x + 92, row_y))

        chip_color = SUCCESS if result.solved else DANGER
        self._draw_status_chip(status, x + 16, y + height - 38, chip_color)

    def _draw_state_blocks(self, depth=None):
        if self.current_state is None:
            return

        # Split mode: two independent 1x1x1 cubes.
        if self.current_state.is_split:
            for index, (
                row,
                column,
            ) in enumerate(
                self.current_state.positions
            ):
                active = (
                    index
                    == self.current_state.active_cube
                )
                self._draw_iso_cube(
                    row,
                    column,
                    ISO_CUBE_HEIGHT,
                    active=active,
                    split=True,
                    label=(
                        index + 1
                        if active
                        else None
                    ),
                )
            return

        # Upright mode: one 1x1 base with the height of two unit cubes.
        if (
            self.current_state.orientation
            == "upright"
        ):
            row, column = (
                self.current_state.positions[0]
            )
            self._draw_iso_cube(
                row,
                column,
                ISO_UPRIGHT_HEIGHT,
                active=False,
                split=False,
            )
            return

        # Horizontal / vertical mode: one 2x1x1 rectangle made from
        # two equal 1x1x1 units.
        self._draw_iso_block_span(
            self.current_state.positions
        )

    def draw_level(self):
        self._draw_background()
        self._draw_header(
            "BLOXORZ AI LAB",
            (
                "AI solution replay · large isometric view"
                if self.game_state in {
                    AI_PLAYING,
                    AI_LEVEL_COMPLETE,
                }
                else "Manual puzzle mode · large isometric view"
            ),
        )

        board_rect = pygame.Rect(
            12,
            HEADER_HEIGHT + 8,
            GAME_AREA_WIDTH - 20,
            SCREEN_HEIGHT - HEADER_HEIGHT - 20,
        )
        self._draw_panel(
            board_rect,
            fill=(8, 17, 30),
            border=(43, 67, 99),
            alpha=242,
            radius=22,
        )

        layout = self.board.level.layout
        max_depth = (
            self.board.level.height
            + self.board.level.width
            - 2
        )

        # Draw all tiles first; draw the solid block last.
        for depth in range(max_depth + 1):
            diagonal_cells = []

            for row in range(
                self.board.level.height
            ):
                column = depth - row
                if (
                    0 <= column
                    < self.board.level.width
                ):
                    diagonal_cells.append(
                        (row, column)
                    )

            diagonal_cells.sort(
                key=lambda position: position[0],
                reverse=True,
            )

            for row, column in diagonal_cells:
                self._draw_iso_tile(
                    row,
                    column,
                    layout[row][column],
                )

        self._draw_state_blocks(depth=None)
        self._draw_game_sidebar()

        if self.game_state in {
            PLAYING,
            AI_PLAYING,
        }:
            if self.game_state == AI_PLAYING:
                self.pause_button.draw(
                    self.screen
                )

            self.restart_button.draw(
                self.screen
            )
            self.menu_button.draw(
                self.screen
            )

        if (
            self.game_state == AI_PLAYING
            and not self.ai_paused
            and self.solution
        ):
            now = pygame.time.get_ticks()

            if (
                now - self.last_ai_step_at
                >= self.ai_step_interval
            ):
                action = self.solution.popleft()
                self.apply_game_action(action)
                self.last_ai_step_at = now

        elif (
            self.game_state == AI_PLAYING
            and self.solution is not None
            and not self.solution
        ):
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