
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime

from LeaderboardScreen import LeaderboardScreen
from NameInput import NameInput
from Pedestrian import Pedestrian
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background
from Database import Database
from Road import Road

pygame.init()

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

SKIN_COLOR = (255, 220, 177)
SHIRT_COLOR = (255, 100, 0)
PANTS_COLOR = (220, 220, 220)
SHOE_COLOR = (139, 69, 19)

GAME_STATE_MENU = 0
GAME_STATE_STAGE1 = 1
GAME_STATE_STAGE2 = 2
GAME_STATE_ENTER_NAME = 3
GAME_STATE_RESULTS = 4
GAME_STATE_LEADERBOARD = 5
GAME_STATE_STAGE1_RESULT = 6

DB_FILE = 'game_scores.db'




class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Gra Drogowa z Leaderboard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 48)
        self.stage1_over = False
        self.stage1_active = True
        self.db = Database()
        self.leaderboard_screen = LeaderboardScreen(self.screen, self.font, self.db)

        self.reset_game()

    def reset_game(self):
        self.game_state = GAME_STATE_STAGE1
        self.stage1_over = False
        self.stage1_active = True
        self.start_time_stage1 = time.time()
        self.selected_road = 0
        self.roads = [Road(i + 1, 100 + i * 160, 140) for i in range(4)]
        self.stage1_done = False
        self.stage1_correct = False
        self.stage1_end_time = None

        self.stage2_done = False
        self.stage2_success = False
        self.stage2_start_time = None
        self.stage2_end_time = None

        self.pedestrians = []
        self.current_ped = 0

        self.name_input = NameInput(self.screen, self.font)
        self.total_score = 0

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        self.db.close()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:

                if self.game_state == GAME_STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.game_state = GAME_STATE_LEADERBOARD
                    elif event.key == pygame.K_r:
                        self.reset_game()

                elif self.game_state == GAME_STATE_STAGE1:
                    if self.stage1_active and not self.stage1_over:
                        if event.key == pygame.K_1:
                            self.finish_stage1(0)
                        elif event.key == pygame.K_2:
                            self.finish_stage1(1)
                        elif event.key == pygame.K_3:
                            self.finish_stage1(2)
                        elif event.key == pygame.K_4:
                            self.finish_stage1(3)
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.game_state = GAME_STATE_LEADERBOARD

                elif self.game_state == GAME_STATE_STAGE2:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.game_state = GAME_STATE_LEADERBOARD

                elif self.game_state == GAME_STATE_STAGE1_RESULT:
                    if event.key == pygame.K_RETURN:
                        self.init_stage2()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.game_state = GAME_STATE_LEADERBOARD

                elif self.game_state == GAME_STATE_ENTER_NAME:
                    if self.name_input.handle_event(event):
                        self.save_score()
                        self.game_state = GAME_STATE_RESULTS

                elif self.game_state == GAME_STATE_RESULTS:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_l:
                        self.game_state = GAME_STATE_LEADERBOARD
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = GAME_STATE_MENU

                elif self.game_state == GAME_STATE_LEADERBOARD:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GAME_STATE_MENU

        return True

    def update(self):
        if self.game_state == GAME_STATE_STAGE1 and not self.stage1_over:
            for road in self.roads:
                road.update()

        elif self.game_state == GAME_STATE_STAGE2 and not self.stage2_done:
            self.road.update()

            if self.current_ped < len(self.pedestrians):
                keys = pygame.key.get_pressed()
                ped = self.pedestrians[self.current_ped]
                ped.update(keys)

                if ped.check_collision(self.road.cars):
                    self.stage2_done = True
                    self.stage2_success = False
                    self.stage2_end_time = time.time() - self.stage2_start_time
                    self.game_state = GAME_STATE_ENTER_NAME
                    return

                if ped.reached_target:
                    self.road.stop_lane(ped.target_lane)
                    self.road.trigger_safety_gap()
                    self.current_ped += 1

                    pygame.time.wait(500)

            if self.current_ped >= len(self.pedestrians):
                self.stage2_done = True
                self.stage2_success = True
                self.stage2_end_time = time.time() - self.stage2_start_time
                self.game_state = GAME_STATE_ENTER_NAME

    def draw(self):
        self.screen.fill(WHITE)

        if self.game_state == GAME_STATE_MENU:
            bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                                 (30, 50, 80), (80, 120, 160))
            self.screen.blit(bg_surface, (0, 0))

            title_pos = (WINDOW_WIDTH // 2 - 100, 150)
            draw_text_with_background(self.screen, "GRA DROGOWA ",
                                      self.big_font, title_pos, WHITE, (0, 0, 0, 200), 15)

            instructions = [
                "ENTER - Rozpocznij grę",
                "L - Tabela wyników",
                "R - Restart"
            ]

            for i, instruction in enumerate(instructions):
                y_pos = 280 + i * 50
                draw_text_with_background(self.screen, instruction, self.font,
                                          (WINDOW_WIDTH // 2 - 120, y_pos),
                                          WHITE, (50, 50, 50, 150), 10)

        elif self.game_state == GAME_STATE_STAGE1:
            bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                                 (40, 60, 80), (80, 100, 120))
            self.screen.blit(bg_surface, (0, 0))

            for road in self.roads:
                road.draw(self.screen)

            if self.stage1_active and not self.stage1_over:
                instructions = [
                    "ETAP 1: Która droga ma największy ruch?",
                    "Naciśnij 1, 2, 3 lub 4 aby wybrać drogę"
                ]

                for i, instruction in enumerate(instructions):
                    draw_text_with_background(self.screen, instruction, self.font,
                                              (50, 20 + i * 35), WHITE, (0, 0, 0, 180), 8)

            controls = ["R - Restart", "L - Tabela wyników"]
            for i, control in enumerate(controls):
                draw_text_with_background(self.screen, control, self.font,
                                          (WINDOW_WIDTH - 200, 20 + i * 30),
                                          WHITE, (100, 0, 0, 150), 5)

        elif self.game_state == GAME_STATE_STAGE2:
            bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                                 (20, 40, 60), (60, 80, 100))
            self.screen.blit(bg_surface, (0, 0))

            self.road.draw(self.screen)
            for i in range(self.current_ped + 1):
                if i < len(self.pedestrians):
                    self.pedestrians[i].draw(self.screen)

            if not self.stage2_done:
                instructions = [
                    f"Pieszy {self.current_ped + 1}/{len(self.pedestrians)}",
                    "Sterowanie: WASD lub strzałki",
                    "Doprowadź pieszego do zielonego celu"
                ]

                for i, instruction in enumerate(instructions):
                    draw_text_with_background(self.screen, instruction, self.font,
                                              (15, 15 + i * 30), WHITE, (0, 0, 0, 180), 5)

            controls = ["R - Restart", "L - Tabela wyników"]
            for i, control in enumerate(controls):
                draw_text_with_background(self.screen, control, self.font,
                                          (WINDOW_WIDTH - 200, 20 + i * 30),
                                          WHITE, (100, 0, 0, 150), 5)

            if self.stage2_done:
                if self.stage2_success:
                    end_text = "GRATULACJE! Wszyscy piesi bezpiecznie przeszli!"
                    end_color = GREEN
                else:
                    end_text = "KOLIZJA! Spróbuj ponownie."
                    end_color = RED

                draw_text_with_background(self.screen, end_text, self.big_font,
                                          (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2),
                                          end_color, (255, 255, 255, 220), 20)

        elif self.game_state == GAME_STATE_STAGE1_RESULT:
            bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                                 (50, 30, 80), (100, 60, 120))
            self.screen.blit(bg_surface, (0, 0))

            title_pos = (WINDOW_WIDTH // 2 - 120, 100)
            draw_text_with_background(self.screen, "ETAP 1 - WYNIK", self.big_font,
                                      title_pos, WHITE, (0, 0, 0, 200), 15)

            if self.stage1_correct:
                result_text = "POPRAWNY WYBÓR!"
                result_color = GREEN
            else:
                result_text = "NIEPOPRAWNY WYBÓR"
                result_color = RED

            result_pos = (WINDOW_WIDTH // 2 - 100, 180)
            draw_text_with_background(self.screen, result_text, self.font,
                                      result_pos, result_color, (255, 255, 255, 180), 10)

            time_text = f"Czas: {self.stage1_end_time:.1f}s"
            time_pos = (WINDOW_WIDTH // 2 - 80, 220)
            draw_text_with_background(self.screen, time_text, self.font,
                                      time_pos, WHITE, (0, 0, 0, 150), 8)

            instructions = [
                "ETAP 2: Przeprowadź pieszych przez drogę",
                "Sterowanie: WASD lub strzałki",
                "Cel: Doprowadź wszystkich pieszych do zielonych celów",
                "Uważaj na samochody!",
                "",
                "ENTER - Rozpocznij Etap 2",
                "R - Restart gry",
                "L - Tabela wyników"
            ]

            for i, instruction in enumerate(instructions):
                if not instruction:
                    continue
                color = WHITE
                if "ENTER" in instruction:
                    color = GREEN
                elif "R -" in instruction or "L -" in instruction:
                    color = YELLOW

                text_pos = (WINDOW_WIDTH // 2 - 200, 280 + i * 35)
                draw_text_with_background(self.screen, instruction, self.font,
                                          text_pos, color, (0, 0, 0, 150), 8)

        elif self.game_state == GAME_STATE_ENTER_NAME:
            self.name_input.draw()

        elif self.game_state == GAME_STATE_RESULTS:

            bg_surface = create_gradient_surface(WINDOW_WIDTH, WINDOW_HEIGHT,
                                                 (30, 50, 30), (60, 100, 60))
            self.screen.blit(bg_surface, (0, 0))

            title_pos = (WINDOW_WIDTH // 2 - 100, 100)
            draw_text_with_background(self.screen, "KOŃCOWY WYNIK", self.big_font,
                                      title_pos, WHITE, (0, 0, 0, 200), 15)

            results = [
                f"Gracz: {self.name_input.get_name()}",
                f"Etap 1: {':)' if self.stage1_correct else ':<'} ({self.stage1_end_time:.1f}s)",
                f"Etap 2: {':)' if self.stage2_success else ':<'} ({self.stage2_end_time:.1f}s)" if self.stage2_end_time else "Etap 2: Nie ukończony",
                f"Piesi uratowani: {sum(p.reached_target for p in self.pedestrians)}/{len(self.pedestrians)}",
                f"Łączny wynik: {self.total_score} punktów"
            ]

            for i, result in enumerate(results):
                result_pos = (WINDOW_WIDTH // 2 - 150, 200 + i * 40)
                draw_text_with_background(self.screen, result, self.font,
                                          result_pos, WHITE, (0, 0, 0, 150), 8)

            instructions = [
                "R - Nowa gra",
                "L - Tabela wyników",
                "ESC - Menu główne"
            ]

            for i, instruction in enumerate(instructions):
                instruction_pos = (WINDOW_WIDTH // 2 - 100, 400 + i * 35)
                draw_text_with_background(self.screen, instruction, self.font,
                                          instruction_pos, YELLOW, (0, 0, 0, 150), 8)

        elif self.game_state == GAME_STATE_LEADERBOARD:
            self.leaderboard_screen.draw()

        pygame.display.flip()

    def init_stage2(self):
        best = self.roads[self.selected_road]

        self.road = Road(best.road_id, 200, 400)
        self.road.lanes = best.lanes
        self.road.car_speed = best.car_speed * 2
        self.road.car_spacing = int(1200)
        self.road.lane_height = self.road.height // self.road.lanes

        self.road.cars = []
        self.road.last_car_time = 0
        self.road.stopped_lanes = set()
        self.road.safety_gap_start = 0

        start_x = 50
        start_y_base = self.road.y_start + self.road.height + 50

        self.pedestrians = []
        for i in range(self.road.lanes):
            ped = Pedestrian(
                start_x,
                start_y_base + i * 60,
                i,
                self.road.lane_height,
                self.road.y_start
            )
            self.pedestrians.append(ped)

        self.stage2_start_time = time.time()
        self.current_ped = 0
        self.stage2_done = False
        self.stage2_success = False
        self.game_state = GAME_STATE_STAGE2

    def calculate_score(self):
        score = 0
        if self.stage1_correct:
            score += 100
            if self.stage1_end_time < 5:
                score += 50
        saved = sum(p.reached_target for p in self.pedestrians)
        score += saved * 200
        if self.stage2_success:
            score += 500
        if self.stage2_success and self.stage2_end_time < 30:
            score += 300
        return score

    def save_score(self):
        name = self.name_input.get_name()
        saved = sum(p.reached_target for p in self.pedestrians)
        total = len(self.pedestrians)
        self.total_score = self.calculate_score()
        self.db.insert_score(name, self.stage1_correct, self.stage1_end_time,
                             self.stage2_success, self.stage2_end_time,
                             saved, total, self.total_score)

    def finish_stage1(self, chosen_index):
        if self.stage1_over:
            return
        self.selected_road = chosen_index
        self.stage1_end_time = time.time() - self.start_time_stage1
        max_index = max(range(4), key=lambda i: self.roads[i].car_count)
        self.stage1_correct = (self.selected_road == max_index)
        self.stage1_over = True
        self.stage1_active = False
        self.game_state = GAME_STATE_STAGE1_RESULT


if __name__ == "__main__":
    game = Game()
    game.run()
