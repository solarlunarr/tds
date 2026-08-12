import pygame as pg
import Constants as c
import math
from turret_data import TURRET_DATA
from bullet import Bullet

class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage", 10)
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None
        self.original_image = pg.image.load("tds/assets/IceTurret.png")
        
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE

        self.angle = 90
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        self.rebuild_range_circle()

    def rebuild_range_circle(self):
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def apply_item(self, item):
        """Upgrades this existing turret directly."""
        if item.op_type == '+':
            self.damage += item.value
        elif item.op_type == 'x':
            self.damage = int(self.damage * item.value)
        elif item.op_type == '^':
            self.damage = int(round(self.damage ** item.value))
        elif item.op_type == '/':
            self.cooldown = max(100, int(self.cooldown * item.value))
        elif item.op_type == '-':
            self.cooldown = max(100, self.cooldown - int(item.value * 20))
        elif item.op_type == 'GOLD':
            # Golden Ball: Reduces turret cooldown directly by 25%
            self.cooldown = max(100, int(self.cooldown * item.value))
            
        print(f"Turret Upgraded! New Damage: {self.damage}, Cooldown: {self.cooldown}ms")

    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

    def update(self, enemy_group, world, bullet_image, bullet_group):
        if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
            self.pick_target(enemy_group, bullet_image, bullet_group)

    def pick_target(self, enemy_group, bullet_image, bullet_group):
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    
                    new_bullet = Bullet(bullet_image, self.x, self.y, self.target.pos, self.damage)
                    bullet_group.add(new_bullet)
                    
                    self.last_shot = pg.time.get_ticks()
                    break

    def upgrade(self):
        if self.upgrade_level < len(TURRET_DATA):
            self.upgrade_level += 1
            data = TURRET_DATA[self.upgrade_level - 1]
            self.range = data.get("range", self.range)
            self.cooldown = data.get("cooldown", self.cooldown)
            self.damage = data.get("damage", self.damage)
            self.rebuild_range_circle()