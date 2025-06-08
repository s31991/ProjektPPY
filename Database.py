
import pygame
import random
import time
import sqlite3
import math
from datetime import datetime
from metody import create_gradient_surface
from metody import draw_shadow
from metody import draw_text_with_background

DB_FILE = 'game_scores.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.create_table()

    def create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            stage1_correct BOOLEAN,
            stage1_time REAL,
            stage2_completed BOOLEAN,
            stage2_time REAL,
            pedestrians_saved INTEGER,
            total_pedestrians INTEGER,
            total_score INTEGER,
            date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def insert_score(self, player_name, stage1_correct, stage1_time, stage2_completed,
                     stage2_time, pedestrians_saved, total_pedestrians, total_score):
        self.conn.execute('''INSERT INTO leaderboard (
            player_name, stage1_correct, stage1_time, stage2_completed, stage2_time,
            pedestrians_saved, total_pedestrians, total_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (player_name, stage1_correct, stage1_time, stage2_completed,
                           stage2_time, pedestrians_saved, total_pedestrians, total_score))
        self.conn.commit()

    def get_top_scores(self, limit=10):
        cursor = self.conn.execute('''SELECT player_name, total_score, stage2_completed,
                                      pedestrians_saved, total_pedestrians, date_played
                                      FROM leaderboard ORDER BY total_score DESC LIMIT ?''', (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
