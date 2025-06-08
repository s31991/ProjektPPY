
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background


from Car import Car
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
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

class Road:
    def __init__(self, road_id, y_start, height):
        self.road_id = road_id
        self.y_start = y_start
        self.height = height
        self.generate_road_params()
        self.lane_height = self.height // self.lanes
        self.cars = []
        self.car_count = 0
        self.last_car_time = 0
        self.stopped_lanes = set()
        self.safety_gap_start = 0
        self.safety_gap_duration = 500

    def generate_road_params(self):
        self.lanes = random.randint(2, 4)
        self.car_speed = random.uniform(1.5, 3.5)
        self.car_spacing = random.randint(150, 300)

    def can_add_car(self, lane):
        lane_y = self.y_start + lane * self.lane_height + (self.lane_height - 15) // 2
        for car in self.cars:
            if abs(car.y - lane_y) < 20 and car.x < 200:  # Увеличен радиус проверки
                return False
        return True

    def is_safety_gap_active(self):
        current_time = time.time() * 1000
        return (current_time - self.safety_gap_start) < self.safety_gap_duration

    def trigger_safety_gap(self):
        self.safety_gap_start = time.time() * 1000

    def add_car(self):
        current_time = time.time() * 1000
        if self.is_safety_gap_active():
            return
        if current_time - self.last_car_time > self.car_spacing:
            attempts = 0
            max_attempts = 10
            while attempts < max_attempts:
                lane = random.randint(0, self.lanes - 1)
                if lane in self.stopped_lanes:
                    attempts += 1
                    continue
                if self.can_add_car(lane):
                    car_y = self.y_start + lane * self.lane_height + (
                                self.lane_height - int(self.lane_height * 0.7)) // 2
                    new_car = Car(-80, car_y, self.car_speed, self.lane_height)
                    self.cars.append(new_car)
                    self.last_car_time = current_time
                    self.trigger_safety_gap()
                    break
                attempts += 1

    def stop_lane(self, lane_number):
        self.stopped_lanes.add(lane_number)
        lane_center_y = self.y_start + lane_number * self.lane_height + self.lane_height // 2
        for car in self.cars:
            car_center_y = car.y + car.height // 2
            if abs(car_center_y - lane_center_y) < self.lane_height // 2:
                car.stop()

    def update(self):
        self.add_car()
        for car in self.cars[:]:
            car.update()
            if car.x + car.width >= 0 and car.x - car.original_speed < 0 and car.z:
                self.car_count += 1
                car.z = False
            if car.x > WINDOW_WIDTH:
                self.cars.remove(car)

    def draw(self, screen):
        road_surface = create_gradient_surface(WINDOW_WIDTH, self.height, (40, 40, 40), (60, 60, 60))
        screen.blit(road_surface, (0, self.y_start))

        shadow_rect = pygame.Rect(0, self.y_start, WINDOW_WIDTH, self.height)
        draw_shadow(screen, shadow_rect, 3, 80)

        for i in range(1, self.lanes):
            y = self.y_start + i * self.lane_height
            for x in range(0, WINDOW_WIDTH, 60):
                line_rect = pygame.Rect(x, y - 3, 30, 6)
                pygame.draw.rect(screen, YELLOW, line_rect)
                draw_shadow(screen, line_rect, 1, 60)

        current_time = time.time()
        for lane in self.stopped_lanes:
            lane_y = self.y_start + lane * self.lane_height
            alpha = int(50 + 30 * math.sin(current_time * 3))
            stopped_surface = pygame.Surface((WINDOW_WIDTH, self.lane_height), pygame.SRCALPHA)
            pygame.draw.rect(stopped_surface, (255, 100, 100, alpha),
                             (0, 0, WINDOW_WIDTH, self.lane_height))
            screen.blit(stopped_surface, (0, lane_y))

        for i in range(3):
            color_intensity = 255 - i * 50
            pygame.draw.line(screen, (color_intensity, 0, 0),
                             (i, self.y_start), (i, self.y_start + self.height), 1)

        for car in self.cars:
            car.draw(screen)

    def get_info_text(self):
        return f"Droga {self.road_id}: {self.lanes} pas(y/ów), prędkość: {self.car_speed:.1f}, odstęp: {self.car_spacing}ms"
