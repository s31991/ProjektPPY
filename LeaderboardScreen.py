
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHT_ORANGE = (255, 200, 100)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

class LeaderboardScreen:
    def __init__(self, screen, font, database):
        self.screen = screen
        self.font = font
        self.database = database
        self.title_font = pygame.font.Font(None, 48)

    def draw(self):
        bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                             (20, 30, 50), (50, 70, 100))
        self.screen.blit(bg_surface, (0, 0))

        title_pos = (WINDOW_WIDTH // 2 - 150, 50)
        draw_text_with_background(self.screen, "TOP 10 WYNIKÓW",
                                  self.title_font, title_pos, WHITE, (0, 0, 0, 200), 15)

        headers = ["Poz.", "Gracz", "Punkty", "Etapy", "Piesi", "Data"]
        header_x_positions = [100, 200, 400, 500, 600, 750]

        for i, header in enumerate(headers):
            draw_text_with_background(self.screen, header, self.font,
                                      (header_x_positions[i], 120),
                                      YELLOW, (0, 0, 0, 150), 5)

        top_scores = self.database.get_top_scores(10)
        for i, score in enumerate(top_scores):
            name, total, stage2_completed, saved, total_peds, date = score
            y_pos = 160 + i * 40

            if i == 0:
                bg_color = (255, 215, 0, 100)
            elif i == 1:
                bg_color = (192, 192, 192, 100)
            elif i == 2:
                bg_color = (205, 127, 50, 100)
            else:
                bg_color = (50, 50, 50, 100)

            position = f"{i + 1}."
            completed_str = "2/2" if stage2_completed else "1/2"
            pedestrians_str = f"{saved}/{total_peds}"
            date_fmt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d.%m")

            data = [position, name[:12], str(total), completed_str, pedestrians_str, date_fmt]

            for j, text in enumerate(data):
                draw_text_with_background(self.screen, text, self.font,
                                          (header_x_positions[j], y_pos),
                                          WHITE, bg_color, 3)

        instruction_pos = (WINDOW_WIDTH // 2 - 150, 650)
        draw_text_with_background(self.screen, "ESC - Powrót do menu",
                                  self.font, instruction_pos, WHITE, (100, 0, 0, 180), 10)

        pygame.display.flip()