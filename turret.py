import pygame as pg
import Constants as c
import math
from turret_data import TURRET_DATA
from bullet import Bullet

class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        
        # Stat initialization from TURRET_DATA
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range", 150)
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown", 1500)
        self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage", getattr(c, "DAMAGE", 10))
        
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None

        self.original_image = pg.image.load("tds/assets/IceTurret.png").convert_alpha()
        
        # Position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE

        # Rotation and Rect setup
        self.angle = 90
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # Create range circle indicator
        self.rebuild_range_circle()

    def rebuild_range_circle(self):
        """Creates or updates the range circle overlay."""
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def apply_math(self, operator):
        if operator == '+':
            self.damage += 5
        elif operator == '-':
            # Reduces cooldown delay (attacks faster)
            self.cooldown = max(100, self.cooldown - 200) 
        elif operator == 'x':
            self.damage = int(self.damage * 1.5)
        elif operator == '/':
            self.cooldown = max(100, int(self.cooldown * 0.7)) # 30% faster fire rate
        elif operator == '^':
            self.damage = self.damage ** 2
        print(f"Turret Upgraded! Damage: {self.damage}, Cooldown: {self.cooldown}ms")

    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

    def update(self, enemy_group, bullet_group, bullet_image):
        if pg.time.get_ticks() - self.last_shot > self.cooldown:
            self.pick_target(enemy_group, bullet_group, bullet_image)

    def pick_target(self, enemy_group, bullet_group, bullet_image):
        for enemy in enemy_group:
            if enemy.health > 0:
                # Safely retrieve position
                if hasattr(enemy, 'pos'):
                    enemy_x, enemy_y = enemy.pos[0], enemy.pos[1]
                else:
                    enemy_x, enemy_y = enemy.rect.centerx, enemy.rect.centery

                x_dist = enemy_x - self.x
                y_dist = enemy_y - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    
                    # Spawn bullet projectile
                    new_bullet = Bullet(bullet_image, self.x, self.y, self.target, self.damage)
                    bullet_group.add(new_bullet)
                    
                    self.last_shot = pg.time.get_ticks()
                    break

    def upgrade(self):
        # Prevent upgrading beyond max level in TURRET_DATA
        if self.upgrade_level < len(TURRET_DATA):
            self.upgrade_level += 1
            data = TURRET_DATA[self.upgrade_level - 1]

            self.range = data.get("range", self.range)
            self.cooldown = data.get("cooldown", self.cooldown)
            self.damage = data.get("damage", self.damage)

            # Redraw range circle to match new range
            self.rebuild_range_circle()