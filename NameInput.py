
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

class NameInput:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.input_text = ""
        self.max_length = 20

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                char = event.unicode
                if char.isprintable() and len(self.input_text) < self.max_length:
                    self.input_text += char
        return False

    def get_name(self):
        return self.input_text if self.input_text.strip() else "Anonim"

    def draw(self):
        self.screen.fill(WHITE)
        prompt = self.font.render("Podaj swój nick (Enter = OK):", True, BLACK)
        self.screen.blit(prompt, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))
        pygame.draw.rect(self.screen, GRAY, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 40), 2)
        text_surface = self.font.render(self.input_text, True, BLACK)
        self.screen.blit(text_surface, (WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT // 2 + 5))
        pygame.display.flip()
