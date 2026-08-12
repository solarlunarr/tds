# enemy.py
import pygame as pg
from pygame.math import Vector2
import math
import random
from enemy_data import ENEMY_DATA
import Constants as c

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images, turret_group=None):
        pg.sprite.Sprite.__init__(self)
        data = ENEMY_DATA.get(enemy_type)
        self.enemy_type = enemy_type
        self.waypoints = waypoints
        self.turret_group = turret_group
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.health = data["health"]
        self.max_health = data["health"]
        self.speed = data["speed"]
        self.armor = data.get("armor", 0)
        self.regen = data.get("regen", 0)
        self.base_damage = data.get("damage", 25)
        self.reward = data.get("reward", c.KILL_REWARD)
        self.angle = 0
        self.original_image = images.get(enemy_type)
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self, world):
        self.move(world)
        if self.alive():
            self.rotate()
            self.regenerate(world)

    def take_damage(self, amount):
        reduced = amount * (1 - self.armor)
        self.health -= reduced

    def regenerate(self, world):
        if self.regen > 0 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + (self.regen * world.game_speed))

    def draw_health_bar(self, surface):
        bar_width = 60
        bar_height = 8
        fill_pct = max(0, self.health / self.max_health)
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 16
        pg.draw.rect(surface, (60, 0, 0), (x, y, bar_width, bar_height))
        pg.draw.rect(surface, (200, 30, 30), (x, y, int(bar_width * fill_pct), bar_height))
        pg.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1)

    def move(self, world):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            self.kill()
            world.health -= self.base_damage
            world.missed_enemies += 1
            return  # Prevent calculation on killed enemy

        dist = self.movement.length()
        if dist >= (self.speed * world.game_speed):
            self.pos += self.movement.normalize() * (self.speed * world.game_speed)
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        dist = self.target - self.pos
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_alive(self, world, inventory=None):
        if self.health <= 0:
            world.killed_enemies += 1
            world.money += self.reward
            
            # 35% Chance to drop an Operation Item on death
            if inventory and random.random() < 0.35:
                from Item import Item
                inventory.add_item(Item(current_level=world.level))
                
            self.kill()