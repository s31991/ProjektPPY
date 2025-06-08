
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background


WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
SKIN_COLOR = (255, 220, 177)
SHIRT_COLOR = (255, 100, 0)
PANTS_COLOR = (220, 220, 220)
SHOE_COLOR = (139, 69, 19)
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

class Pedestrian:
    def __init__(self, x, y, target_lane, lane_height, road_y_start):
        self.lane_height = lane_height
        self.x = x
        self.y = y
        self.target_lane = target_lane
        self.road_y_start = road_y_start
        self.speed = 2
        self.reached_target = False
        self.target_x = WINDOW_WIDTH - 100
        self.target_y = road_y_start + target_lane * lane_height + lane_height // 2

        self.body_height = max(int(lane_height * 0.6), 25)
        self.body_width = self.body_height // 3
        self.head_radius = self.body_width // 2

        self.walk_cycle = 0
        self.leg_offset = 0

    def update(self, keys_pressed):
        if not self.reached_target:
            moved = False
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.x -= self.speed
                moved = True
            if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.x += self.speed
                moved = True
            if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                self.y -= self.speed
                moved = True
            if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                self.y += self.speed
                moved = True

            if moved:
                self.walk_cycle += 0.3
                self.leg_offset = math.sin(self.walk_cycle) * 3

            self.x = max(self.body_width, min(WINDOW_WIDTH - self.body_width, self.x))
            self.y = max(self.body_height, min(WINDOW_HEIGHT - self.body_height, self.y))

            distance_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
            if distance_to_target < 15:
                self.reached_target = True

    def check_collision(self, cars):
        ped_rect = pygame.Rect(self.x - self.body_width // 2,
                               self.y - self.body_height // 2,
                               self.body_width, self.body_height)
        for car in cars:
            car_rect = pygame.Rect(car.x, car.y, car.width, car.height)
            if ped_rect.colliderect(car_rect):
                return True
        return False

    def draw(self, screen):
        shadow_center = (int(self.x), int(self.y + self.body_height // 2 + 5))
        shadow_surface = pygame.Surface((self.body_width * 2, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 100),
                            (0, 0, self.body_width * 2, 8))
        screen.blit(shadow_surface, (shadow_center[0] - self.body_width, shadow_center[1]))

        head_center = (int(self.x), int(self.y - self.body_height // 2 - self.head_radius))
        pygame.draw.circle(screen, SKIN_COLOR, head_center, self.head_radius)
        pygame.draw.circle(screen, BLACK, head_center, self.head_radius, 2)

        hair_rect = pygame.Rect(head_center[0] - self.head_radius + 2,
                                head_center[1] - self.head_radius,
                                (self.head_radius - 2) * 2, self.head_radius)
        pygame.draw.ellipse(screen, (101, 67, 33), hair_rect)

        eye_y = head_center[1] - 2
        pygame.draw.circle(screen, WHITE, (head_center[0] - 3, eye_y), 2)
        pygame.draw.circle(screen, WHITE, (head_center[0] + 3, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (head_center[0] - 3, eye_y), 1)
        pygame.draw.circle(screen, BLACK, (head_center[0] + 3, eye_y), 1)

        pygame.draw.circle(screen, (200, 150, 120), (head_center[0], head_center[1] + 1), 1)
        pygame.draw.arc(screen, BLACK,
                        (head_center[0] - 3, head_center[1] + 2, 6, 4), 0, math.pi, 1)

        body_rect = pygame.Rect(self.x - self.body_width // 2,
                                self.y - self.body_height // 3,
                                self.body_width, self.body_height // 2)
        pygame.draw.rect(screen, SHIRT_COLOR, body_rect, border_radius=3)
        pygame.draw.rect(screen, BLACK, body_rect, 1, border_radius=3)

        arm_length = self.body_height // 3
        left_arm_end = (int(self.x - self.body_width // 2 - 5),
                        int(self.y - self.body_height // 6))
        right_arm_end = (int(self.x + self.body_width // 2 + 5),
                         int(self.y - self.body_height // 6))

        pygame.draw.line(screen, SKIN_COLOR,
                         (self.x - self.body_width // 2, self.y - self.body_height // 4),
                         left_arm_end, 3)
        pygame.draw.line(screen, SKIN_COLOR,
                         (self.x + self.body_width // 2, self.y - self.body_height // 4),
                         right_arm_end, 3)

        pygame.draw.circle(screen, SKIN_COLOR, left_arm_end, 3)
        pygame.draw.circle(screen, SKIN_COLOR, right_arm_end, 3)

        pants_rect = pygame.Rect(self.x - self.body_width // 2,
                                 self.y + self.body_height // 6,
                                 self.body_width, self.body_height // 3)
        pygame.draw.rect(screen, PANTS_COLOR, pants_rect, border_radius=2)
        pygame.draw.rect(screen, BLACK, pants_rect, 1, border_radius=2)

        leg_start_y = self.y + self.body_height // 2
        leg_length = self.body_height // 3

        left_leg_x = self.x - self.body_width // 4
        left_leg_end = (int(left_leg_x + self.leg_offset), int(leg_start_y + leg_length))
        pygame.draw.line(screen, PANTS_COLOR,
                         (left_leg_x, leg_start_y), left_leg_end, 4)

        right_leg_x = self.x + self.body_width // 4
        right_leg_end = (int(right_leg_x - self.leg_offset), int(leg_start_y + leg_length))
        pygame.draw.line(screen, PANTS_COLOR,
                         (right_leg_x, leg_start_y), right_leg_end, 4)

        pygame.draw.ellipse(screen, SHOE_COLOR,
                            (left_leg_end[0] - 4, left_leg_end[1] - 2, 8, 6))
        pygame.draw.ellipse(screen, SHOE_COLOR,
                            (right_leg_end[0] - 4, right_leg_end[1] - 2, 8, 6))

        if not self.reached_target:
            current_time = time.time()
            pulse = int(10 + 5 * math.sin(current_time * 4))

            pygame.draw.circle(screen, GREEN,
                               (int(self.target_x), int(self.target_y)),
                               15 + pulse, 3)
            pygame.draw.circle(screen, GREEN,
                               (int(self.target_x), int(self.target_y)),
                               8, 2)
            pygame.draw.circle(screen, GREEN,
                               (int(self.target_x), int(self.target_y)),
                               3)
