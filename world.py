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

    def process_data(self):
        #looks for the relavent data needed
        for layer in self.level_data["layers"]: 
            if layer["name"] == "Stone background":
                self.tile_map = layer["data"]
                
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    # Grab the object's base x and y coordinates
                    x_offset = obj.get("x")
                    y_offset = obj.get("y")
                    # Pass the offsets into process_waypoints
                    self.process_waypoints(waypoint_data, x_offset, y_offset)
                    
    def process_waypoints(self, data, x_offset, y_offset):
        #iterate through waypoints to find individual sets of x/y coords
        for point in data:
            # Add the base offset to each point's relative coordinates
            temp_x = point.get("x") + x_offset
            temp_y = point.get("y") + y_offset
            self.waypoints.append((temp_x, temp_y))

    def process_enemies(self):
        
        if ENEMY_SPAWN_DATA[0] == 0:
            game_outcome = 1
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for enemy in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        #now randomize the list to shuffle the enemies
        random.shuffle(self.enemy_list)

    def check_level_complete(self):
        if (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
            return True

    def reset_level(self):
        #reset enemy variables
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0
        
    def draw(self, surface):
        surface.blit(self.image, (0,0))