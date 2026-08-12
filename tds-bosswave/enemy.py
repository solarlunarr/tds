import pygame as pg
from pygame.math import Vector2
import math
from enemy_data import ENEMY_DATA
import Constants as c

class Enemy(pg.sprite.Sprite):
  def __init__(self, enemy_type, waypoints, images):
    pg.sprite.Sprite.__init__(self)
    data = ENEMY_DATA.get(enemy_type)
    self.enemy_type = enemy_type
    self.waypoints = waypoints
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
    self.rotate()
    self.regenerate(world)
    self.check_alive(world)

  def take_damage(self, amount):
    #armor reduces incoming damage - a lightly-armored boss laughs off weak turrets
    reduced = amount * (1 - self.armor)
    self.health -= reduced

  def regenerate(self, world):
    if self.regen > 0 and self.health < self.max_health:
      self.health = min(self.max_health, self.health + (self.regen * world.game_speed))

  def draw_health_bar(self, surface):
    #floating health bar - mainly useful for tanky enemies like the boss
    bar_width = 60
    bar_height = 8
    fill_pct = max(0, self.health / self.max_health)
    x = self.rect.centerx - bar_width // 2
    y = self.rect.top - 16
    pg.draw.rect(surface, (60, 0, 0), (x, y, bar_width, bar_height))
    pg.draw.rect(surface, (200, 30, 30), (x, y, int(bar_width * fill_pct), bar_height))
    pg.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 1)

  def move(self, world):
    #define a target waypoint
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      #enemy has reached the end of the path
      self.kill()
      world.health -= self.base_damage
      world.missed_enemies +=1

    #calculate distance to target
    dist = self.movement.length()
    #check if remaining distance is greater than the enemy speed
    if dist >= (self.speed * world.game_speed):
      self.pos += self.movement.normalize() * (self.speed * world.game_speed)
    else:
      if dist != 0:
        self.pos += self.movement.normalize() * dist
      self.target_waypoint += 1

  def rotate(self):
    #calculate distance to next waypoint
    dist = self.target - self.pos
    #use distance to calculate angle
    self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
    #rotate image and update rectangle
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def check_alive(self, world):
    if self.health <= 0:
      world.killed_enemies +=1
      world.money += self.reward
      self.kill()
