
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background

CAR_COLORS = [
    (220, 20, 60),
    (34, 139, 34),
    (30, 144, 255),
    (255, 140, 0),
    (138, 43, 226),
    (0, 191, 255),
    (220, 220, 220),
    (139, 69, 19),
]
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


class Car:
    def __init__(self, x, y, speed, lane_height):
        self.x = x
        self.y = y
        self.speed = speed
        self.original_speed = speed
        self.color = random.choice(CAR_COLORS)

        self.height = max(int(lane_height * 0.7), 20)
        self.width = max(int(self.height * random.uniform(1.5, 2.2)), 30)

        self.z = True
        self.stopped = False

        self.body_color = self.color
        self.window_color = (50, 50, 80)
        self.wheel_color = BLACK
        self.light_color = (255, 255, 200) if random.choice([True, False]) else (255, 100, 100)

    def update(self):
        if not self.stopped:
            self.x += self.speed

    def stop(self):
        self.stopped = True
        self.speed = 0

    def draw(self, screen):
        car_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        draw_shadow(screen, car_rect, 4, 120)

        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.body_color, body_rect, border_radius=3)

        highlight_color = tuple(min(255, c + 40) for c in self.body_color)
        highlight_rect = pygame.Rect(self.x, self.y, self.width, self.height // 3)
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=3)

        window_width = self.width * 0.6
        window_height = self.height * 0.4
        window_x = self.x + (self.width - window_width) // 2
        window_y = self.y + self.height * 0.15

        front_window = pygame.Rect(window_x + window_width * 0.6, window_y,
                                   window_width * 0.35, window_height)
        pygame.draw.rect(screen, self.window_color, front_window, border_radius=2)

        back_window = pygame.Rect(window_x, window_y,
                                  window_width * 0.35, window_height)
        pygame.draw.rect(screen, self.window_color, back_window, border_radius=2)

        wheel_radius = self.height // 6
        wheel_y = self.y + self.height - wheel_radius

        back_wheel_x = self.x + self.width * 0.2
        pygame.draw.circle(screen, self.wheel_color,
                           (int(back_wheel_x), int(wheel_y)), wheel_radius)
        pygame.draw.circle(screen, GRAY,
                           (int(back_wheel_x), int(wheel_y)), wheel_radius // 2)

        front_wheel_x = self.x + self.width * 0.8
        pygame.draw.circle(screen, self.wheel_color,
                           (int(front_wheel_x), int(wheel_y)), wheel_radius)
        pygame.draw.circle(screen, GRAY,
                           (int(front_wheel_x), int(wheel_y)), wheel_radius // 2)

        front_light = pygame.Rect(self.x + self.width - 3, self.y + self.height * 0.3,
                                  3, self.height * 0.2)
        pygame.draw.rect(screen, self.light_color, front_light)

        back_light = pygame.Rect(self.x, self.y + self.height * 0.3,
                                 3, self.height * 0.2)
        pygame.draw.rect(screen, RED, back_light)

        pygame.draw.rect(screen, BLACK, body_rect, 2, border_radius=3)