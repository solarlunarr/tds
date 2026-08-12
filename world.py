# world.py
import pygame as pg
import random
import Constants as c
from enemy_data import ENEMY_SPAWN_DATA

class World():
    def __init__(self, data, map_image):
        self.level = 1
        self.game_speed = 1
        self.health = c.HEALTH
        self.money = c.MONEY
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        self.boss_incoming = False

    def process_data(self):
        for layer in self.level_data["layers"]: 
            if layer["name"] == "Stone background":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    x_offset = obj.get("x")
                    y_offset = obj.get("y")
                    self.process_waypoints(waypoint_data, x_offset, y_offset)
                    
    def process_waypoints(self, data, x_offset, y_offset):
        for point in data:
            temp_x = point.get("x") + x_offset
            temp_y = point.get("y") + y_offset
            self.waypoints.append((temp_x, temp_y))

    def process_enemies(self):
        if self.level > len(ENEMY_SPAWN_DATA):
            return

        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        boss_count = enemies.get("boss", 0)
        self.boss_incoming = boss_count > 0

        for enemy_type in enemies:
            if enemy_type == "boss":
                continue
            enemies_to_spawn = enemies[enemy_type]
            for _ in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)

        random.shuffle(self.enemy_list)

        # Boss spawns last after all escort enemies
        for _ in range(boss_count):
            self.enemy_list.append("boss")

    def check_level_complete(self):
        if len(self.enemy_list) > 0 and (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
            return True

    def reset_level(self):
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        self.boss_incoming = False
        
    def draw(self, surface):
        surface.blit(self.image, (0, 0))